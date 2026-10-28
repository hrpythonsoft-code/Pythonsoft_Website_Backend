from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # Application
    APP_NAME: str = "PythonSoft API"
    APP_VERSION: str = "1.0.0"

    # CORS
    ALLOWED_ORIGINS: list[str]

    # MongoDB
    MONGODB_URL: str
    DB_NAME: str

    # JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 5760

    # Cookies
    COOKIE_SECURE: bool = True
    COOKIE_SAMESITE: str = "lax"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()