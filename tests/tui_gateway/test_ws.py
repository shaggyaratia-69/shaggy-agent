import asyncio

import pytest

from tui_gateway.ws import _is_disconnected_runtime_error, handle_ws


class FakeDisconnectedRuntimeWS:
    def __init__(self):
        self.accepted = False
        self.closed = False
        self.sent = []

    async def accept(self):
        self.accepted = True

    async def send_text(self, line: str):
        self.sent.append(line)

    async def receive_text(self):
        raise RuntimeError("WebSocket is not connected. Need to call 'accept' first.")

    async def close(self):
        self.closed = True


class FakeUnexpectedRuntimeWS(FakeDisconnectedRuntimeWS):
    async def receive_text(self):
        raise RuntimeError("boom")


def test_disconnected_runtime_error_detection():
    assert _is_disconnected_runtime_error(RuntimeError("WebSocket is not connected"))
    assert not _is_disconnected_runtime_error(RuntimeError("boom"))


def test_handle_ws_treats_starlette_not_connected_runtime_error_as_disconnect():
    ws = FakeDisconnectedRuntimeWS()

    asyncio.run(handle_ws(ws))

    assert ws.accepted is True
    assert ws.closed is True
    assert any('gateway.ready' in line for line in ws.sent)


def test_handle_ws_reraises_unexpected_runtime_error():
    ws = FakeUnexpectedRuntimeWS()

    with pytest.raises(RuntimeError, match="boom"):
        asyncio.run(handle_ws(ws))

    assert ws.closed is True
