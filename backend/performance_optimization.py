"""
Performance Optimization Module for OMAYA Platform
Caching, connection pooling, and query optimization
"""
from typing import Dict, Any, Optional, List, Callable
import logging
import asyncio
import time
from functools import wraps
from datetime import datetime, timedelta
from dataclasses import dataclass
import redis
import psycopg2
from psycopg2 import pool
import json
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class CacheStats:
    """Cache statistics."""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    
    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0


class RedisCache:
    """Redis-based caching with TTL support."""
    
    def __init__(self, redis_client: redis.Redis, default_ttl: int = 3600):
        """
        Initialize Redis cache.
        
        Args:
            redis_client: Redis client instance
            default_ttl: Default time-to-live in seconds
        """
        self.redis = redis_client
        self.default_ttl = default_ttl
        self.stats = CacheStats()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None
        """
        try:
            value = self.redis.get(key)
            if value is not None:
                self.stats.hits += 1
                return json.loads(value)
            else:
                self.stats.misses += 1
                return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            self.stats.misses += 1
            return None
    
    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds
            
        Returns:
            True on success, False on error
        """
        try:
            serialized = json.dumps(value)
            ttl = ttl or self.default_ttl
            self.redis.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            self.redis.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate all keys matching pattern.
        
        Args:
            pattern: Key pattern (e.g., "machine:*")
            
        Returns:
            Number of keys deleted
        """
        try:
            keys = self.redis.keys(pattern)
            if keys:
                return self.redis.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache pattern invalidation error: {e}")
            return 0
    
    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        return self.stats
    
    def clear_stats(self):
        """Clear cache statistics."""
        self.stats = CacheStats()


class QueryCache:
    """Query result caching for database queries."""
    
    def __init__(self, cache: RedisCache):
        self.cache = cache
    
    def _generate_key(self, query: str, params: tuple = ()) -> str:
        """Generate cache key from query and parameters."""
        key_data = f"{query}:{params}"
        return f"query:{hashlib.sha256(key_data.encode()).hexdigest()}"
    
    def get(self, query: str, params: tuple = ()) -> Optional[List[Dict[str, Any]]]:
        """Get cached query result."""
        key = self._generate_key(query, params)
        return self.cache.get(key)
    
    def set(self, query: str, result: List[Dict[str, Any]], 
            params: tuple = (), ttl: int = 300) -> bool:
        """Cache query result."""
        key = self._generate_key(query, params)
        return self.cache.set(key, result, ttl)
    
    def invalidate(self, table: str):
        """Invalidate all cached queries for a table."""
        pattern = f"query:*{table}*"
        return self.cache.invalidate_pattern(pattern)


class ConnectionPool:
    """Database connection pool manager."""
    
    def __init__(self, host: str, port: int, database: str, 
                 user: str, password: str, min_conn: int = 2, 
                 max_conn: int = 20):
        """
        Initialize connection pool.
        
        Args:
            host: Database host
            port: Database port
            database: Database name
            user: Database user
            password: Database password
            min_conn: Minimum connections
            max_conn: Maximum connections
        """
        self.pool = psycopg2.pool.ThreadedConnectionPool(
            minconn=min_conn,
            maxconn=max_conn,
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        logger.info(f"Connection pool initialized: {min_conn}-{max_conn} connections")
    
    def get_connection(self):
        """Get connection from pool."""
        return self.pool.getconn()
    
    def return_connection(self, conn):
        """Return connection to pool."""
        self.pool.putconn(conn)
    
    def close_all(self):
        """Close all connections in pool."""
        self.pool.closeall()
        logger.info("Connection pool closed")


class AsyncConnectionPool:
    """Async database connection pool."""
    
    def __init__(self, dsn: str, min_size: int = 2, max_size: int = 20):
        """
        Initialize async connection pool.
        
        Args:
            dsn: Database connection string
            min_size: Minimum pool size
            max_size: Maximum pool size
        """
        self.dsn = dsn
        self.min_size = min_size
        self.max_size = max_size
        self.pool = None
    
    async def initialize(self):
        """Initialize async pool."""
        try:
            import asyncpg
            self.pool = await asyncpg.create_pool(
                self.dsn,
                min_size=self.min_size,
                max_size=self.max_size
            )
            logger.info(f"Async connection pool initialized: {self.min_size}-{self.max_size}")
        except Exception as e:
            logger.error(f"Failed to initialize async pool: {e}")
            raise
    
    async def acquire(self):
        """Acquire connection from pool."""
        return self.pool.acquire()
    
    async def close(self):
        """Close connection pool."""
        await self.pool.close()
        logger.info("Async connection pool closed")


def async_cache(ttl: int = 300, key_prefix: str = ""):
    """
    Decorator for async function caching.
    
    Args:
        ttl: Time-to-live in seconds
        key_prefix: Prefix for cache keys
    """
    def decorator(func):
        _cache = {}
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            key_data = f"{key_prefix}:{args}:{kwargs}"
            cache_key = hashlib.sha256(str(key_data).encode()).hexdigest()
            
            # Check cache
            if cache_key in _cache:
                cached_item = _cache[cache_key]
                if time.time() - cached_item['timestamp'] < ttl:
                    return cached_item['value']
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache result
            _cache[cache_key] = {
                'value': result,
                'timestamp': time.time()
            }
            
            return result
        
        return wrapper
    return decorator


def sync_cache(ttl: int = 300, key_prefix: str = ""):
    """
    Decorator for synchronous function caching.
    
    Args:
        ttl: Time-to-live in seconds
        key_prefix: Prefix for cache keys
    """
    def decorator(func):
        _cache = {}
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            key_data = f"{key_prefix}:{args}:{kwargs}"
            cache_key = hashlib.sha256(str(key_data).encode()).hexdigest()
            
            # Check cache
            if cache_key in _cache:
                cached_item = _cache[cache_key]
                if time.time() - cached_item['timestamp'] < ttl:
                    return cached_item['value']
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Cache result
            _cache[cache_key] = {
                'value': result,
                'timestamp': time.time()
            }
            
            return result
        
        return wrapper
    return decorator


class PerformanceMonitor:
    """Performance monitoring and metrics collection."""
    
    def __init__(self):
        self.metrics: Dict[str, List[float]] = {}
        self.lock = asyncio.Lock()
    
    async def record_metric(self, name: str, value: float):
        """Record a metric value."""
        async with self.lock:
            if name not in self.metrics:
                self.metrics[name] = []
            self.metrics[name].append(value)
            
            # Keep only last 1000 values
            if len(self.metrics[name]) > 1000:
                self.metrics[name] = self.metrics[name][-1000:]
    
    def get_metric_stats(self, name: str) -> Optional[Dict[str, float]]:
        """Get statistics for a metric."""
        if name not in self.metrics or not self.metrics[name]:
            return None
        
        values = self.metrics[name]
        return {
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values),
            'median': sorted(values)[len(values) // 2]
        }
    
    def get_all_metrics(self) -> Dict[str, Dict[str, float]]:
        """Get statistics for all metrics."""
        return {name: self.get_metric_stats(name) 
                for name in self.metrics.keys()}


def monitor_performance(metric_name: str):
    """
    Decorator to monitor function performance.
    
    Args:
        metric_name: Name for the performance metric
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                # Record metric (would need monitor instance)
                logger.debug(f"{metric_name} took {duration:.3f}s")
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                logger.debug(f"{metric_name} took {duration:.3f}s")
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


