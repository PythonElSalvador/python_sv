from __future__ import annotations

import logging

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, Response

from python_sv.config import get_settings
from python_sv.dependencies import (
    page_content,
    templates,
)

_settings = get_settings()

logger = logging.getLogger("pythonsv")

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/robots.txt", response_class=PlainTextResponse)
async def robots_txt() -> str:
    return f"User-agent: *\nAllow: /\nSitemap: {_settings.base_url}/sitemap.xml\n"


@router.get("/sitemap.xml", response_class=PlainTextResponse)
async def sitemap_xml() -> str:
    return (
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


_PAGE_CACHE_HEADERS = {"cache-control": "public, max-age=3600"}


@router.get("/", response_class=HTMLResponse)
async def home(request: Request) -> Response:
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": page_content["title"],
            "body": page_content["body"],
        },
        headers=_PAGE_CACHE_HEADERS,
    )


@router.get("/codigo-de-conducta", response_class=HTMLResponse)
async def code_of_conduct(request: Request) -> Response:
    return templates.TemplateResponse(
        request=request,
        name="codigo-de-conducta.html",
        headers=_PAGE_CACHE_HEADERS,
    )


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
    return templates.TemplateResponse(
        request=request,
        name="calendario.html",
        context={"events": EVENTS},
        headers=_PAGE_CACHE_HEADERS,
    )
