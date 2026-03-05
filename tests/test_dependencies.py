from __future__ import annotations

import time

from app.dependencies import (
    RATE_MAX,
    check_rate_limit,
    new_csrf_token,
    verify_csrf_token,
)


def test_csrf_token_roundtrip():
    token = new_csrf_token()
    assert verify_csrf_token(token)


def test_csrf_token_rejects_garbage():
    assert not verify_csrf_token("")
    assert not verify_csrf_token("not.valid")
    assert not verify_csrf_token("abc")


def test_csrf_token_rejects_expired(monkeypatch):
    token = new_csrf_token()
    original_time = time.time()
    monkeypatch.setattr(time, "time", lambda: original_time + 7200)
    assert not verify_csrf_token(token)


def test_rate_limit_allows_under_max():
    for _ in range(RATE_MAX):
        assert check_rate_limit("1.2.3.4")


def test_rate_limit_blocks_over_max():
    for _ in range(RATE_MAX):
        check_rate_limit("5.6.7.8")
    assert not check_rate_limit("5.6.7.8")


def test_rate_limit_independent_per_ip():
    for _ in range(RATE_MAX):
        check_rate_limit("10.0.0.1")
    assert check_rate_limit("10.0.0.2")