class BatchProcessor:
    """Batch processing for bulk operations."""
    
    def __init__(self, batch_size: int = 100, max_delay: float = 1.0):
        """
        Initialize batch processor.
        
        Args:
            batch_size: Maximum batch size
            max_delay: Maximum delay before processing
        """
        self.batch_size = batch_size
        self.max_delay = max_delay
        self.queue: List[Any] = []
        self.last_process_time = time.time()
    
    def add(self, item: Any) -> bool:
        """
        Add item to batch.
        
        Args:
            item: Item to add
            
        Returns:
            True if batch should be processed
        """
        self.queue.append(item)
        
        should_process = (
            len(self.queue) >= self.batch_size or
            time.time() - self.last_process_time >= self.max_delay
        )
        
        if should_process:
            self.last_process_time = time.time()
        
        return should_process
    
    def get_batch(self) -> List[Any]:
        """Get and clear current batch."""
        batch = self.queue.copy()
        self.queue.clear()
        return batch
    
    def flush(self) -> List[Any]:
        """Flush all pending items."""
        return self.get_batch()


class DataLoader:
    """Efficient data loading with pagination and caching."""
    
    def __init__(self, cache: RedisCache, page_size: int = 100):
        """
        Initialize data loader.
        
        Args:
            cache: Redis cache instance
            page_size: Default page size
        """
        self.cache = cache
        self.page_size = page_size
    
    async def load_page(self, key: str, page: int, 
                        loader_func: Callable) -> List[Dict[str, Any]]:
        """
        Load a page of data with caching.
        
        Args:
            key: Cache key prefix
            page: Page number
            loader_func: Function to load data
            
        Returns:
            Page of data
        """
        cache_key = f"{key}:page:{page}"
        
        # Try cache first
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached
        
        # Load from source
        offset = page * self.page_size
        data = await loader_func(offset=offset, limit=self.page_size)
        
        # Cache result
        self.cache.set(cache_key, data, ttl=300)
        
        return data
    
    async def load_all(self, key: str, loader_func: Callable, 
                      max_pages: int = 100) -> List[Dict[str, Any]]:
        """
        Load all pages of data.
        
        Args:
            key: Cache key prefix
            loader_func: Function to load data
            max_pages: Maximum pages to load
            
        Returns:
            All data
        """
        all_data = []
        
        for page in range(max_pages):
            page_data = await self.load_page(key, page, loader_func)
            
            if not page_data:
                break
            
            all_data.extend(page_data)
            
            if len(page_data) < self.page_size:
                break
        
        return all_data


