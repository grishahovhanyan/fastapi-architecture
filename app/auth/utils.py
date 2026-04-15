from datetime import datetime, UTC, timedelta

import jwt 
from pwdlib import PasswordHash
from fastapi.security import HTTPBearer

from app.config import settings


password_hasher = PasswordHash.recommended()

security = HTTPBearer()

def hash_password(password: str) -> str:
  return password_hasher.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
  return password_hasher.verify(password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta) -> str:
  to_encode = data.copy()

  if expires_delta:
    expire = datetime.now(UTC) + expires_delta
  else:
    expire = datetime.now(UTC) + timedelta(
      minutes=settings.jwt_access_token_expire_minutes
    )

  to_encode.update({ "exp": expire })

  token = jwt.encode(
    to_encode,
    settings.jwt_access_token_secret.get_secret_value(),
    algorithm=settings.jwt_algorithm
  )

  return token

def verify_access_token(token: str) -> dict | None:
  try:
    payload = jwt.decode(
      token,
      settings.jwt_access_token_secret.get_secret_value(),
      algorithms=[settings.jwt_algorithm],
      options={ "require": ["sub", "exp"] }
    )
  except jwt.InvalidTokenError:
    return None
  else: 
    return payload.get("sub")
  