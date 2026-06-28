from celery import Celery
from src.config.settings import settings

celery_app = Celery(
    "repo_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["src.application.worker"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
)
