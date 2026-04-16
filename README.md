# FastAPI Architecture

A production-ready FastAPI boilerplate with async SQLAlchemy 2.0, Pydantic v2, Alembic migrations, and JWT authentication.

## Tech Stack

| Tool | Version | Purpose |
|---|---|---|
| **FastAPI** | ≥0.135 | Web framework |
| **SQLAlchemy** | ≥2.0 | Async ORM |
| **Alembic** | ≥1.18 | Database migrations |
| **PostgreSQL** | — | Database |
| **psycopg** | ≥3.3 | Async PostgreSQL driver |
| **Pydantic** | v2 | Data validation & settings |
| **pydantic-settings** | ≥2.13 | Environment config |
| **pwdlib[argon2]** | ≥0.3 | Password hashing |
| **PyJWT** | ≥2.12 | JWT token handling |
| **Python** | ≥3.13 | Runtime |

---

## Project Structure

```
fastapi-architecture/
├── main.py                          # App entry point
├── pyproject.toml                   # Dependencies & metadata
├── alembic.ini                      # Alembic configuration
├── .env                             # Environment variables (gitignored)
└── app/
    ├── config/
    │   ├── __init__.py              # Re-exports `settings`
    │   └── base.py                  # Pydantic Settings class
    ├── core/
    │   └── exceptions.py            # Domain exception classes + register_exception_handlers()
    ├── database/
    │   ├── base.py                  # Engine, session, Base, mixins, get_db()
    │   ├── repository.py            # Generic BaseRepository[T]
    │   ├── models/
    │   │   └── user.py              # User ORM model
    │   └── migrations/
    │       ├── env.py               # Alembic runtime config
    │       └── versions/
    │           └── 11e46588a4f8_create_users_table.py
    ├── auth/
    │   ├── router.py                # POST /register, POST /login
    │   ├── service.py               # AuthService
    │   ├── schemas.py               # RegisterSchema, LoginSchema, TokenResponseSchema
    │   ├── utils.py                 # Password hashing, JWT creation/verification
    │   └── dependencies.py          # get_current_user(), CurrentUser type alias
    ├── users/
    │   ├── router.py                # GET /me
    │   ├── service.py               # UserService
    │   ├── schemas.py               # UserCreate, UserUpdate, UserResponse
    │   └── repository.py            # UserRepository
    └── utils/
        └── schemas.py               # CustomBaseModel (camelCase aliases)
```

---

## Getting Started

### 1. Prerequisites

- Python 3.13+
- PostgreSQL running locally

### 2. Install dependencies

```bash
pip install -e .
# or with uv
uv sync
```

### 3. Configure environment

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost/fastapi-architecture

JWT_ACCESS_TOKEN_SECRET=your-access-secret
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15

JWT_REFRESH_TOKEN_SECRET=your-refresh-secret
JWT_REFRESH_TOKEN_EXPIRE_MINUTES=43200
```

### 4. Run migrations

```bash
alembic upgrade head
```

### 5. Start the server

```bash
fastapi dev main.py
```

---

## Architecture

### Request Flow

```
HTTP Request
    │
    ▼
Router (app/*/router.py)
    │  extracts request body / path params
    ▼
Service (app/*/service.py)
    │  business logic, raises domain exceptions (NotFoundException, etc.)
    ▼
