from __future__ import annotations

from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from tempfile import gettempdir

from fastapi import Request
from fastapi.templating import Jinja2Templates
from jinja2 import FileSystemBytecodeCache

from python_sv.config import BASE_DIR, get_settings

settings = get_settings()

page_content: dict[str, str] = {}

_cache_dir = Path(gettempdir()) / "jinja2_cache"
_cache_dir.mkdir(exist_ok=True)


@lru_cache(maxsize=1)
def _current_year() -> int:
    return datetime.now(timezone.utc).year


def context_processor(request: Request) -> dict[str, str | int]:
    return {
        "csp_nonce": request.state.csp_nonce,
        "current_year": _current_year(),
    }


templates = Jinja2Templates(
    directory=BASE_DIR / "templates",
    context_processors=[context_processor],
)
templates.env.bytecode_cache = FileSystemBytecodeCache(str(_cache_dir))
templates.env.auto_reload = settings.debug
templates.env.trim_blocks = True
templates.env.lstrip_blocks = True
templates.env.globals["whatsapp_url"] = settings.whatsapp_url  # ty: ignore[invalid-assignment]
