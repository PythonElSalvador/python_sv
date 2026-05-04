from __future__ import annotations

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from python_sv.dependencies import page_content
from python_sv.main import _page_cache, _prerender_pages, create_app
from python_sv.routers.pages import cache_html_bytes


@pytest_asyncio.fixture
async def bench_client():
    page_content.setdefault("title", "Python SV")
    page_content.setdefault("body", "<p>Benchmarks</p>")
    app = create_app()
    _prerender_pages(app)
    cache_html_bytes(_page_cache)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://localhost") as ac:
        yield ac
