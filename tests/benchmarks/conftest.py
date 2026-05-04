from __future__ import annotations

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from python_sv.dependencies import page_content
from python_sv.main import _prerender_pages, create_app


@pytest_asyncio.fixture
async def bench_client():
    page_content.setdefault("title", "Python SV")
    page_content.setdefault("body", "<p>Benchmarks</p>")
    app = create_app()
    _prerender_pages(app)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://localhost") as ac:
        yield ac
