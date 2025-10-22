import asyncio

from celery import Celery
from celery.schedules import crontab

from app.application.use_cases.user import CleanupUnverifiedUsersUseCase
from app.infrastructure.database.connection import AsyncSessionLocal
from app.infrastructure.repositories.user_repository import SQLAlchemyUserRepository

from app.core.config import settings

celery_app = Celery(
    "coffee_shop", broker=settings.redis_url, backend=settings.redis_url
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

celery_app.conf.beat_schedule = {
    "cleanup-unverified-users": {
        "task": "app.infrastructure.celery.worker.cleanup_unverified_users",
        # "schedule": crontab(hour="*/6"),
        "schedule": crontab(minute="*/1"),  # For testing purposes, runs every minute
    },
}


@celery_app.task(name="app.infrastructure.celery.worker.cleanup_unverified_users")
def cleanup_unverified_users():
    """
    Periodic task to clean up unverified users whose verification has expired.
    Runs every 6 hours.
    """

    async def _cleanup():
        async with AsyncSessionLocal() as session:
            user_repo = SQLAlchemyUserRepository(session)
            use_case = CleanupUnverifiedUsersUseCase(user_repo)
            deleted_count, expired_users = await use_case.execute()
            return deleted_count, expired_users

    # Run the async function using the current event loop
    # This avoids creating a new loop which conflicts with the one used by the DB driver
    loop = asyncio.get_event_loop()
    deleted_count, expired_users = loop.run_until_complete(_cleanup())

    return {"deleted_count": deleted_count, "expired_users": expired_users}
