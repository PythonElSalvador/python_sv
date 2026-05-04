from __future__ import annotations

import gzip
import io
import logging
import pathlib
import secrets
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

import brotli

import frontmatter
import markdown
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.types import ASGIApp, Receive, Scope, Send
from uvicorn.logging import DefaultFormatter

from motor.motor_asyncio import AsyncIOMotorClient

from python_sv.config import BASE_DIR, get_settings
from python_sv.dependencies import page_content, templates
from python_sv.http import HttpClients, create_aio_session, create_httpx_client
from python_sv.routers.admin import router as admin_router
from python_sv.routers.pages import router
from python_sv.routers.signup import router as signup_router


settings = get_settings()
logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))
logger = logging.getLogger("pythonsv")
logger.handlers = [logging.StreamHandler()]
logger.handlers[0].setFormatter(DefaultFormatter("%(levelprefix)s %(message)s"))
logger.propagate = False


def load_page(slug: str) -> frontmatter.Post:
    path = BASE_DIR.parent.parent / "content" / f"{slug}.md"
    return frontmatter.load(str(path))


def _build_static_hashes() -> dict[str, str]:
    static_dir = BASE_DIR / "static"
    hashes = {}
    for f in static_dir.rglob("*"):
        if f.is_file():
            rel = f.relative_to(static_dir)
            hashes[str(rel)] = hex(int(f.stat().st_mtime))[2:]
    return hashes


# Raw ASGI middleware — intentionally avoids BaseHTTPMiddleware to prevent
# issues with streaming responses and for better performance.
class SecurityHeadersMiddleware:
    _static_headers: list[tuple[bytes, bytes]] = [
        (b"x-content-type-options", b"nosniff"),
        (b"x-frame-options", b"DENY"),
        (b"referrer-policy", b"strict-origin-when-cross-origin"),
        (b"permissions-policy", b"camera=(), microphone=(), geolocation=()"),
        (b"cross-origin-opener-policy", b"same-origin"),
    ]
    _hsts_header: tuple[bytes, bytes] = (
        b"strict-transport-security",
        b"max-age=63072000; includeSubDomains; preload",
    )
    _csp_template: str = (
        "default-src 'self'; "
        "script-src 'self' 'nonce-{}'; "
        "style-src 'self' 'unsafe-inline'; "
        "font-src 'self'; "
        "img-src 'self' data:; "
        "connect-src 'self'; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self'; "
        "upgrade-insecure-requests"
    )
    _static_csp: bytes = (
        b"default-src 'none'; "
        b"style-src 'self' 'unsafe-inline'; "
        b"font-src 'self'; "
        b"img-src 'self' data:"
    )
    _static_immutable_headers: list[tuple[bytes, bytes]] = [
        *_static_headers,
        _hsts_header,
        (b"content-security-policy", _static_csp),
        (b"cache-control", b"public, max-age=31536000, immutable"),
    ]
    _static_debug_headers: list[tuple[bytes, bytes]] = [
        *_static_headers,
        (b"content-security-policy", _static_csp),
    ]

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")

        if path.startswith("/static/"):
            scope.setdefault("state", {})["csp_nonce"] = ""
            extra = (
                self._static_immutable_headers
                if not settings.debug
                else self._static_debug_headers
            )

            async def static_send(message: Any) -> None:
                if message["type"] == "http.response.start":
                    headers = list(message.get("headers", []))
                    headers.extend(extra)
                    message = {**message, "headers": headers}
                await send(message)

            await self.app(scope, receive, static_send)
            return

        nonce = secrets.token_urlsafe(16)
        state = scope.setdefault("state", {})
        state["csp_nonce"] = nonce
        state["request_start"] = time.perf_counter()
        csp = self._csp_template.format(nonce).encode()

        hsts = self._hsts_header

        async def send_wrapper(message: Any) -> None:
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                headers.extend(
                    [
                        *self._static_headers,
                        hsts,
                        (b"content-security-policy", csp),
                    ]
                )
                message = {**message, "headers": headers}
            await send(message)

        await self.app(scope, receive, send_wrapper)


_COMPRESSIBLE_TYPES = frozenset(
    {
        b"text/html",
        b"text/css",
        b"text/plain",
        b"text/xml",
        b"application/json",
        b"application/javascript",
        b"application/xml",
        b"image/svg+xml",
    }
)

_COMPRESSIBLE_EXTS = frozenset({".css", ".js", ".svg", ".json", ".xml", ".txt"})


