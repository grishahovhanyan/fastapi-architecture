from pydantic import ConfigDict, Field, EmailStr

from app.utils.schemas import CustomBaseModel

class RegisterSchema(CustomBaseModel): 
  username: str = Field(min_length=1, max_length=50)
  email: EmailStr = Field(max_length=120)
  password: str = Field(min_length=8)

class LoginSchema(CustomBaseModel):
  email: EmailStr = Field(max_length=120)
  password: str = Field(min_length=8)

class TokenResponseSchema(CustomBaseModel):
  model_config = ConfigDict(from_attributes=True)

  access_token: str
