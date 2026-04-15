from typing import Annotated

from fastapi import APIRouter, Depends

from app.users.schemas import UserResponse
from .service import get_auth_service, AuthService
from .schemas import RegisterSchema, LoginSchema, TokenResponseSchema

router = APIRouter(tags=["Auth"])

@router.post("/register", response_model=UserResponse)
async def register(
  auth_service: Annotated[AuthService, Depends(get_auth_service)],
  register_data: RegisterSchema
):
  return await auth_service.register(register_data)

@router.post("/login")
async def login(
  auth_service: Annotated[AuthService, Depends(get_auth_service)],
  login_data: LoginSchema
):
  return await auth_service.login(login_data)
