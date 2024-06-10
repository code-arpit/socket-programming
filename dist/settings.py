from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DEBUG: bool = True
    PROJECT_NAME: str = "WhizChat"

    DB_HOST: str = "db"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_NAME: str = "postgres"

    SECRET_KEY: str = "abc123fda4213dfr"
    JWT_ALGORITHM: str = "HS256"


settings = Settings()
