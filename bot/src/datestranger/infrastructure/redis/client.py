"""
Redis Connection Client Wrapper for DateWithStranger
"""

from typing import Optional, Any
from datestranger.config.settings import get_settings
from datestranger.infrastructure.logging.logger import get_logger

logger = get_logger("redis_client")


class RedisClient:
    def __init__(self, host: Optional[str] = None, port: Optional[int] = None, password: Optional[str] = None, db: int = 0):
        settings = get_settings()
        self.host = host or settings.redis.host
        self.port = port or settings.redis.port
        self.password = password or settings.redis.password
        self.db = db or settings.redis.db
        self.client = None
        self._is_connected = False
        self._memory_cache = {}  # In-memory fallback for local dev/testing

    def connect(self) -> bool:
        """Attempt to connect to Redis server."""
        try:
            import redis
            self.client = redis.Redis(
                host=self.host,
                port=self.port,
                password=self.password,
                db=self.db,
                socket_timeout=3.0,
                decode_responses=True
            )
            self.client.ping()
            self._is_connected = True
            logger.info(f"✅ Connected to Redis at {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.warning(f"⚠️ Redis connection un-available ({e}). Falling back to in-memory cache.")
            self._is_connected = False
            return False

    def is_connected(self) -> bool:
        return self._is_connected

    def get(self, key: str) -> Optional[str]:
        if self._is_connected and self.client:
            try:
                return self.client.get(key)
            except Exception as e:
                logger.error(f"Redis GET error: {e}")
        return self._memory_cache.get(key)

    def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        if self._is_connected and self.client:
            try:
                return bool(self.client.set(key, str(value), ex=ex))
            except Exception as e:
                logger.error(f"Redis SET error: {e}")
        self._memory_cache[key] = str(value)
        return True

    def delete(self, key: str) -> bool:
        if self._is_connected and self.client:
            try:
                return bool(self.client.delete(key))
            except Exception as e:
                logger.error(f"Redis DELETE error: {e}")
        if key in self._memory_cache:
            del self._memory_cache[key]
            return True
        return False

    def ping(self) -> bool:
        if self._is_connected and self.client:
            try:
                return bool(self.client.ping())
            except Exception:
                return False
        return True


_redis_instance: Optional[RedisClient] = None


def get_redis_client() -> RedisClient:
    global _redis_instance
    if _redis_instance is None:
        _redis_instance = RedisClient()
        _redis_instance.connect()
    return _redis_instance
