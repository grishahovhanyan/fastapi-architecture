from datetime import datetime
from pydantic import ConfigDict, Field, EmailStr

from app.utils.schemas import CustomBaseModel

class UserCreate(CustomBaseModel): 
  username: str
  email: EmailStr
  password: str

class UserUpdate(CustomBaseModel):
  username: str | None = Field(default=None, min_length=1, max_length=50)
  email: EmailStr | None = Field(default=None, max_length=120)

class UserResponse(CustomBaseModel): 
  model_config = ConfigDict(from_attributes=True)

  id: int
  username: str
  email: str
  created_at: datetime
  updated_at: datetime
