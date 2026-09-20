from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "mysql+pymysql://root:password@localhost:3306/eventflow"
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_NAME: str = "eventflow"
    DB_USER: str = "root"
    DB_PASSWORD: str = "password"

    SECRET_KEY: str = "your-super-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    UPLOAD_DIRECTORY: str = "uploads/"
    MAX_UPLOAD_SIZE: int = 10485760

    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    class Config:
        env_file = ".env"


settings = Settings()
