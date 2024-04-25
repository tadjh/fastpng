from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import (
    Field,
    RedisDsn
)

class Settings(BaseSettings):
    """
    Base settings for the FastPNG application

    """    
    redis_dsn: RedisDsn = Field("redis://redis:6379/0", description="Redis DSN")
    cache_expire: int = Field(3600, description="The default cache expiry time in seconds")