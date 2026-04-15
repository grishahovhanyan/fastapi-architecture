from  __future__ import annotations

from datetime import timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, status

from app.config import settings
from app.users.service import get_user_service, UserService
from app.users.schemas import UserCreate
from .utils import hash_password, verify_password, create_access_token
from .schemas import RegisterSchema, LoginSchema, TokenResponseSchema


def get_auth_service(
  user_service: Annotated[UserService, Depends(get_user_service),]
) -> AuthService:
  return AuthService(user_service)


class AuthService:
  def __init__(self, user_service: UserService):
    self.user_service = user_service

  async def register(self, register_data: RegisterSchema):
    existing_user = await self.user_service.get_by_email(register_data.email)

    if existing_user:
      raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="User with such email already exists"
      )
    
    existing_user = await self.user_service.get_by_username(register_data.username)

    if existing_user:
      raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="User with such username already exists"
      )
    
    user= await self.user_service.create_user(UserCreate(
      username=register_data.username,
      email=register_data.email,
      password=hash_password(register_data.password),
    ))
    
    return user

  async def login(self, login_data: LoginSchema):
    user = await self.user_service.get_by_email(login_data.email)

    if not user or not verify_password(login_data.password, user.password):
      raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid email or password"
      )

    access_token_expires_delta = timedelta(minutes=settings.jwt_access_token_expire_minutes)
    access_token = create_access_token(
      data={ "sub": str(user.id) }, 
      expires_delta=access_token_expires_delta
    )
    
    return TokenResponseSchema(access_token=access_token)
