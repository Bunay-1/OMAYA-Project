import pytest
from unittest.mock import AsyncMock, MagicMock
from websocket_manager import ConnectionManager

@pytest.mark.asyncio
async def test_websocket_connect():
    manager = ConnectionManager()
    websocket = AsyncMock()

    await manager.connect(websocket)

    assert len(manager.active_connections) == 1
    assert websocket in manager.active_connections
    websocket.accept.assert_called_once()

@pytest.mark.asyncio
async def test_websocket_disconnect():
    manager = ConnectionManager()
    websocket = AsyncMock()

    await manager.connect(websocket)
    manager.disconnect(websocket)

    assert len(manager.active_connections) == 0

@pytest.mark.asyncio
async def test_websocket_broadcast():
    manager = ConnectionManager()
    ws1 = AsyncMock()
    ws2 = AsyncMock()

    await manager.connect(ws1)
    await manager.connect(ws2)

    message = {"type": "test_msg", "data": "hello"}
    await manager.broadcast(message)

    ws1.send_json.assert_called_with(message)
    ws2.send_json.assert_called_with(message)

@pytest.mark.asyncio
async def test_websocket_broadcast_cleanup():
    manager = ConnectionManager()
    ws1 = AsyncMock()
    ws2 = AsyncMock()
    ws2.send_json.side_effect = Exception("Connection closed")

    await manager.connect(ws1)
    await manager.connect(ws2)

    await manager.broadcast({"msg": "test"})

    # ws2 should have been removed
    assert len(manager.active_connections) == 1
    assert ws1 in manager.active_connections
    assert ws2 not in manager.active_connections
