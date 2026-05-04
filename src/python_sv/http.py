from __future__ import annotations

import socket
from typing import TYPE_CHECKING

import attrs
import httpx
from aiohttp import ClientSession, ClientTimeout, TCPConnector

if TYPE_CHECKING:
    from fastapi import Request


@attrs.define
class HttpClients:
    aio: ClientSession
    httpx: httpx.AsyncClient


def create_aio_session() -> ClientSession:
    connector = TCPConnector(
        limit=0,
        limit_per_host=30,
        ttl_dns_cache=300,
        use_dns_cache=True,
        enable_cleanup_closed=True,
        keepalive_timeout=30,
    )
    timeout = ClientTimeout(
        total=30,
        connect=5,
        sock_connect=3,
        sock_read=10,
    )
    return ClientSession(
        connector=connector,
        timeout=timeout,
        read_bufsize=2**18,
    )


def create_httpx_client() -> httpx.AsyncClient:
    transport = httpx.AsyncHTTPTransport(
        http1=False,
        http2=True,
        socket_options=[
            (socket.IPPROTO_TCP, socket.TCP_NODELAY, 1),
        ],
    )
    limits = httpx.Limits(
        max_connections=100,
        max_keepalive_connections=50,
        keepalive_expiry=30,
    )
    timeout = httpx.Timeout(
        connect=5.0,
        read=30.0,
        write=10.0,
        pool=10.0,
    )
    return httpx.AsyncClient(
        transport=transport,
        limits=limits,
        timeout=timeout,
    )


def get_http(request: Request) -> HttpClients:
    clients: HttpClients = request.app.state.http
    return clients
