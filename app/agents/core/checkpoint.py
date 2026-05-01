"""
app/agents/core/checkpoint.py
==============================
Persistent Async Postgres checkpointer for LangGraph.
"""

import logging
from psycopg_pool import AsyncConnectionPool
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.core.config import settings

logger = logging.getLogger(__name__)

class CheckpointManager:
    _pool: AsyncConnectionPool = None
    _checkpointer: AsyncPostgresSaver = None

    @classmethod
    async def get_checkpointer(cls) -> AsyncPostgresSaver:
        if cls._checkpointer is None:
            logger.info("Initializing Async Postgres checkpointer...")
            # Initialize async pool
            cls._pool = AsyncConnectionPool(
                conninfo=settings.database_url,
                max_size=settings.DB_MAX_CONNECTIONS,
                kwargs={"autocommit": True}
            )
            # Initialize saver
            cls._checkpointer = AsyncPostgresSaver(cls._pool)
            # Ensure tables exist (setup is async too)
            await cls._checkpointer.setup()
            logger.info("Async Postgres checkpointer tables setup complete.")
        return cls._checkpointer

    @classmethod
    async def close(cls):
        if cls._pool:
            await cls._pool.close()
            cls._pool = None
            cls._checkpointer = None

async def get_postgres_checkpointer() -> AsyncPostgresSaver:
    """Convenience async dependency."""
    return await CheckpointManager.get_checkpointer()
