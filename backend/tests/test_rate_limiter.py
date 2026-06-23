import pytest
import time
from rate_limiter import RateLimiter, RateLimitConfig

def test_rate_limit_config():
    # Test default limit for guest
    assert RateLimitConfig.get_limit("default", "guest") == 50
    # Test admin multiplier
    assert RateLimitConfig.get_limit("default", "admin") == 500
    # Test specific endpoint
    assert RateLimitConfig.get_limit("auth", "operator") == 5

@pytest.mark.skipif(not RateLimiter().connected, reason="Redis not available")
def test_rate_limiter_logic():
    rl = RateLimiter()
    key = "test_user_123"
    rl.reset(key)

    # First 3 requests should pass
    limit = 3
    for i in range(limit):
        is_limited, info = rl.is_rate_limited(key, limit=limit, window_seconds=10)
        assert is_limited is False
        assert info["remaining"] == limit - (i + 1)

    # 4th request should be limited
    is_limited, info = rl.is_rate_limited(key, limit=limit, window_seconds=10)
    assert is_limited is True
    assert info["remaining"] == 0
    assert info["reset_in"] > 0

    # Reset and should pass again
    rl.reset(key)
    is_limited, info = rl.is_rate_limited(key, limit=limit, window_seconds=10)
    assert is_limited is False
