from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from app.dependencies import page_content
from app.main import app


@pytest.fixture
async def client():
    page_content.setdefault("title", "Python SV")
    page_content.setdefault("body", "<p>Test</p>")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://localhost") as ac:
        yield ac