def _precompress_static(static_dir: pathlib.Path) -> dict[str, tuple[bytes, bytes]]:
    cache: dict[str, tuple[bytes, bytes]] = {}
    for f in static_dir.rglob("*"):
        if not f.is_file() or f.suffix not in _COMPRESSIBLE_EXTS:
            continue
        raw = f.read_bytes()
        if len(raw) < 256:
            continue
        rel = str(f.relative_to(static_dir))
        br_data = brotli.compress(raw, quality=11)
        buf = io.BytesIO()
        with gzip.GzipFile(fileobj=buf, mode="wb", compresslevel=9) as gz_f:
            gz_f.write(raw)
        gz_data = buf.getvalue()
        cache[rel] = (br_data, gz_data)
    return cache


_static_compress_cache: dict[str, tuple[bytes, bytes]] = {}

_page_cache: dict[str, str] = {}


def _prerender_pages(app: FastAPI) -> None:
    from python_sv.dependencies import _current_year
    from python_sv.routers.pages import _NONCE_SENTINEL, _RENDER_MS_SENTINEL

    env = templates.env
    ctx = {
        "csp_nonce": _NONCE_SENTINEL,
        "current_year": _current_year(),
        "render_time_ms": _RENDER_MS_SENTINEL,
        "whatsapp_url": settings.whatsapp_url,
        "title": page_content.get("title", "Python SV"),
        "body": page_content.get("body", ""),
    }

    from python_sv.routers.pages import EVENTS

    page_defs: list[tuple[str, str, dict[str, Any]]] = [
        ("index", "index.html", {}),
        ("calendario", "calendario.html", {"events": EVENTS}),
        ("codigo-de-conducta", "codigo-de-conducta.html", {}),
    ]
    for slug, template_name, extra_ctx in page_defs:
        tmpl = env.get_template(template_name)
        html = tmpl.render({**ctx, **extra_ctx})
        _page_cache[slug] = html

    app.state.page_cache = _page_cache


