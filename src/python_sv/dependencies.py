from __future__ import annotations

import secrets
from datetime import datetime, timezone

from fastapi import Request
from fastapi.templating import Jinja2Templates

from python_sv.config import BASE_DIR, get_settings

settings = get_settings()

page_content: dict[str, str] = {}


def context_processor(request: Request) -> dict[str, str | int]:
    return {
        "csp_nonce": getattr(request.state, "csp_nonce", secrets.token_urlsafe(16)),
        "current_year": datetime.now(timezone.utc).year,
    }


templates = Jinja2Templates(
    directory=BASE_DIR / "templates",
    context_processors=[context_processor],
)
templates.env.globals["whatsapp_url"] = settings.whatsapp_url  # ty: ignore[invalid-assignment]
templates.env.globals["static_url"] = lambda path: f"/static/{path}"  # ty: ignore[invalid-assignment]
