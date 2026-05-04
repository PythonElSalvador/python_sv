from __future__ import annotations

import types

import httpx as httpx_lib
import pytest
from aiohttp import ClientSession, TCPConnector

from python_sv.http import (
    HttpClients,
    create_aio_session,
    create_httpx_client,
    get_http,
)


@pytest.mark.anyio
async def test_create_aio_session_connector():
    async with create_aio_session() as session:
        assert isinstance(session, ClientSession)
        assert isinstance(session.connector, TCPConnector)
        assert session.connector.limit == 200
        assert session.connector.limit_per_host == 30


@pytest.mark.anyio
async def test_create_aio_session_timeout():
    async with create_aio_session() as session:
        assert session.timeout.total == 30
        assert session.timeout.connect == 5
        assert session.timeout.sock_connect == 3
        assert session.timeout.sock_read == 10


@pytest.mark.anyio
async def test_create_httpx_client_transport():
    async with create_httpx_client() as client:
        assert isinstance(client, httpx_lib.AsyncClient)
        assert isinstance(client._transport, httpx_lib.AsyncHTTPTransport)


@pytest.mark.anyio
async def test_create_httpx_client_timeout():
    async with create_httpx_client() as client:
        assert client.timeout.connect == 5.0
        assert client.timeout.read == 30.0
        assert client.timeout.write == 10.0
        assert client.timeout.pool == 10.0


def test_get_http():
    sentinel = HttpClients(aio=object(), httpx=object())  # type: ignore[arg-type]
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
        assert isinstance(clients.httpx, httpx_lib.AsyncClient)
        assert not clients.aio.closed
        assert not clients.httpx.is_closed

    assert clients.aio.closed
    assert clients.httpx.is_closed
