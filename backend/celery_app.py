from celery import Celery
from config import REDIS_URL

# Create Celery app
celery_app = Celery(
    "crypto_tasks",
    broker=REDIS_URL,
    backend=REDIS_URL
)

# Configure Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)