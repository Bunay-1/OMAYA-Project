"""
Rate Limiting Module
Redis-based request throttling
"""
import redis
import time
import os
import logging
from typing import Optional
from functools import wraps

logger = logging.getLogger(__name__)

class RateLimiter:
    """Redis-based rate limiter"""
    
    def __init__(self):
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", 6379))
        
        try:
            self.client = redis.Redis(
                host=redis_host,
                port=redis_port,
                decode_responses=True
            )
            self.client.ping()
            logger.info(f"✅ Redis rate limiter connected: {redis_host}:{redis_port}")
            self.connected = True
        except Exception as e:
            logger.warning(f"⚠️  Rate limiter not available: {e}")
            self.client = None
            self.connected = False
    
    def is_rate_limited(
        self, 
        key: str, 
        limit: int = 100, 
        window_seconds: int = 60
    ) -> tuple[bool, dict]:
        """
        Check if request is rate limited
        
        Args:
            key: Unique identifier (e.g., username, IP address)
            limit: Maximum requests allowed
            window_seconds: Time window in seconds
            
        Returns:
            Tuple (is_limited, info_dict)
        """
        if not self.connected:
            return False, {"limited": False, "remaining": limit}
        
        try:
            redis_key = f"rate_limit:{key}"
            current = self.client.get(redis_key)
            
            if current is None:
                # First request in window
                self.client.setex(redis_key, window_seconds, 1)
                return False, {"limited": False, "remaining": limit - 1, "reset_in": window_seconds}
            
            current_count = int(current)
            
            if current_count >= limit:
                # Rate limit exceeded
                ttl = self.client.ttl(redis_key)
                return True, {
                    "limited": True,
                    "remaining": 0,
                    "reset_in": ttl,
                    "limit": limit
                }
            
            # Increment counter
            self.client.incr(redis_key)
            ttl = self.client.ttl(redis_key)
            
            return False, {
                "limited": False,
                "remaining": limit - (current_count + 1),
                "reset_in": ttl,
                "limit": limit
            }
            
        except Exception as e:
            logger.error(f"Rate limiter error: {e}")
            return False, {"limited": False, "remaining": limit}
    
    def reset(self, key: str):
        """Reset rate limit for key"""
        if self.connected:
            redis_key = f"rate_limit:{key}"
            self.client.delete(redis_key)

class RateLimitConfig:
    """Rate limit configurations for different endpoints"""
    
    # Endpoint-specific limits (requests per minute)
    LIMITS = {
        "default": 100,
        "predict": 30,
        "simulate": 10,
        "auth": 5,
        "export": 10,
        "health": 1000,  # Very high for monitoring
    }
    
    # Role-based limits
    ROLE_MULTIPLIERS = {
        "admin": 5.0,      # 5x limit
        "supervisor": 2.0,  # 2x limit
        "operator": 1.0,    # 1x limit
        "guest": 0.5       # 0.5x limit
    }
    
    @staticmethod
    def get_limit(endpoint: str, role: str = "guest") -> int:
        """Get rate limit for endpoint and role"""
        base_limit = RateLimitConfig.LIMITS.get(endpoint, RateLimitConfig.LIMITS["default"])
        multiplier = RateLimitConfig.ROLE_MULTIPLIERS.get(role, 1.0)
        return int(base_limit * multiplier)

# Singleton instance
rate_limiter = RateLimiter()

def rate_limit(endpoint: str = "default", window_seconds: int = 60):
    """Decorator for rate limiting endpoints"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Extract user identifier from context
            # In real implementation, extract from JWT token
            user_key = kwargs.get("current_user", "anonymous")
            
            limit = RateLimitConfig.get_limit(endpoint, user_key)
            is_limited, info = rate_limiter.is_rate_limited(
                f"{endpoint}:{user_key}",
                limit=limit,
                window_seconds=window_seconds
            )
            
            if is_limited:
                raise Exception(
                    f"Rate limit exceeded. Reset in {info['reset_in']} seconds"
                )
            
            return await func(*args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            user_key = kwargs.get("current_user", "anonymous")
            
            limit = RateLimitConfig.get_limit(endpoint, user_key)
            is_limited, info = rate_limiter.is_rate_limited(
                f"{endpoint}:{user_key}",
                limit=limit,
                window_seconds=window_seconds
            )
            
            if is_limited:
                raise Exception(
                    f"Rate limit exceeded. Reset in {info['reset_in']} seconds"
                )
            
            return func(*args, **kwargs)
        
        # Determine if async or sync
        if hasattr(func, '__code__') and func.__code__.co_flags & 0x100:
            return async_wrapper
        return sync_wrapper
    
    return decorator
