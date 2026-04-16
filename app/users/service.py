from __future__ import annotations

from typing import Annotated
from fastapi import Depends

from app.database.models import User
from app.exceptions import NotFoundException

from .repository import get_user_repo, UserRepository
from .schemas import UserCreate


def get_user_service(repo: Annotated[UserRepository, Depends(get_user_repo)]) -> UserService:
  return UserService(repo)


class UserService:
  def __init__(self, repo: UserRepository):
    self.repo = repo

  async def get_by_id(self, user_id: int):
    user = await self.repo.get_by_id(user_id)

    if not user:
      raise NotFoundException("User not found")

    return user
  
  async def get_by_email(self, email: str):
    return await self.repo.get_by_email(email)
  
  async def get_by_username(self, username: str):
    return await self.repo.get_by_username(username)

  async def create_user(self, data: UserCreate):
    user = User(**data.model_dump())
    return await self.repo.create(user)
