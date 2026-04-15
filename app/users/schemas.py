from pydantic import BaseModel, ConfigDict, Field, EmailStr

class UserCreate(BaseModel): 
  username: str
  email: EmailStr
  password: str

class UserUpdate(BaseModel):
  username: str | None = Field(default=None, min_length=1, max_length=50)
  email: EmailStr | None = Field(default=None, max_length=120)

class UserResponse(BaseModel): 
  model_config = ConfigDict(from_attributes=True)

  id: int
  username: str
  email: str
