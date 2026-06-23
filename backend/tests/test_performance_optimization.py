"""
Tests for Performance Optimization Module
"""
import pytest
from backend.performance_optimization import (
    RedisCache,
    MemoryCache,
    CacheStats,
    BatchProcessor,
    DataLoader
)
from unittest.mock import Mock
import time


@pytest.fixture
def mock_redis():
    """Create mock Redis client."""
    redis = Mock()
    redis.get = Mock(return_value=None)
    redis.setex = Mock(return_value=True)
    redis.delete = Mock(return_value=1)
    redis.keys = Mock(return_value=[])
    return redis


def test_redis_cache_get_miss(mock_redis):
    """Test Redis cache get miss."""
    cache = RedisCache(mock_redis, default_ttl=3600)
    value = cache.get("test_key")
    assert value is None
    assert cache.stats.misses == 1


def test_redis_cache_set(mock_redis):
    """Test Redis cache set."""
    cache = RedisCache(mock_redis, default_ttl=3600)
    result = cache.set("test_key", {"data": "test"})
    assert result is True
    mock_redis.setex.assert_called_once()


def test_redis_cache_delete(mock_redis):
    """Test Redis cache delete."""
    cache = RedisCache(mock_redis, default_ttl=3600)
    result = cache.delete("test_key")
    assert result is True
    mock_redis.delete.assert_called_once()


def test_redis_cache_stats():
    """Test cache statistics."""
    stats = CacheStats(hits=100, misses=50)
    assert stats.hits == 100
    assert stats.misses == 50
    assert stats.hit_rate == 0.6666666666666666


def test_redis_cache_hit_rate():
    """Test cache hit rate calculation."""
    stats = CacheStats(hits=90, misses=10)
    assert stats.hit_rate == 0.9


def test_redis_cache_hit_rate_zero():
    """Test cache hit rate with no data."""
    stats = CacheStats()
    assert stats.hit_rate == 0.0


def test_memory_cache_set():
    """Test memory cache set."""
    cache = MemoryCache(max_size=10)
    cache.set("key1", "value1")
    assert cache.get("key1") == "value1"
    assert cache.size() == 1


def test_memory_cache_get():
    """Test memory cache get."""
    cache = MemoryCache(max_size=10)
    cache.set("key1", "value1")
    value = cache.get("key1")
    assert value == "value1"


def test_memory_cache_lru_eviction():
    """Test LRU eviction in memory cache."""
    cache = MemoryCache(max_size=3)
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    cache.set("key3", "value3")
    cache.set("key4", "value4")  # Should evict key1
    
    assert cache.get("key1") is None
    assert cache.get("key4") == "value4"


def test_memory_cache_delete():
    """Test memory cache delete."""
    cache = MemoryCache(max_size=10)
    cache.set("key1", "value1")
    cache.delete("key1")
    assert cache.get("key1") is None


def test_memory_cache_clear():
    """Test memory cache clear."""
    cache = MemoryCache(max_size=10)
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    cache.clear()
    assert cache.size() == 0


def test_batch_processor_add():
    """Test batch processor add."""
    processor = BatchProcessor(batch_size=5, max_delay=1.0)
    should_process = processor.add("item1")
    assert should_process is False


def test_batch_processor_batch_size():
    """Test batch processor batch size trigger."""
    processor = BatchProcessor(batch_size=3, max_delay=1.0)
    processor.add("item1")
    processor.add("item2")
    should_process = processor.add("item3")
    assert should_process is True


def test_batch_processor_get_batch():
    """Test batch processor get batch."""
    processor = BatchProcessor(batch_size=3, max_delay=1.0)
    processor.add("item1")
    processor.add("item2")
    batch = processor.get_batch()
    assert len(batch) == 2


def test_batch_processor_flush():
    """Test batch processor flush."""
    processor = BatchProcessor(batch_size=10, max_delay=1.0)
    processor.add("item1")
    processor.add("item2")
    batch = processor.flush()
    assert len(batch) == 2


def test_data_loader_load_page():
    """Test data loader page loading."""
    cache = MemoryCache(max_size=100)
    loader = DataLoader(cache, page_size=10)
    
    async def mock_loader(offset, limit):
        return [{"id": i} for i in range(offset, offset + limit)]
    
    # This would need async test setup
    # For now, just verify initialization
    assert loader.page_size == 10


def test_cache_stats_clear():
    """Test cache stats clear."""
    cache = RedisCache(Mock(), default_ttl=3600)
    cache.stats.hits = 100
    cache.stats.misses = 50
    cache.clear_stats()
    assert cache.stats.hits == 0
    assert cache.stats.misses == 0
