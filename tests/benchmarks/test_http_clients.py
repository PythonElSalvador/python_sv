from __future__ import annotations

import types

import pytest
from aiohttp import ClientSession
from httpx import AsyncClient

from python_sv.http import (
    HttpClients,
    create_aio_session,
    create_httpx_client,
    get_http,
)
from python_sv.main import create_app, lifespan


@pytest.mark.asyncio
async def test_bench_create_aio_session(async_benchmark):
    async def create_and_close():
        async with create_aio_session() as session:
            assert isinstance(session, ClientSession)

    await async_benchmark(create_and_close, rounds=10, iterations=20)


@pytest.mark.asyncio
async def test_bench_create_httpx_client(async_benchmark):
    async def create_and_close():
        async with create_httpx_client() as client:
            assert isinstance(client, AsyncClient)

    await async_benchmark(create_and_close, rounds=10, iterations=20)


@pytest.mark.asyncio
async def test_bench_lifespan_cycle(async_benchmark):
    async def cycle():
        app = create_app()
        async with lifespan(app):
            assert not app.state.http.aio.closed
            assert not app.state.http.httpx_client.is_closed

    await async_benchmark(cycle, rounds=5, iterations=5)


@pytest.mark.asyncio
async def test_bench_get_http_dependency(async_benchmark):
    sentinel = HttpClients(aio=object(), httpx_client=object())  # type: ignore[arg-type]
    request = types.SimpleNamespace(
        app=types.SimpleNamespace(state=types.SimpleNamespace(http=sentinel))
    )

    async def resolve():
        result = get_http(request)  # type: ignore[arg-type]
        assert result is sentinel

    await async_benchmark(resolve, rounds=10, iterations=100)
