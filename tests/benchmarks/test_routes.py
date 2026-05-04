from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_bench_health(async_benchmark, bench_client):
    async def hit():
        resp = await bench_client.get("/health")
        assert resp.status_code == 200

    await async_benchmark(hit, rounds=10, iterations=50)


@pytest.mark.asyncio
async def test_bench_home(async_benchmark, bench_client):
    async def hit():
        resp = await bench_client.get("/")
        assert resp.status_code == 200

    await async_benchmark(hit, rounds=10, iterations=50)


@pytest.mark.asyncio
async def test_bench_robots_txt(async_benchmark, bench_client):
    async def hit():
        resp = await bench_client.get("/robots.txt")
        assert resp.status_code == 200

    await async_benchmark(hit, rounds=10, iterations=50)


@pytest.mark.asyncio
async def test_bench_sitemap_xml(async_benchmark, bench_client):
    async def hit():
        resp = await bench_client.get("/sitemap.xml")
        assert resp.status_code == 200

    await async_benchmark(hit, rounds=10, iterations=50)


@pytest.mark.asyncio
async def test_bench_calendar(async_benchmark, bench_client):
    async def hit():
        resp = await bench_client.get("/calendario")
        assert resp.status_code == 200

    await async_benchmark(hit, rounds=10, iterations=50)


@pytest.mark.asyncio
async def test_bench_code_of_conduct(async_benchmark, bench_client):
    async def hit():
        resp = await bench_client.get("/codigo-de-conducta")
        assert resp.status_code == 200

    await async_benchmark(hit, rounds=10, iterations=50)
