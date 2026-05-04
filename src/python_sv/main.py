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
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.types import ASGIApp, Receive, Scope, Send
from uvicorn.logging import DefaultFormatter

from python_sv.config import BASE_DIR, get_settings
from python_sv.dependencies import page_content, templates
from python_sv.http import HttpClients, create_aio_session, create_httpx_client
from python_sv.routers.pages import router


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
    ]
    _csp_template: str = (
        "default-src 'self'; "
        "script-src 'self' 'nonce-{}'; "
        "style-src 'self' 'unsafe-inline'; "
        "font-src 'self'; "
        "img-src 'self' data:; "
        "connect-src 'self'; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self'"
    )
    _static_csp: bytes = (
        b"default-src 'none'; "
        b"style-src 'self' 'unsafe-inline'; "
        b"font-src 'self'; "
        b"img-src 'self' data:"
    )
    _static_immutable_headers: list[tuple[bytes, bytes]] = [
        *_static_headers,
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

        async def send_wrapper(message: Any) -> None:
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                headers.extend(
                    [
                        *self._static_headers,
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

        body_parts: list[bytes] = []
        initial_message: dict[str, Any] = {}
        content_type = b""

        async def buffer_send(message: Any) -> None:
            nonlocal initial_message, content_type
            if message["type"] == "http.response.start":
                initial_message = message
                for k, v in message.get("headers", []):
                    if k == b"content-type":
                        content_type = v.split(b";")[0].strip()
                        break
            elif message["type"] == "http.response.body":
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

    async with (
        create_aio_session() as aio_session,
        create_httpx_client() as httpx_client,
    ):
        app.state.http = HttpClients(aio=aio_session, httpx_client=httpx_client)
        logger.info("pythonsv started")
        yield
        logger.info("pythonsv shutting down")


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

    @application.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> HTMLResponse:
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
