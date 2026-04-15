from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.user import User
from app.database.base import get_db
from .utils import verify_access_token


security = HTTPBearer()

# TODO: user UserService instead of `db: Annotated[AsyncSession, Depends(get_db)]`

async def get_current_user(
  db: Annotated[AsyncSession, Depends(get_db)],
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
  
  result = await db.execute(select(User).where(User.id == user_id_int))
  user = result.scalars().first()

  if not user:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Invalid or expired token",
      headers={"WWW-Authenticate": "Bearer"},
    )
  
  return user

CurrentUser = Annotated[User, Depends(get_current_user)]
  