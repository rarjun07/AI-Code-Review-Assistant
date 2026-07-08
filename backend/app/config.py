from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App Configuration
    APP_NAME: str = "AI Code Review Assistant"
    VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Database Configuration
    DATABASE_URL: str

    # JWT Configuration
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    class Config:
        env_file = ".env"


settings = Settings()