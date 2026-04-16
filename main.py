from contextlib import asynccontextmanager

from sqlalchemy import text
from fastapi import FastAPI

from app.database.base import engine, AsyncSessionLocal
from app.auth import router as auth_router
from app.users import router as users_router
from app.core.exceptions import register_exception_handlers

@asynccontextmanager
async def lifespan(_app: FastAPI):
  # Startup
  # verify DB is reachable
  async with AsyncSessionLocal() as session:
    await session.execute(text("SELECT 1"))
  yield
  # Shutdown
  await engine.dispose()

app = FastAPI(lifespan=lifespan)

app.include_router(auth_router.router, prefix="/api/v1/auth")
app.include_router(users_router.router, prefix="/api/v1/users")

register_exception_handlers(app)
