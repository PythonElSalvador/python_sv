from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from python_sv.dependencies import page_content
from python_sv.main import _page_cache, _prerender_pages, create_app, templates
from python_sv.routers.pages import cache_html_bytes


@pytest.fixture
def app():
    page_content.setdefault("title", "Python SV")
    page_content.setdefault("body", "<p>Test</p>")
    templates.env.globals.setdefault("static_url", lambda path: f"/static/{path}")
    application = create_app()
    _prerender_pages(application)
    cache_html_bytes(_page_cache)
    return application


@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://localhost") as ac:
        yield ac