Repository (app/*/repository.py)
    │  database queries via SQLAlchemy
    ▼
Database (PostgreSQL)
```

### Dependency Injection

FastAPI's `Depends()` wires everything together. Each layer is injected into the one above it:

```python
# Router injects Service
async def register(
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    register_data: RegisterSchema
): ...

# Service injects Repository
def get_auth_service(
    user_service: Annotated[UserService, Depends(get_user_service)]
): ...

# Repository injects DB session
def get_user_repo(
    db: Annotated[AsyncSession, Depends(get_db)]
): ...
```

---

## SQLAlchemy

### Async Engine & Session

`app/database/base.py` sets up the async database layer:

```python
engine = create_async_engine(settings.database_url)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False   # keeps objects usable after commit
)
```

### Session Dependency

`get_db()` is an async generator used as a FastAPI dependency. It commits on success and rolls back on any exception:

```python
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

### DeclarativeBase & Mixins

All models inherit from `Base` (SQLAlchemy's `DeclarativeBase`) plus reusable mixins:

```python
class Base(DeclarativeBase):
    pass

class IDMixin:
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

### User Model

```python
class User(Base, IDMixin, TimestampMixin):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    email:    Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
```

### Generic Repository Pattern

`BaseRepository[ModelT]` provides typed CRUD operations for any model:

```python
class BaseRepository(Generic[ModelT]):
    async def get_by_id(self, id: int) -> ModelT | None
    async def get_all(self, skip: int = 0, limit: int = 100) -> Sequence[ModelT]
    async def create(self, obj: ModelT) -> ModelT
    async def update(self, obj: ModelT, data: dict) -> ModelT
    async def delete(self, obj: ModelT) -> None
```

Domain repositories extend it with custom queries:

```python
class UserRepository(BaseRepository[User]):
    async def get_by_email(self, email: str) -> User | None
    async def get_by_username(self, username: str) -> User | None
```

---

## Pydantic

### CustomBaseModel

All schemas extend `CustomBaseModel` (`app/utils/schemas.py`), which automatically converts snake_case field names to camelCase in JSON responses:

```python
class CustomBaseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,   # snake_case → camelCase in JSON
        populate_by_name=True,      # also accept original snake_case names
    )
```

### Request Schemas (Input)

```python
class RegisterSchema(CustomBaseModel):
    username: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(max_length=120)
    password: str = Field(min_length=8)

class LoginSchema(CustomBaseModel):
    email: EmailStr = Field(max_length=120)
    password: str = Field(min_length=8)
```

### Response Schemas (Output)

```python
class UserResponse(CustomBaseModel):
    model_config = ConfigDict(from_attributes=True)  # ORM → Pydantic

    id: int
    username: str
    email: str
    created_at: datetime
    updated_at: datetime

class TokenResponseSchema(CustomBaseModel):
    model_config = ConfigDict(from_attributes=True)
    access_token: str
```

`from_attributes=True` enables Pydantic to read directly from SQLAlchemy ORM objects.

### Settings

`app/config/base.py` uses `pydantic-settings` to load and validate environment variables from `.env`:

```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    jwt_access_token_secret: SecretStr    # masked in logs/repr
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_secret: SecretStr
    jwt_refresh_token_expire_minutes: int = 43200  # 30 days
    jwt_algorithm: str = "HS256"
    database_url: str

settings = Settings()
```

`SecretStr` prevents secrets from leaking into logs or error messages.

---

## Alembic Migrations

Alembic manages the database schema. Migrations live in `app/database/migrations/versions/`.

### Common Commands

```bash
# Apply all pending migrations
alembic upgrade head

# Roll back one migration
alembic downgrade -1

# Auto-generate a migration from model changes
alembic revision --autogenerate -m "description"

# View migration history
alembic history

# Check current revision
alembic current
```

### How It Works

`app/database/migrations/env.py` connects Alembic to your SQLAlchemy models:

1. Imports `Base.metadata` from `app.database.base`
2. Imports all models (e.g. `app.database.models`) so they register with `Base`
3. Reads `DATABASE_URL` from `settings` at runtime
4. Supports both **offline** (SQL script generation) and **online** (direct DB) modes

### Migration File Anatomy

```python
revision = '11e46588a4f8'
down_revision = None          # None = first migration

def upgrade() -> None:
    op.create_table('users', ...)

def downgrade() -> None:
    op.drop_table('users')
```

---

## Authentication

### Flow

```
POST /api/v1/auth/register
    body: { username, email, password }
    → hashes password with Argon2
    → stores user in DB
    → returns UserResponse

POST /api/v1/auth/login
    body: { email, password }
    → verifies password hash
    → returns { accessToken: "<JWT>" }

GET /api/v1/users/me
    header: Authorization: Bearer <JWT>
    → verifies token signature + expiry
    → returns current UserResponse
```

### Password Hashing

Uses `pwdlib` with the Argon2 algorithm (memory-hard, recommended for passwords):

```python
password_hasher = PasswordHash.recommended()

def hash_password(password: str) -> str:
    return password_hasher.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    return password_hasher.verify(password, hashed_password)
```

### JWT Tokens

Tokens are signed with HS256 using secrets from `.env`:

```python
def create_access_token(data: dict, expires_delta: timedelta) -> str:
    payload = {**data, "exp": datetime.now(UTC) + expires_delta}
    return jwt.encode(payload, settings.jwt_access_token_secret.get_secret_value(), algorithm="HS256")

def verify_access_token(token: str) -> str | None:
    payload = jwt.decode(token, secret, algorithms=["HS256"], options={"require": ["sub", "exp"]})
    return payload.get("sub")  # returns user_id string, or None on failure
```

The `sub` claim holds the user's numeric ID as a string.

### Protected Routes

`CurrentUser` is a type alias that bundles the dependency:

```python
CurrentUser = Annotated[User, Depends(get_current_user)]

# Usage in any router:
async def get_me(current_user: CurrentUser):
    return current_user
```

---

## Exception Handling

Domain exceptions live in `app/core/exceptions.py`. Each exception class carries its own HTTP status code, keeping services completely free of HTTP/FastAPI imports.

### Exception Classes

```python
class NotFoundException(Exception):
    def __init__(self, detail: str = "Resource not found"):
        self.status = 404
        self.detail = detail

class ConflictException(Exception):
    def __init__(self, detail: str = "Conflict"):
        self.status = 409
        self.detail = detail

class BadRequestException(Exception): ...   # 400
class UnauthorizedException(Exception): ... # 401
class ForbiddenException(Exception): ...    # 403
```

### Registering Handlers

All handlers are wired up via a single function called in `main.py`:

```python
# app/core/exceptions.py
def register_exception_handlers(app: FastAPI):
    @app.exception_handler(NotFoundException)
    async def not_found_handler(request, exc):
        return JSONResponse(status_code=exc.status, content={"detail": exc.detail})
    # ... one handler per exception class

# main.py
register_exception_handlers(app)
```

This keeps `main.py` clean and groups all error-handling logic in one place.

### Usage in Services

```python
# services raise domain exceptions — no FastAPI imports needed
async def get_by_id(self, user_id: int):
    user = await self.repo.get_by_id(user_id)
    if not user:
        raise NotFoundException("User not found")
    return user
```

---

## API Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/api/v1/auth/register` | No | Register a new user |
| `POST` | `/api/v1/auth/login` | No | Login, returns JWT |
| `GET` | `/api/v1/users/me` | Bearer JWT | Get current user profile |

Interactive docs available at `/docs` (Swagger UI) and `/redoc` when the server is running.

---

## Application Startup

`main.py` is intentionally minimal — it wires together routers, lifespan, and exception handlers:

```python
app = FastAPI(lifespan=lifespan)

app.include_router(auth_router.router, prefix="/api/v1/auth")
app.include_router(users_router.router, prefix="/api/v1/users")

register_exception_handlers(app)
```

The `lifespan` context manager handles startup/shutdown:

```python
@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Startup: verify DB is reachable
    async with AsyncSessionLocal() as session:
        await session.execute(text("SELECT 1"))
    yield
    # Shutdown: dispose connection pool
    await engine.dispose()
```

If the database is unreachable on startup, the app will fail fast rather than serving traffic with a broken connection.
