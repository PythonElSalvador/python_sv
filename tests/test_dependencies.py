from __future__ import annotations

from app.dependencies import context_processor


class FakeState:
    csp_nonce = "test-nonce"


class FakeRequest:
    state = FakeState()


def test_context_processor_returns_nonce():
    ctx = context_processor(FakeRequest())
    assert ctx["csp_nonce"] == "test-nonce"


def test_context_processor_returns_current_year():
    ctx = context_processor(FakeRequest())
    assert isinstance(ctx["current_year"], int)
    assert ctx["current_year"] >= 2025
