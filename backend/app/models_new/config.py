"""
MindMate Database Configuration
===============================
Fresh database configuration for multi-agent mental health platform.
"""

from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class DatabaseSettings(BaseSettings):
    """Database configuration settings"""
    
    # Database
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "mindmate_v2"  # New database name
    DB_USER: str = "mindmate"
    DB_PASSWORD: str = "mindmate_secure_2026"
    
    # Connection pool
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    
    # Redis (for caching/sessions)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    @property
    def database_url(self) -> str:
        """PostgreSQL connection URL"""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def async_database_url(self) -> str:
        """Async PostgreSQL connection URL"""
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def redis_url(self) -> str:
        """Redis connection URL"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_db_settings() -> DatabaseSettings:
    """Get cached database settings"""
    return DatabaseSettings()


# Export for convenience
db_settings = get_db_settings()
