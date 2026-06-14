from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.core.config import settings

Base = declarative_base()

class DatabaseManager:
    def __init__(self):
        self.engine: AsyncEngine | None = None
        self.session_maker: async_sessionmaker[AsyncSession] | None = None

    def init_db(self, db_url: str):
        if not db_url:
            return
            
        self.engine = create_async_engine(
            db_url,
            echo=settings.debug,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
        )
        self.session_maker = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )

    async def close_db(self):
        if self.engine:
            await self.engine.dispose()
            self.engine = None
            self.session_maker = None

db_manager = DatabaseManager()

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    if not db_manager.session_maker:
        raise RuntimeError("Database not initialized")
        
    async with db_manager.session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
