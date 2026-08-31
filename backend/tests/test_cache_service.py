import time
import pytest
from services.cache_service import CacheService

def test_cache_service_in_memory_set_get():
    cache = CacheService()
    
    cache.set("test_prefix", {"message": "hello world"}, ttl_seconds=10, item_id="123")
    val = cache.get("test_prefix", item_id="123")
    
    assert val == {"message": "hello world"}
    
    # Nonexistent key
    assert cache.get("test_prefix", item_id="999") is None

def test_cache_service_expiration():
    cache = CacheService()
    
    # 1 second TTL
    cache.set("short_lived", "expires_soon", ttl_seconds=1, key="abc")
    assert cache.get("short_lived", key="abc") == "expires_soon"
    
    time.sleep(1.2)
    assert cache.get("short_lived", key="abc") is None

def test_cache_service_invalidation():
    cache = CacheService()
    cache.set("inv_test", "data", ttl_seconds=60, user="u1")
    assert cache.get("inv_test", user="u1") == "data"
    
    cache.invalidate("inv_test", user="u1")
    assert cache.get("inv_test", user="u1") is None
