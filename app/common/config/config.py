from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, Field

class Settings(BaseSettings):
    # PostgreSQL connection URL, e.g. postgresql://user:pass@localhost:5432/db
    database_url: PostgresDsn = Field(..., env="DATABASE_URL")

    # Application metadata
    app_name: str = Field("User API Service", env="APP_NAME")
    debug: bool = Field(False, env="DEBUG")

    # JWT settings
    secret_key:      str = Field(..., env="SECRET_KEY")
    jwt_algorithm:   str = Field("HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(60, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

# Singleton settings object for import
settings = Settings()