class CompressMiddleware:
    def __init__(self, app: ASGIApp, minimum_size: int = 500) -> None:
        self.app = app
        self.minimum_size = minimum_size

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        accept = ""
        for header_name, header_value in scope.get("headers", []):
            if header_name == b"accept-encoding":
                accept = header_value.decode("latin-1")
                break

        use_br = "br" in accept
        use_gz = not use_br and "gzip" in accept

        if not use_br and not use_gz:
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")
        if path.startswith("/static/") and _static_compress_cache:
            rel = path[len("/static/") :].split("?")[0]
            cached = _static_compress_cache.get(rel)
            if cached:
                await self._serve_static_compressed(
                    scope, receive, send, cached, use_br
                )
                return

        already_encoded = False
        body_parts: list[bytes] = []
        initial_message: dict[str, Any] = {}
        content_type = b""

        async def buffer_send(message: Any) -> None:
            nonlocal initial_message, content_type, already_encoded
            if message["type"] == "http.response.start":
                initial_message = message
                for k, v in message.get("headers", []):
                    if k == b"content-type":
                        content_type = v.split(b";")[0].strip()
                    elif k == b"content-encoding":
                        already_encoded = True
                if already_encoded:
                    await send(message)
                    return
            elif message["type"] == "http.response.body":
                if already_encoded:
                    await send(message)
                    return
                body = message.get("body", b"")
                if body:
                    body_parts.append(body)
                if not message.get("more_body", False):
                    raw = b"".join(body_parts)
                    if (
                        len(raw) >= self.minimum_size
                        and content_type in _COMPRESSIBLE_TYPES
                    ):
                        if use_br:
                            compressed = brotli.compress(raw, quality=5)
                            encoding = b"br"
                        else:
                            buf = io.BytesIO()
                            with gzip.GzipFile(
                                fileobj=buf, mode="wb", compresslevel=6
                            ) as gz_file:
                                gz_file.write(raw)
                            compressed = buf.getvalue()
                            encoding = b"gzip"

                        headers = [
                            (k, v)
                            for k, v in initial_message.get("headers", [])
                            if k != b"content-length"
                        ]
                        headers.append((b"content-encoding", encoding))
                        headers.append(
                            (b"content-length", str(len(compressed)).encode())
                        )
                        headers.append((b"vary", b"Accept-Encoding"))
                        initial_message = {**initial_message, "headers": headers}
                        await send(initial_message)
                        await send({"type": "http.response.body", "body": compressed})
                    else:
                        await send(initial_message)
                        await send({"type": "http.response.body", "body": raw})

        await self.app(scope, receive, buffer_send)

    async def _serve_static_compressed(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
        cached: tuple[bytes, bytes],
        use_br: bool,
    ) -> None:
        br_data, gz_data = cached
        initial_message: dict[str, Any] = {}

        async def intercept_send(message: Any) -> None:
            nonlocal initial_message
            if message["type"] == "http.response.start":
                initial_message = message
            elif message["type"] == "http.response.body":
                if not message.get("more_body", False):
                    compressed = br_data if use_br else gz_data
                    encoding = b"br" if use_br else b"gzip"
                    headers = [
                        (k, v)
                        for k, v in initial_message.get("headers", [])
                        if k != b"content-length"
                    ]
                    headers.append((b"content-encoding", encoding))
                    headers.append((b"content-length", str(len(compressed)).encode()))
                    headers.append((b"vary", b"Accept-Encoding"))
                    await send({**initial_message, "headers": headers})
                    await send({"type": "http.response.body", "body": compressed})

        await self.app(scope, receive, intercept_send)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    index_page = load_page("index")
    page_content["title"] = str(index_page.metadata.get("title", "Python SV"))
    page_content["body"] = markdown.markdown(index_page.content)

    static_hashes = _build_static_hashes()

    def static_url(path: str) -> str:
        h = static_hashes.get(path, "")
        return f"/static/{path}?v={h}" if h else f"/static/{path}"

    templates.env.globals["static_url"] = static_url  # ty: ignore[invalid-assignment]

    _static_compress_cache.update(_precompress_static(BASE_DIR / "static"))
    logger.info("pre-compressed %d static files", len(_static_compress_cache))

    _prerender_pages(app)
    logger.info("pre-rendered %d page templates", len(_page_cache))

    from python_sv.routers.pages import cache_html_bytes

    cache_html_bytes(_page_cache)

    link_parts = []
    for path, rel_type in [
        ("fonts/bricolage-grotesque-latin.woff2", "font/woff2"),
        ("fonts/dm-sans-latin.woff2", "font/woff2"),
    ]:
        url = static_url(path)
        link_parts.append(
            f"<{url}>; rel=preload; as=font; type={rel_type}; crossorigin"
        )
    css_url = static_url("css/pysv.css")
    link_parts.append(f"<{css_url}>; rel=preload; as=style")
    app.state.link_header = ", ".join(link_parts)

    mongo_client: AsyncIOMotorClient[Any] | None = None
    if settings.mongodb_uri:
        mongo_client = AsyncIOMotorClient(settings.mongodb_uri)
        db = mongo_client.pythonsv
        await db.signups.create_index("email", unique=True)
        await db.signups.create_index([("created_at", -1)])
        app.state.db = db
        logger.info("connected to mongodb")
    else:
        app.state.db = None

    async with (
        create_aio_session() as aio_session,
        create_httpx_client() as httpx_client,
    ):
        app.state.http = HttpClients(aio=aio_session, httpx_client=httpx_client)
        logger.info("pythonsv started")
        yield
        logger.info("pythonsv shutting down")

    if mongo_client:
        mongo_client.close()


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


def create_app() -> FastAPI:
    application = FastAPI(
        lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None
    )
    application.add_middleware(SecurityHeadersMiddleware)
    application.add_middleware(CompressMiddleware, minimum_size=500)
    application.add_middleware(
        TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts
    )
    application.mount(
        "/static", StaticFiles(directory=BASE_DIR / "static"), name="static"
    )
    application.include_router(router)
    application.include_router(signup_router)
    application.include_router(admin_router)

    @application.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> HTMLResponse:
        if request.url.path.startswith("/api/"):
            return templates.TemplateResponse(
                request=request,
                name="partials/signup_error.html",
                context={
                    "message": "Por favor revisa que todos los campos estén correctos."
                },
                status_code=422,
            )
        return render_error(422, "Invalid request.", request)

    @application.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> HTMLResponse:
        if exc.status_code == 401:
            return HTMLResponse(
                content="Unauthorized",
                status_code=401,
                headers={"WWW-Authenticate": "Basic"},
            )
        if exc.status_code == 404:
            return render_error(404, "Page not found.", request)
        return render_error(exc.status_code, str(exc.detail), request)

    @application.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> HTMLResponse:
        try:
            logger.exception("Unhandled error")
            return render_error(500, "Something went wrong. Please try again.", request)
        except Exception:
            return HTMLResponse("Internal Server Error", status_code=500)

    return application


app = create_app()
