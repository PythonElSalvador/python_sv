from __future__ import annotations

import gzip
import io
import logging
import time

import brotli

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, Response

from python_sv.config import get_settings

_settings = get_settings()
_ROBOTS_TXT = f"User-agent: *\nAllow: /\nSitemap: {_settings.base_url}/sitemap.xml\n"
_LLMS_TXT = """\
# Python SV

> La comunidad de Python en El Salvador. Organizamos meetups presenciales, charlas técnicas y demos.

## Páginas

- [Inicio](https://pythonsv.com/): Página principal con información del próximo evento y formulario para unirse.
- [Calendario](https://pythonsv.com/calendario): Próximos meetups y eventos.
- [Código de Conducta](https://pythonsv.com/codigo-de-conducta): Reglas de convivencia de la comunidad.

## Contacto

- Email: conduct@pythonsv.com
- Meetup: https://www.meetup.com/python-sv_/
- WhatsApp: Enlace disponible en la página principal.

## Contexto

Python SV es una comunidad sin fines de lucro fundada en 2026 con el objetivo de revivir el ecosistema de Python en El Salvador. Organizamos meetups mensuales en San Salvador con charlas técnicas, demos en vivo y networking. La comunidad está abierta a estudiantes, profesionales y cualquier persona interesada en Python.
"""
_SITEMAP_XML = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    "  <url>\n"
    f"    <loc>{_settings.base_url}/</loc>\n"
    "  </url>\n"
    "  <url>\n"
    f"    <loc>{_settings.base_url}/propuestas</loc>\n"
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


@router.get("/llms.txt", response_class=PlainTextResponse)
async def llms_txt() -> Response:
    return PlainTextResponse(
        _LLMS_TXT,
        headers={"cache-control": "public, max-age=86400"},
    )


@router.get("/robots.txt", response_class=PlainTextResponse)
async def robots_txt() -> Response:
    return PlainTextResponse(
        _ROBOTS_TXT,
        headers={"cache-control": "public, max-age=86400"},
    )


@router.get("/sitemap.xml")
async def sitemap_xml() -> Response:
    return Response(
        content=_SITEMAP_XML,
        media_type="application/xml; charset=utf-8",
        headers={"cache-control": "public, max-age=86400"},
    )


_PAGE_CACHE_HEADERS = (
    {} if _settings.debug else {"cache-control": "public, max-age=3600"}
)

_NONCE_SENTINEL = "__PYSV_NONCE__"
_RENDER_MS_SENTINEL = "__RENDER_MS__"

_html_bytes_cache: dict[str, bytes] = {}


def cache_html_bytes(page_cache: dict[str, str]) -> None:
    for slug, html in page_cache.items():
        _html_bytes_cache[slug] = html.encode()


def _serve_cached(request: Request, slug: str) -> Response:
    nonce = request.state.csp_nonce
    elapsed = f"{(time.perf_counter() - request.state.request_start) * 1000:.1f}"

    raw = _html_bytes_cache.get(slug)
    if not raw:
        html = request.app.state.page_cache[slug]
        html = html.replace(_NONCE_SENTINEL, nonce).replace(
            _RENDER_MS_SENTINEL, elapsed
        )
        return HTMLResponse(content=html, headers=_PAGE_CACHE_HEADERS)

    raw = raw.replace(b"__PYSV_NONCE__", nonce.encode()).replace(
        b"__RENDER_MS__", elapsed.encode()
    )

    link_header = getattr(request.app.state, "link_header", "")
    extra_headers = {**_PAGE_CACHE_HEADERS}
    if link_header:
        extra_headers["link"] = link_header

    accept = request.headers.get("accept-encoding", "")
    if "br" in accept:
        return Response(
            content=brotli.compress(raw, quality=1),
            media_type="text/html; charset=utf-8",
            headers={
                **extra_headers,
                "content-encoding": "br",
                "vary": "Accept-Encoding",
            },
        )
    if "gzip" in accept:
        buf = io.BytesIO()
        with gzip.GzipFile(fileobj=buf, mode="wb", compresslevel=1) as gz_f:
            gz_f.write(raw)
        return Response(
            content=buf.getvalue(),
            media_type="text/html; charset=utf-8",
            headers={
                **extra_headers,
                "content-encoding": "gzip",
                "vary": "Accept-Encoding",
            },
        )
    return Response(
        content=raw,
        media_type="text/html; charset=utf-8",
        headers=extra_headers,
    )


@router.get("/", response_class=HTMLResponse)
async def home(request: Request) -> Response:
    return _serve_cached(request, "index")


@router.get("/codigo-de-conducta", response_class=HTMLResponse)
async def code_of_conduct(request: Request) -> Response:
    return _serve_cached(request, "codigo-de-conducta")


EVENTS = [
    {
        "title": "Introducción a FastAPI",
        "month": "JUL",
        "year": "2026",
        "day": 18,
        "date_display": "Sábado 18 de julio, 2PM–5PM",
        "location": "UEES, San Salvador",
        "topics": ["FastAPI", "APIs", "Python"],
        "description": "Construye tu primera API moderna con FastAPI: rutas, validación con Pydantic, documentación automática y despliegue básico — todo en una sesión.",
        "speaker_name": "Emilio Serrano",
        "speaker_role": "Ingeniero de Software - Junior @ Core",
        "speaker_photo": "img/emilio-serrano.webp",
        "image": "img/uees-building-640.webp",
        # TODO: agregar "link" y "link_text" cuando el evento se publique en Meetup
    },
    {
        "title": "Procesamiento de datos con Pandas",
        "month": "AGO",
        "year": "2026",
        "day": 22,
        "date_display": "Sábado 22 de agosto, 2PM–5PM",
        "location": "TBD",
        "topics": ["Pandas", "Análisis de datos", "Python"],
        "description": "Aprende a limpiar, transformar y analizar datos reales con Pandas: DataFrames, groupby, merges y visualización rápida — con demo en vivo.",
        "speaker_name": "Kevin Turcios",
        "speaker_role": "CEO & Founder @ Core",
        "speaker_photo": "img/kevin-turcios.webp",
        "image": "img/uees-building-640.webp",
        # TODO: agregar "link" y "link_text" cuando el evento se publique en Meetup
    },
    {
        "title": "Web Scraping en Python: Un Arsenal de Herramientas para la Extracción de Datos",
        "month": "SEP",
        "year": "2026",
        "day": 19,
        "date_display": "Sábado 19 de septiembre, 2PM–5PM",
        "location": "TBD",
        "topics": ["Web scraping", "Extracción de datos", "Python"],
        "description": "Domina las principales herramientas de web scraping en Python: requests, BeautifulSoup, Scrapy y Playwright — con ejemplos prácticos para extraer datos de sitios reales.",
        "speaker_name": "Demetrio Reyes",
        "speaker_role": "Desarrollador fullstack · Python · Nodejs · Rust · Automatización con IA",
        "speaker_photo": "img/demetrio-reyes.webp",
        "image": "img/uees-building-640.webp",
        # TODO: agregar "link" y "link_text" cuando el evento se publique en Meetup
    },
]


@router.get("/propuestas", response_class=HTMLResponse)
async def proposals(request: Request) -> Response:
    return _serve_cached(request, "propuestas")


@router.get("/calendario", response_class=HTMLResponse)
async def calendar(request: Request) -> Response:
    return _serve_cached(request, "calendario")
