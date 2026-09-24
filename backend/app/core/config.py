"""EventFlow Settings Configuration.

All secrets MUST come from environment / .env in production.
Defaults below are safe dev/test fallbacks only (no real credentials).
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "mysql+pymysql://root:password@localhost:3306/eventflow"
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_NAME: str = "eventflow"
    DB_USER: str = "root"
    DB_PASSWORD: str = "password"

    # REQUIRED in production: set SECRET_KEY env var (min 32 chars).
    SECRET_KEY: str = "change-me-please-set-SECRET_KEY-env"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    UPLOAD_DIRECTORY: str = "uploads/"
    # Verification docs live OUTSIDE any public static dir (Phase 1 security)
    VERIFICATION_DOC_DIR: str = "uploads/verifications/"
    MAX_UPLOAD_SIZE: int = 10485760

    FRONTEND_URL: str = "http://localhost:5173"
    BACKEND_URL: str = "http://localhost:8000"

    # eSewa TEST/UAT defaults only — override with real merchant creds via env.
    ESEWA_MERCHANT_CODE: str = "EPAYTEST"
    ESEWA_SECRET_KEY: str = ""
    ESEWA_BASE_URL: str = "https://rc-epay.esewa.com.np"
    # Require live eSewa status-lookup on verify (fail closed). Tests disable it.
    ESEWA_STATUS_CHECK: bool = True
    # Khalti TEST defaults only — override via env.
    KHALTI_SECRET_KEY: str = ""
    KHALTI_BASE_URL: str = "https://a.khalti.com/api/v2"

    # Demo settlement/accounting defaults (admin-editable via platform_settings)
    PLATFORM_TICKET_FEE: float = 20.0
    WITHDRAWAL_SERVICE_FEE: float = 20.0
    SETTLEMENT_HOLD_DAYS: int = 2

    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    class Config:
        env_file = ".env"


settings = Settings()
