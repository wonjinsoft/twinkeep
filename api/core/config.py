"""환경 설정"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    redis_url: str = "redis://localhost:6379"
    database_url: str = "postgresql+asyncpg://twinkeep:twinkeep@localhost:5432/twinkeep"
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7일

    model_config = {"env_file": ".env"}


settings = Settings()
