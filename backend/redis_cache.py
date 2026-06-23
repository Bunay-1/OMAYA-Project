"""
Redis Cache Layer
Real-time caching for machine states and metrics
"""
import redis
import json
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import os

class RedisCache:
    def __init__(self):
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", 6379))
        redis_db = int(os.getenv("REDIS_DB", 0))
        
        try:
            self.client = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                decode_responses=True
            )
            self.client.ping()
            print(f"✅ Redis connected: {redis_host}:{redis_port}")
        except redis.ConnectionError:
            print("⚠️  Redis not available, running without cache")
            self.client = None
    
    def set(self, key: str, value: Any, ttl_seconds: int = 300):
        """Set value with TTL (default 5 minutes)"""
        if not self.client:
            return False
        
        try:
            serialized = json.dumps(value)
            self.client.setex(key, ttl_seconds, serialized)
            return True
        except Exception as e:
            print(f"Redis SET error: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.client:
            return None
        
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Redis GET error: {e}")
            return None
    
    def delete(self, key: str):
        """Delete key from cache"""
        if not self.client:
            return False
        
        try:
            self.client.delete(key)
            return True
        except Exception as e:
            print(f"Redis DELETE error: {e}")
            return False
    
    def set_machine_state(self, machine_id: str, state: Dict):
        """Cache machine state"""
        key = f"machine:{machine_id}:state"
        state["cached_at"] = datetime.now().isoformat()
        return self.set(key, state, ttl_seconds=60)
    
    def get_machine_state(self, machine_id: str) -> Optional[Dict]:
        """Get cached machine state"""
        key = f"machine:{machine_id}:state"
        return self.get(key)
    
    def set_kpi_data(self, kpi_data: Dict):
        """Cache KPI data"""
        key = "kpi:fleet"
        return self.set(key, kpi_data, ttl_seconds=30)
    
    def get_kpi_data(self) -> Optional[Dict]:
        """Get cached KPI data"""
        key = "kpi:fleet"
        return self.get(key)
    
    def increment_metric(self, metric_name: str) -> int:
        """Increment a metric counter"""
        if not self.client:
            return 0
        
        try:
            key = f"metric:{metric_name}"
            return self.client.incr(key)
        except Exception as e:
            print(f"Redis INCR error: {e}")
            return 0
    
    def get_metric(self, metric_name: str) -> int:
        """Get metric value"""
        if not self.client:
            return 0
        
        try:
            key = f"metric:{metric_name}"
            value = self.client.get(key)
            return int(value) if value else 0
        except Exception as e:
            print(f"Redis GET metric error: {e}")
            return 0

# Singleton instance
cache = RedisCache()
