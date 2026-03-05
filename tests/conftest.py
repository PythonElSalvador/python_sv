from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient
from mongomock_motor import AsyncMongoMockClient

import app.dependencies as deps
from app.dependencies import page_content, rate_limits
from app.main import app


@pytest.fixture
async def client():
    mock_client = AsyncMongoMockClient()
    deps.mongo_client = mock_client
    deps.db = mock_client["pythonsv_test"]
    await deps.db.signups.create_index("email", unique=True)

    page_content.setdefault("title", "Python SV")
    page_content.setdefault("body", "<p>Test</p>")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://localhost") as ac:
        yield ac

    await deps.db.signups.drop()
    deps.db = None  # type: ignore[assignment]
    deps.mongo_client = None  # type: ignore[assignment]


@pytest.fixture(autouse=True)
def clear_rate_limits():
    rate_limits.clear()
