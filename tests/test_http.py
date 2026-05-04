from __future__ import annotations

import types

import httpx as httpx_lib
import pytest
from aiohttp import ClientSession

from python_sv.http import (
    HttpClients,
    create_aio_session,
    create_httpx_client,
    get_http,
)


@pytest.mark.anyio
async def test_aio_session_usable():
    async with create_aio_session() as session:
        assert isinstance(session, ClientSession)
        assert not session.closed


@pytest.mark.anyio
async def test_httpx_client_supports_http2():
    async with create_httpx_client() as client:
        assert isinstance(client, httpx_lib.AsyncClient)
        assert not client.is_closed


def test_get_http():
    sentinel = HttpClients(aio=object(), httpx_client=object())  # type: ignore[arg-type]
    request = types.SimpleNamespace(
        app=types.SimpleNamespace(state=types.SimpleNamespace(http=sentinel))
    )
    assert get_http(request) is sentinel  # type: ignore[arg-type]


@pytest.mark.anyio
async def test_lifespan_manages_http_clients():
    from python_sv.main import create_app, lifespan

    app = create_app()
    async with lifespan(app):
        clients = app.state.http
        assert isinstance(clients, HttpClients)
        assert isinstance(clients.aio, ClientSession)
        assert isinstance(clients.httpx_client, httpx_lib.AsyncClient)
        assert not clients.aio.closed
        assert not clients.httpx_client.is_closed

    assert clients.aio.closed
    assert clients.httpx_client.is_closed
