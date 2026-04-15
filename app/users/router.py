from typing import Annotated

from fastapi import APIRouter, Depends

from app.auth.dependencies import CurrentUser
from .service import get_user_service, UserService
from .schemas import UserResponse

router = APIRouter(tags=["Users"])

@router.get("/me", response_model=UserResponse)
async def get_user(
  user_service: Annotated[UserService, Depends(get_user_service)], # For example
  current_user: CurrentUser
):
  return current_user
