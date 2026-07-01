from __future__ import annotations

from unittest.mock import patch

import pytest
from fastapi import HTTPException
from httpx import ASGITransport, AsyncClient

from python_sv.config import Settings


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
    import python_sv.routers.pages as pages_mod

    custom = Settings(base_url="https://custom.example.com")
    custom_robots = f"User-agent: *\nAllow: /\nSitemap: {custom.base_url}/sitemap.xml\n"
    original = pages_mod._ROBOTS_TXT
    pages_mod._ROBOTS_TXT = custom_robots
    try:
        resp = await client.get("/robots.txt")
        assert "https://custom.example.com" in resp.text
    finally:
        pages_mod._ROBOTS_TXT = original


@pytest.mark.anyio
async def test_static_cache_header(client):
    resp = await client.get("/static/css/pysv.css")
    assert resp.headers["cache-control"] == "public, max-age=31536000, immutable"


@pytest.mark.anyio
async def test_code_of_conduct_renders(client):
    resp = await client.get("/codigo-de-conducta")
    assert resp.status_code == 200


@pytest.mark.anyio
async def test_calendar_renders(client):
    resp = await client.get("/calendario")
    assert resp.status_code == 200
    assert "JUL" in resp.text
    assert "Procesamiento de imágenes con OpenCV" not in resp.text


@pytest.mark.anyio
async def test_non_http_scope_passthrough(app):
    received: dict[str, object] = {}

    async def mock_app(scope, receive, send):
        received["scope"] = scope

    from python_sv.main import SecurityHeadersMiddleware

    mw = SecurityHeadersMiddleware(mock_app)
    await mw({"type": "websocket"}, None, None)
    assert received["scope"]["type"] == "websocket"


@pytest.mark.anyio
async def test_non_404_http_exception(app, client):
    async def raise_405():
        raise HTTPException(status_code=405, detail="Method Not Allowed")

    app.add_api_route("/test-405", raise_405)
    resp = await client.get("/test-405")
    assert resp.status_code == 405


@pytest.fixture
async def lenient_client(app):
    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://localhost") as ac:
        yield ac


@pytest.mark.anyio
async def test_unhandled_exception_returns_500(app, lenient_client):
    async def raise_unhandled():
        raise RuntimeError("boom")

    app.add_api_route("/test-500", raise_unhandled)
    resp = await lenient_client.get("/test-500")
    assert resp.status_code == 500
    assert "pythonsv.com" in resp.text


@pytest.mark.anyio
async def test_unhandled_exception_fallback(app, lenient_client):
    async def raise_unhandled():
        raise RuntimeError("boom")

    app.add_api_route("/test-fallback", raise_unhandled)
    with patch("python_sv.main.render_error", side_effect=Exception("render failed")):
        resp = await lenient_client.get("/test-fallback")
    assert resp.status_code == 500
    assert resp.text == "Internal Server Error"
