from __future__ import annotations

import pytest

from python_sv.config import Settings, get_settings
from python_sv.main import app


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
    assert "no existe" in resp.text


@pytest.mark.anyio
async def test_security_headers(client):
    resp = await client.get("/health")
    assert resp.headers["x-content-type-options"] == "nosniff"
    assert resp.headers["x-frame-options"] == "DENY"
    assert "content-security-policy" in resp.headers


@pytest.mark.anyio
async def test_settings_override(client):
    custom = Settings(base_url="https://custom.example.com")
    app.dependency_overrides[get_settings] = lambda: custom
    try:
        resp = await client.get("/robots.txt")
        assert "https://custom.example.com" in resp.text
    finally:
        app.dependency_overrides.clear()
