from typing import Literal, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App Configuration
    APP_NAME: str = "AI Code Review Assistant"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    FRONTEND_URL: str = "http://localhost:5173"
    CORS_ORIGINS: Optional[str] = None

    # Database Configuration
    DATABASE_URL: str

    # JWT Configuration
    SECRET_KEY: str = Field(min_length=32)
    ALGORITHM: Literal["HS256"] = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    PASSWORD_RESET_EXPIRE_MINUTES: int = 15
    PASSWORD_RESET_EMAIL_PROVIDER: Literal["disabled", "resend"] = "disabled"
    PASSWORD_RESET_FROM_EMAIL: Optional[str] = None
    RESEND_API_KEY: Optional[str] = None
    PASSWORD_RESET_RATE_LIMIT_EMAIL: int = Field(default=5, ge=1)
    PASSWORD_RESET_RATE_LIMIT_IP: int = Field(default=10, ge=1)
    PASSWORD_RESET_RATE_LIMIT_WINDOW_MINUTES: int = Field(default=15, ge=1)

    # AI Provider Configuration
    AI_PROVIDER: Literal["auto", "huggingface", "openai"] = "auto"

    # Hugging Face Configuration
    HF_TOKEN: Optional[str] = None
    HUGGINGFACE_MODEL: str = "Qwen/Qwen2.5-Coder-32B-Instruct:cheapest"
    HUGGINGFACE_BASE_URL: str = "https://router.huggingface.co/v1"

    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4.1-mini"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    @property
    def allowed_cors_origins(self) -> list[str]:
        """Return the configured browser origins without trailing slashes."""
        configured_origins = self.CORS_ORIGINS or self.FRONTEND_URL
        return [
            origin.strip().rstrip("/")
            for origin in configured_origins.split(",")
            if origin.strip()
        ]


settings = Settings()
