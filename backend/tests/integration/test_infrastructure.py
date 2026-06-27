import pytest
from app.core.database import db_manager
from app.core.cache import cache_manager, get_redis
from app.core.config import settings

@pytest.mark.asyncio
async def test_database_connection():
    db_manager.init_db(settings.database_url)
    assert db_manager.engine is not None
    assert db_manager.session_maker is not None
    
    # We won't actually hit the DB in this test unless a real DB is running,
    # but we can verify the initialization logic.
    await db_manager.close_db()
    assert db_manager.engine is None

@pytest.mark.asyncio
async def test_redis_connection():
    # If redis isn't running, this will log an error but shouldn't raise exception
    # due to how we wrote init_cache.
    await cache_manager.init_cache(settings.redis_url)
    assert cache_manager.pool is not None
    assert cache_manager.redis is not None
    
    redis = get_redis()
    assert redis is not None
    
    await cache_manager.close_cache()
