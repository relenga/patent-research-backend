import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

LOGGER = logging.getLogger(__name__)


async def check_database_health(db: AsyncSession) -> bool:
    try:
        await db.execute(text("SELECT 1"))
        return True
    except Exception as e:
        LOGGER.exception(f"Database health check failed with error: {e}")
        return False


# Phase 1 Cleanup: Redis health check removed as Redis/ARQ infrastructure was removed
# async def check_redis_health(redis: Redis) -> bool:
#     try:
#         await redis.ping()
#         return True
#     except Exception as e:
#         LOGGER.exception(f"Redis health check failed with error: {e}")
#         return False
