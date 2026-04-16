from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import http_exception_handler, request_validation_exception_handler
from starlette.exceptions import HTTPException as StarletteHTTPException


class BadRequestException(Exception):
  def __init__(self, detail: str = "Bad request"):
    self.status = status.HTTP_400_BAD_REQUEST
    self.detail = detail

class UnauthorizedException(Exception):
  def __init__(self, detail: str = "Unauthorized"):
    self.status = status.HTTP_401_UNAUTHORIZED
    self.detail = detail

class ForbiddenException(Exception):
  def __init__(self, detail: str = "Forbidden"):
    self.status = status.HTTP_403_FORBIDDEN
    self.detail = detail

class NotFoundException(Exception):
  def __init__(self, detail: str = "Resource not found"):
    self.status = status.HTTP_404_NOT_FOUND
    self.detail = detail

class ConflictException(Exception):
  def __init__(self, detail: str = "Conflict"):
    self.status = status.HTTP_409_CONFLICT
    self.detail = detail


def register_exception_handlers(app: FastAPI):
  @app.exception_handler(StarletteHTTPException)
  async def general_http_exception_handler(request: Request, exception: StarletteHTTPException):
    return await http_exception_handler(request, exception)

  @app.exception_handler(RequestValidationError)
  async def global_validation_exception_handler(request: Request, exception: RequestValidationError):
    return await request_validation_exception_handler(request, exception)


  @app.exception_handler(BadRequestException)
  async def bad_request_exception_handler(request: Request, exception: BadRequestException):
    return JSONResponse(status_code=exception.status, content={"detail": exception.detail})

  @app.exception_handler(UnauthorizedException)
  async def unauthorized_exception_handler(request: Request, exception: UnauthorizedException):
    return JSONResponse(status_code=exception.status, content={"detail": exception.detail}, headers={"WWW-Authenticate": "Bearer"})

  @app.exception_handler(ForbiddenException)
  async def not_found_exception_handler(request: Request, exception: ForbiddenException):
    return JSONResponse(status_code=exception.status, content={"detail": exception.detail})

  @app.exception_handler(NotFoundException)
  async def not_found_exception_handler(request: Request, exception: NotFoundException):
    return JSONResponse(status_code=exception.status, content={"detail": exception.detail})

  @app.exception_handler(ConflictException)
  async def conflict_exception_handler(request: Request, exception: ConflictException):
    return JSONResponse(status_code=exception.status, content={"detail": exception.detail})
