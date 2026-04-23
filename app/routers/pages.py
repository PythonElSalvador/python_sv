from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, PlainTextResponse

from app.config import Settings, get_settings
from app.dependencies import (
    page_content,
    templates,
)

logger = logging.getLogger("pythonsv")

router = APIRouter()


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get("/robots.txt", response_class=PlainTextResponse)
async def robots_txt(settings: Annotated[Settings, Depends(get_settings)]):
    return f"User-agent: *\nAllow: /\nSitemap: {settings.base_url}/sitemap.xml\n"


@router.get("/sitemap.xml", response_class=PlainTextResponse)
async def sitemap_xml(settings: Annotated[Settings, Depends(get_settings)]):
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        "  <url>\n"
        f"    <loc>{settings.base_url}/</loc>\n"
        "  </url>\n"
        "  <url>\n"
        f"    <loc>{settings.base_url}/codigo-de-conducta</loc>\n"
        "  </url>\n"
        "</urlset>\n"
    )


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": page_content["title"],
            "body": page_content["body"],
        },
    )


@router.get("/codigo-de-conducta", response_class=HTMLResponse)
async def code_of_conduct(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="codigo-de-conducta.html",
    )
