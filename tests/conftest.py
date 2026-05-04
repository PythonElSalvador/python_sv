from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from python_sv.dependencies import page_content
from python_sv.main import create_app


@pytest.fixture
def app():
    page_content.setdefault("title", "Python SV")
    page_content.setdefault("body", "<p>Test</p>")
    return create_app()


@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://localhost") as ac:
        yield ac
