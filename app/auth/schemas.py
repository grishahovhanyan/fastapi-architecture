from pydantic import BaseModel, ConfigDict, Field, EmailStr


class RegisterSchema(BaseModel): 
  username: str = Field(min_length=1, max_length=50)
  email: EmailStr = Field(max_length=120)
  password: str = Field(min_length=8)

class LoginSchema(BaseModel):
  email: EmailStr = Field(max_length=120)
  password: str = Field(min_length=8)

class TokenResponseSchema(BaseModel):
  model_config = ConfigDict(from_attributes=True)

  access_token: str
