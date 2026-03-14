from __future__ import annotations

import hashlib
import logging
import secrets
from contextlib import asynccontextmanager

import frontmatter
import markdown
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.types import ASGIApp, Receive, Scope, Send
from uvicorn.logging import DefaultFormatter

from app.config import BASE_DIR, get_settings
from app.dependencies import page_content, templates
from app.routers.pages import router


settings = get_settings()
logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))
logger = logging.getLogger("pythonsv")
logger.handlers = [logging.StreamHandler()]
logger.handlers[0].setFormatter(DefaultFormatter("%(levelprefix)s %(message)s"))
logger.propagate = False


def load_page(slug: str) -> frontmatter.Post:
    path = BASE_DIR.parent / "content" / f"{slug}.md"
    return frontmatter.load(path)


def _file_hash(path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()[:10]


def _build_static_hashes() -> dict[str, str]:
    static_dir = BASE_DIR / "static"
    hashes = {}
    for f in static_dir.rglob("*"):
        if f.is_file():
            rel = f.relative_to(static_dir)
            hashes[str(rel)] = _file_hash(f)
    return hashes


# Raw ASGI middleware — intentionally avoids BaseHTTPMiddleware to prevent
# issues with streaming responses and for better performance.
class SecurityHeadersMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        nonce = secrets.token_urlsafe(16)
        scope.setdefault("state", {})["csp_nonce"] = nonce
        path = scope.get("path", "")

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                headers.extend(
                    [
                        (b"x-content-type-options", b"nosniff"),
                        (b"x-frame-options", b"DENY"),
                        (b"referrer-policy", b"strict-origin-when-cross-origin"),
                        (
                            b"permissions-policy",
                            b"camera=(), microphone=(), geolocation=()",
                        ),
                        (
                            b"content-security-policy",
                            (
                                f"default-src 'self'; "
                                f"script-src 'self' 'nonce-{nonce}'; "
                                f"style-src 'self' 'unsafe-inline'; "
                                f"font-src 'self'; "
                                f"img-src 'self' data:; "
                                f"connect-src 'self'; "
                                f"frame-ancestors 'none'; "
                                f"base-uri 'self'; "
                                f"form-action 'self'"
                            ).encode(),
                        ),
                    ]
                )
                if path.startswith("/static/") and not settings.debug:
                    headers.append(
                        (b"cache-control", b"public, max-age=31536000, immutable")
                    )
                message = {**message, "headers": headers}
            await send(message)

        await self.app(scope, receive, send_wrapper)


@asynccontextmanager
async def lifespan(app: FastAPI):
    index_page = load_page("index")
    page_content["title"] = index_page.metadata.get("title", "Python SV")
    page_content["body"] = markdown.markdown(index_page.content)

    static_hashes = _build_static_hashes()

    def static_url(path: str) -> str:
        h = static_hashes.get(path, "")
        return f"/static/{path}?v={h}" if h else f"/static/{path}"

    templates.env.globals["static_url"] = static_url

    logger.info("pythonsv started")
    yield
    logger.info("pythonsv shutting down")


app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
app.include_router(router)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return render_error(404, "Page not found.", request)
    return render_error(exc.status_code, str(exc.detail), request)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    try:
        logger.exception("Unhandled error")
        return render_error(500, "Something went wrong. Please try again.", request)
    except Exception:
        return HTMLResponse("Internal Server Error", status_code=500)


def render_error(code: int, message: str, request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="error.html",
        context={
            "code": code,
            "message": message,
        },
        status_code=code,
    )
