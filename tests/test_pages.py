from __future__ import annotations

import pytest

from app.config import Settings, get_settings
from app.dependencies import new_csrf_token
from app.main import app


@pytest.mark.anyio
async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


@pytest.mark.anyio
async def test_home_renders(client):
    resp = await client.get("/")
    assert resp.status_code == 200
    assert "Python SV" in resp.text
    assert "csp_nonce" not in resp.text or "nonce-" in resp.text


@pytest.mark.anyio
async def test_home_has_csrf_token(client):
    resp = await client.get("/")
    assert 'name="csrf_token"' in resp.text


@pytest.mark.anyio
async def test_robots_txt(client):
    resp = await client.get("/robots.txt")
    assert resp.status_code == 200
    assert "User-agent: *" in resp.text
    assert "Sitemap:" in resp.text


@pytest.mark.anyio
async def test_sitemap_xml(client):
    resp = await client.get("/sitemap.xml")
    assert resp.status_code == 200
    assert "<urlset" in resp.text


@pytest.mark.anyio
async def test_404_returns_error_page(client):
    resp = await client.get("/nonexistent")
    assert resp.status_code == 404
    assert "Page not found" in resp.text


@pytest.mark.anyio
async def test_security_headers(client):
    resp = await client.get("/health")
    assert resp.headers["x-content-type-options"] == "nosniff"
    assert resp.headers["x-frame-options"] == "DENY"
    assert "content-security-policy" in resp.headers


@pytest.mark.anyio
async def test_signup_success(client):
    token = new_csrf_token()
    resp = await client.post(
        "/signups",
        data={
            "name": "Test User",
            "email": "test@example.com",
            "city": "San Salvador",
            "member_type": "individual",
            "role": "attend",
            "csrf_token": token,
        },
    )
    assert resp.status_code == 200
    assert "Test User" in resp.text


@pytest.mark.anyio
async def test_signup_bad_csrf(client):
    resp = await client.post(
        "/signups",
        data={
            "name": "Test",
            "email": "test@example.com",
            "city": "San Salvador",
            "member_type": "individual",
            "role": "attend",
            "csrf_token": "invalid",
        },
    )
    assert resp.status_code == 200
    assert "Session expired" in resp.text


@pytest.mark.anyio
async def test_signup_bad_email(client):
    token = new_csrf_token()
    resp = await client.post(
        "/signups",
        data={
            "name": "Test",
            "email": "not-an-email",
            "city": "San Salvador",
            "member_type": "student",
            "role": "attend",
            "csrf_token": token,
        },
    )
    assert resp.status_code == 200
    assert "Invalid email" in resp.text


@pytest.mark.anyio
async def test_signup_other_city_required(client):
    token = new_csrf_token()
    resp = await client.post(
        "/signups",
        data={
            "name": "Test",
            "email": "test@example.com",
            "city": "Other",
            "member_type": "individual",
            "role": "attend",
            "other_city": "",
            "csrf_token": token,
        },
    )
    assert resp.status_code == 200
    assert "specify your city" in resp.text


@pytest.mark.anyio
async def test_signup_duplicate_email(client):
    token = new_csrf_token()
    data = {
        "name": "Test User",
        "email": "dupe@example.com",
        "city": "San Salvador",
        "member_type": "company",
        "role": "attend",
        "csrf_token": token,
    }
    resp = await client.post("/signups", data=data)
    assert resp.status_code == 200
    assert "Test User" in resp.text

    token2 = new_csrf_token()
    data["csrf_token"] = token2
    resp = await client.post("/signups", data=data)
    assert resp.status_code == 200
    assert "ya está en la lista" in resp.text


@pytest.mark.anyio
async def test_settings_override(client):
    custom = Settings(base_url="https://custom.example.com")
    app.dependency_overrides[get_settings] = lambda: custom
    try:
        resp = await client.get("/robots.txt")
        assert "https://custom.example.com" in resp.text
    finally:
        app.dependency_overrides.clear()
