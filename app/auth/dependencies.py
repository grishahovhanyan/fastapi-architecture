from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer

from app.database.models.user import User
from app.users.service import get_user_service, UserService
from .utils import verify_access_token


security = HTTPBearer()

async def get_current_user(
  user_service: Annotated[UserService, Depends(get_user_service)],
  credentials =  Depends(security),
) -> User:
  token = credentials.credentials

  user_id = verify_access_token(token)

  if not user_id:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Invalid or expired token",
      headers={"WWW-Authenticate": "Bearer"},
    )
  
  try:
    user_id_int = int(user_id)
  except (ValueError, TypeError):
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Invalid or expired token",
      headers={"WWW-Authenticate": "Bearer"},
    )
  
  user = await user_service.get_by_id(user_id_int)

  if not user:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Invalid or expired token",
      headers={"WWW-Authenticate": "Bearer"},
    )
  
  return user

CurrentUser = Annotated[User, Depends(get_current_user)]
  