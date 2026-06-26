"""
Tests for Rate Limiting and Security Hardening
"""
import pytest
import asyncio
from backend.websocket_manager import ConnectionManager
from unittest.mock import Mock, patch

def test_websocket_rate_limiting():
    manager = ConnectionManager()
    manager.rate_limit = 5
    client_id = "test_client"

    # Send 5 messages - should be allowed
    for _ in range(5):
        assert manager.check_rate_limit(client_id) is True

    # 6th message should be blocked
    assert manager.check_rate_limit(client_id) is False

def test_graphql_security_config():
    import os
    with patch.dict(os.environ, {"ENV": "production"}):
        # Reloading module to apply env change if it was already loaded
        import importlib
        import backend.graphql_layer
        importlib.reload(backend.graphql_layer)

        from backend.graphql_layer import graphql_router
        assert graphql_router.graphql_ide is None
