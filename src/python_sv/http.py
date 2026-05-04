from __future__ import annotations

from typing import TYPE_CHECKING

import attrs
from aiohttp import ClientSession
from httpx import AsyncClient

if TYPE_CHECKING:
    from fastapi import Request


@attrs.define
class HttpClients:
    aio: ClientSession
    httpx: AsyncClient


def get_http(request: Request) -> HttpClients:
    clients: HttpClients = request.app.state.http
    return clients
