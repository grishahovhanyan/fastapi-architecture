from contextlib import asynccontextmanager

from sqlalchemy import text
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import http_exception_handler, request_validation_exception_handler
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.database.base import engine, AsyncSessionLocal
from app.auth import router as auth_router
from app.users import router as users_router

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

@app.exception_handler(StarletteHTTPException)
async def general_http_exception_handler(request: Request, exception: StarletteHTTPException):
  return await http_exception_handler(request, exception)

@app.exception_handler(RequestValidationError)
async def global_validation_exception_handler(request: Request, exception: RequestValidationError):
  return await request_validation_exception_handler(request, exception)
