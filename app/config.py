from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    database_hostname: Optional[str] = "localhost"
    database_port: Optional[str] = "5432"
    database_password: Optional[str] = ""
    database_name: Optional[str] = "test_db"
    database_username: Optional[str] = "test_user"
    secret_key: Optional[str] = "test_secret_key"
    algorithm: Optional[str] = "HS256"
    access_token_expire_minutes: Optional[int] = 30
    sqlite_uri: Optional[str] = "sqlite:///./test.db"

    class Config:
        env_file = ".env"
        extra = "allow"  # Allow extra fields from .env file

settings = Settings()