from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from python_sv.main import create_app


VALID_FORM = {
    "name": "Ana García",
    "email": "ana@example.com",
    "city": "San Salvador",
    "member_type": "student",
    "role": "backend",
}


@pytest.fixture
def signup_app():
    application = create_app()
    application.state.db = AsyncMock()
    return application


@pytest.fixture
async def signup_client(signup_app):
    transport = ASGITransport(app=signup_app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://localhost") as ac:
        yield ac


@pytest.mark.anyio
async def test_successful_signup(signup_client):
    with patch("python_sv.routers.signup.notify_signup"):
        resp = await signup_client.post("/api/signup", data=VALID_FORM)

    assert resp.status_code == 200
    assert "ya estás en la lista" in resp.text
    app = signup_client._transport.app
    app.state.db.signups.insert_one.assert_awaited_once()


@pytest.mark.anyio
async def test_duplicate_email(signup_client):
    app = signup_client._transport.app
    app.state.db.signups.insert_one.side_effect = Exception(
        "E11000 duplicate key error collection"
    )

    resp = await signup_client.post("/api/signup", data=VALID_FORM)

    assert resp.status_code == 200
    assert "ya está en la lista" in resp.text


@pytest.mark.anyio
async def test_validation_error_invalid_email(signup_client):
    bad_form = {**VALID_FORM, "email": "not-valid"}

    resp = await signup_client.post("/api/signup", data=bad_form)

    assert resp.status_code == 422
    assert "revisa que todos los campos" in resp.text


@pytest.mark.anyio
async def test_db_unavailable(signup_client):
    app = signup_client._transport.app
    app.state.db = None

    resp = await signup_client.post("/api/signup", data=VALID_FORM)

    assert resp.status_code == 503
    assert "pysv-form-error" in resp.text


@pytest.mark.anyio
async def test_db_insert_failure_non_duplicate(signup_client):
    app = signup_client._transport.app
    app.state.db.signups.insert_one.side_effect = Exception("connection timeout")

    resp = await signup_client.post("/api/signup", data=VALID_FORM)

    assert resp.status_code == 500
    assert "pysv-form-error" in resp.text
