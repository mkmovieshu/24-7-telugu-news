# config.py

from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Render / Koyeb లో వున్న ENV variables
    MONGO_URL: str
    MONGO_DB_NAME: str
    ADMIN_SECRET: str

    # ఆప్షనల్ – లేకపోయినా పర్లేదు
    GOOGLE_API_KEY: str | None = None
    RSS_FEEDS: str | None = None

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()


#❗ఇదే పేరు కోసం db.py, app.py వెతుకుతున్నాయి
settings: Settings = get_settings()
