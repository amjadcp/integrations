from pydantic import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    ROOT_URL: str
    REDIS_URI: str
    AIRTABLE_CLIENT_ID: str
    AIRTABLE_CLIENT_SECRET: str
    NOTION_CLIENT_ID: str
    NOTION_CLIENT_SECRET: str
    HUBSPOT_CLIENT_ID: str
    HUBSPOT_CLIENT_SECRET: str
    class Config:
        env_file = ".env"

@lru_cache() # avoid reloading settings on every import
def get_settings():
    return Settings()