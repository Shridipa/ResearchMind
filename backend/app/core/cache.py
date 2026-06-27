import logging

try:
    from redis.asyncio import Redis, ConnectionPool
except ImportError:  # pragma: no cover
    Redis = None  # type: ignore
    ConnectionPool = None  # type: ignore


logger = logging.getLogger(__name__)

class CacheManager:
    def __init__(self):
        self.pool: ConnectionPool | None = None
        self.redis: Redis | None = None

    async def init_cache(self, redis_url: str):
        if not redis_url:
            return
        if ConnectionPool is None or Redis is None:
            logger.error("redis library not installed; cache disabled.")
            return
        self.pool = ConnectionPool.from_url(
            redis_url,
            decode_responses=True,
            max_connections=10
        )
        self.redis = Redis(connection_pool=self.pool)

        try:
            await self.redis.ping()
            logger.info("Successfully connected to Redis")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")

    async def close_cache(self):
        if self.redis:
            await self.redis.close()
        if self.pool:
            await self.pool.disconnect()
            
    async def get(self, key: str) -> str | None:
        if not self.redis:
            return None
        return await self.redis.get(key)
        
    async def set(self, key: str, value: str, ex: int | None = None) -> bool:
        if not self.redis:
            return False
        return await self.redis.set(key, value, ex=ex)
        
cache_manager = CacheManager()

def get_redis():
    return cache_manager.redis