class IndexOptimizer:
    """Database index optimization recommendations."""
    
    @staticmethod
    def analyze_query_pattern(query: str) -> List[str]:
        """
        Analyze query pattern and recommend indexes.
        
        Args:
            query: SQL query to analyze
            
        Returns:
            List of recommended index statements
        """
        recommendations = []
        query_lower = query.lower()
        
        # Check for WHERE clauses
        if 'where' in query_lower:
            # Extract columns from WHERE clause
            where_start = query_lower.find('where') + 5
            where_end = query_lower.find('group by') if 'group by' in query_lower else \
                       query_lower.find('order by') if 'order by' in query_lower else \
                       query_lower.find('limit') if 'limit' in query_lower else \
                       len(query_lower)
            
            where_clause = query_lower[where_start:where_end]
            columns = [col.strip() for col in where_clause.split('and') if '=' in col]
            
            for col in columns:
                col_name = col.split('=')[0].strip()
                if col_name and not col_name.startswith('('):
                    recommendations.append(f"CREATE INDEX idx_{col_name} ON table_name ({col_name});")
        
        # Check for JOIN conditions
        if 'join' in query_lower:
            recommendations.append("Ensure foreign key columns are indexed")
        
        # Check for ORDER BY
        if 'order by' in query_lower:
            order_start = query_lower.find('order by') + 8
            order_end = query_lower.find('limit') if 'limit' in query_lower else len(query_lower)
            order_clause = query_lower[order_start:order_end]
            columns = [col.strip() for col in order_clause.split(',')]
            
            for col in columns:
                recommendations.append(f"CREATE INDEX idx_{col} ON table_name ({col});")
        
        return recommendations


class QueryOptimizer:
    """SQL query optimization utilities."""
    
    @staticmethod
    def add_query_hints(query: str, hints: List[str]) -> str:
        """
        Add query hints to SQL query.
        
        Args:
            query: Original SQL query
            hints: List of hints to add
            
        Returns:
            Query with hints
        """
        if not hints:
            return query
        
        hint_string = ' '.join(hints)
        return f"/*+ {hint_string} */ {query}"
    
    @staticmethod
    def optimize_join_order(query: str, table_sizes: Dict[str, int]) -> str:
        """
        Optimize join order based on table sizes.
        
        Args:
            query: SQL query with joins
            table_sizes: Dictionary of table names and row counts
            
        Returns:
            Query with optimized join order
        """
        # This is a simplified implementation
        # Real implementation would parse SQL and reorder joins
        tables = list(table_sizes.keys())
        tables_sorted = sorted(tables, key=lambda t: table_sizes[t])
        
        # Log recommendation
        logger.info(f"Recommended join order: {tables_sorted}")
        
        return query


class MemoryCache:
    """In-memory cache with LRU eviction."""
    
    def __init__(self, max_size: int = 1000):
        """
        Initialize memory cache.
        
        Args:
            max_size: Maximum number of items in cache
        """
        self.max_size = max_size
        self.cache: Dict[str, Any] = {}
        self.access_order: List[str] = []
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if key in self.cache:
            # Update access order
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]
        return None
    
    def set(self, key: str, value: Any):
        """Set value in cache."""
        if key in self.cache:
            self.access_order.remove(key)
        elif len(self.cache) >= self.max_size:
            # Evict least recently used
            lru_key = self.access_order.pop(0)
            del self.cache[lru_key]
        
        self.cache[key] = value
        self.access_order.append(key)
    
    def delete(self, key: str):
        """Delete key from cache."""
        if key in self.cache:
            del self.cache[key]
            self.access_order.remove(key)
    
    def clear(self):
        """Clear all cache entries."""
        self.cache.clear()
        self.access_order.clear()
    
    def size(self) -> int:
        """Get current cache size."""
        return len(self.cache)
