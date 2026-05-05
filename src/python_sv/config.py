from __future__ import annotations

import secrets
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    whatsapp_url: str = "https://chat.whatsapp.com/Ly7exFkvNe0AJ8dFR2utwp"
    base_url: str = "https://pythonsv.com"
    allowed_hosts: list[str] = ["localhost", "127.0.0.1"]
    log_level: str = "INFO"
    csrf_secret: str = secrets.token_hex(32)
    mongodb_uri: str = ""
    admin_username: str = ""
    admin_password: str = ""
    resend_api_key: str = ""
    notification_from: str = "Python SV <hola@pythonsv.com>"
    notification_to: str = ""
    debug: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
