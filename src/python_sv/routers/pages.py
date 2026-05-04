from __future__ import annotations

import logging
import time

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, Response

from python_sv.config import get_settings

_settings = get_settings()
_ROBOTS_TXT = f"User-agent: *\nAllow: /\nSitemap: {_settings.base_url}/sitemap.xml\n"
_SITEMAP_XML = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    "  <url>\n"
    f"    <loc>{_settings.base_url}/</loc>\n"
    "  </url>\n"
    "  <url>\n"
    f"    <loc>{_settings.base_url}/calendario</loc>\n"
    "  </url>\n"
    "  <url>\n"
    f"    <loc>{_settings.base_url}/codigo-de-conducta</loc>\n"
    "  </url>\n"
    "</urlset>\n"
)

logger = logging.getLogger("pythonsv")

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/robots.txt", response_class=PlainTextResponse)
async def robots_txt() -> str:
    return _ROBOTS_TXT


@router.get("/sitemap.xml", response_class=PlainTextResponse)
async def sitemap_xml() -> str:
    return _SITEMAP_XML


_PAGE_CACHE_HEADERS = (
    {} if _settings.debug else {"cache-control": "public, max-age=3600"}
)

_NONCE_SENTINEL = "__PYSV_NONCE__"
_RENDER_MS_SENTINEL = "__RENDER_MS__"


def _serve_cached(request: Request, slug: str) -> Response:
    html = request.app.state.page_cache[slug]
    nonce = request.state.csp_nonce
    elapsed = f"{(time.perf_counter() - request.state.request_start) * 1000:.1f}"
    html = html.replace(_NONCE_SENTINEL, nonce).replace(_RENDER_MS_SENTINEL, elapsed)
    return HTMLResponse(content=html, headers=_PAGE_CACHE_HEADERS)


@router.get("/", response_class=HTMLResponse)
async def home(request: Request) -> Response:
    return _serve_cached(request, "index")


@router.get("/codigo-de-conducta", response_class=HTMLResponse)
async def code_of_conduct(request: Request) -> Response:
    return _serve_cached(request, "codigo-de-conducta")


EVENTS = [
    {
        "title": "Python SV Meetup — AI, Memory & Security",
        "month": "May",
        "year": "2026",
        "date_display": "Sábado 2 de mayo, 2026",
        "location": "Presencial — lugar por confirmar",
        "topics": ["AI", "Memory", "Security"],
        "description": "Nuestro primer meetup presencial. Charlas y demos sobre inteligencia artificial, manejo de memoria y seguridad en Python.",
        "link": None,
        "link_text": "",
    },
    {
        "title": "Python SV Meetup — Virtual",
        "month": "Jun",
        "year": "2026",
        "date_display": "Fecha por confirmar",
        "location": "Virtual",
        "topics": [],
        "description": "Meetup virtual de la comunidad. Tema por confirmar.",
        "link": None,
        "link_text": "",
    },
]


@router.get("/calendario", response_class=HTMLResponse)
async def calendar(request: Request) -> Response:
    return _serve_cached(request, "calendario")
