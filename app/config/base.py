from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
  model_config = SettingsConfigDict(
    env_file=".env",
    env_file_encoding="utf-8"
  )

  jwt_access_token_secret: SecretStr
  jwt_access_token_expire_minutes: int = 15
  jwt_refresh_token_secret: SecretStr
  jwt_refresh_token_expire_minutes: int = 43200 # 30 days
  jwt_algorithm: str = "HS256"

  database_url: str

settings = Settings()
