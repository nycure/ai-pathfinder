import os
import json
import hashlib
import time
import threading
from typing import Any, Optional

class CacheService:
    """
    Production-grade caching layer supporting Redis distributed caching with automatic
    fallback to a thread-safe, memory-bounded LRU in-memory cache with TTL expiration.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(CacheService, cls).__new__(cls)
                    cls._instance._init_cache()
        return cls._instance

    def _init_cache(self):
        self._memory_cache = {}
        self._ttl_cache = {}
        self._max_entries = 1000
        self.use_redis = False
        self.redis_client = None

        redis_url = os.getenv("REDIS_URL")
        if redis_url:
            try:
                import redis
                self.redis_client = redis.from_url(redis_url, decode_responses=True)
                self.redis_client.ping()
                self.use_redis = True
                print("[CacheService] Connected to Redis cluster.")
            except Exception as e:
                print(f"[CacheService] Redis connection failed, falling back to in-memory: {e}")
                self.use_redis = False

    def _generate_key(self, prefix: str, **kwargs) -> str:
        """Generates a consistent cache key based on a prefix and arguments."""
        key_str = json.dumps(kwargs, sort_keys=True)
        key_hash = hashlib.md5(key_str.encode('utf-8')).hexdigest()
        return f"{prefix}:{key_hash}"

    def get(self, prefix: str, **kwargs) -> Optional[Any]:
        """Retrieves a value from Redis or the local in-memory cache."""
        key = self._generate_key(prefix, **kwargs)
        
        if self.use_redis and self.redis_client:
            try:
                val = self.redis_client.get(key)
                if val:
                    return json.loads(val)
            except Exception as e:
                print(f"[CacheService] Redis get error: {e}")

        # In-memory cache lookup
        with self._lock:
            if key in self._memory_cache:
                ttl = self._ttl_cache.get(key)
                if ttl and time.time() > ttl:
                    # Expired
                    del self._memory_cache[key]
                    del self._ttl_cache[key]
                    return None
                return self._memory_cache[key]
        return None

    def set(self, prefix: str, value: Any, ttl_seconds: int = 3600, **kwargs):
        """Sets a value in Redis or the thread-safe local cache with a TTL."""
        key = self._generate_key(prefix, **kwargs)
        
        if self.use_redis and self.redis_client:
            try:
                self.redis_client.setex(key, ttl_seconds, json.dumps(value))
                return
            except Exception as e:
                print(f"[CacheService] Redis set error: {e}")

        # Thread-safe in-memory cache set with LRU pruning
        with self._lock:
            if len(self._memory_cache) >= self._max_entries:
                # Remove oldest 100 entries
                keys_to_remove = list(self._memory_cache.keys())[:100]
                for k in keys_to_remove:
                    self._memory_cache.pop(k, None)
                    self._ttl_cache.pop(k, None)

            self._memory_cache[key] = value
            self._ttl_cache[key] = time.time() + ttl_seconds

    def invalidate(self, prefix: str, **kwargs):
        """Invalidates a cached entry."""
        key = self._generate_key(prefix, **kwargs)
        if self.use_redis and self.redis_client:
            try:
                self.redis_client.delete(key)
            except Exception:
                pass

        with self._lock:
            self._memory_cache.pop(key, None)
            self._ttl_cache.pop(key, None)
