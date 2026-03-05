from __future__ import annotations

import hashlib
import hmac
import secrets
import time
from collections import defaultdict
from datetime import datetime, timezone

import motor.motor_asyncio
from fastapi import Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr, Field

from app.config import BASE_DIR, get_settings

MAX_FIELD_LEN = 200

settings = get_settings()

CSRF_SECRET = bytes.fromhex(settings.csrf_secret)
CSRF_TTL = 3600  # 1 hour

# NOTE: In-memory rate limiting — resets on restart and is per-process
# (not shared across gunicorn workers). Replace with Redis when scaling.
rate_limits: defaultdict[str, list[float]] = defaultdict(list)
RATE_WINDOW = 300  # 5 minutes
RATE_MAX = 5  # max submissions per window

page_content: dict[str, str] = {}

mongo_client: motor.motor_asyncio.AsyncIOMotorClient = None  # type: ignore[assignment]
db: motor.motor_asyncio.AsyncIOMotorDatabase = None  # type: ignore[assignment]


class SignupForm(BaseModel):
    name: str = Field(max_length=MAX_FIELD_LEN)
    email: EmailStr
    city: str = Field(max_length=MAX_FIELD_LEN)
    role: str = Field(max_length=MAX_FIELD_LEN)
    other_city: str = Field("", max_length=MAX_FIELD_LEN)
    csrf_token: str = ""


def context_processor(request: Request) -> dict[str, str | int]:
    return {
        "csp_nonce": getattr(request.state, "csp_nonce", secrets.token_urlsafe(16)),
        "current_year": datetime.now(timezone.utc).year,
    }


templates = Jinja2Templates(
    directory=BASE_DIR / "templates",
    context_processors=[context_processor],
)
templates.env.globals["whatsapp_url"] = settings.whatsapp_url
templates.env.globals["static_url"] = lambda path: f"/static/{path}"


def new_csrf_token() -> str:
    timestamp = str(int(time.time()))
    sig = hmac.new(CSRF_SECRET, timestamp.encode(), hashlib.sha256).hexdigest()
    return f"{timestamp}.{sig}"


def verify_csrf_token(token: str) -> bool:
    parts = token.split(".", 1)
    if len(parts) != 2:
        return False
    timestamp, sig = parts
    try:
        ts = int(timestamp)
    except ValueError:
        return False
    if time.time() - ts > CSRF_TTL:
        return False
    expected = hmac.new(CSRF_SECRET, timestamp.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(sig, expected)


def check_rate_limit(ip: str) -> bool:
    now = time.monotonic()
    timestamps = rate_limits[ip]
    rate_limits[ip] = [t for t in timestamps if now - t < RATE_WINDOW]
    if len(rate_limits[ip]) >= RATE_MAX:
        return False
    rate_limits[ip].append(now)

    # Prune empty entries to prevent unbounded growth
    if len(rate_limits) > RATE_MAX * 20:
        stale = [k for k, v in rate_limits.items() if not v]
        for k in stale:
            del rate_limits[k]

    return True
