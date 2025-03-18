from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/")

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
    broker_connection_retry_on_startup=True
)

# Create Celery app
celery_app = Celery(
    "crypto_tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

@celery_app.task(
    name="process_question_task",
    bind=True,
    max_retries=3,
    default_retry_delay=60
)
def process_question_task(self, question_data: dict):
    """
    Celery task to process questions asynchronously.
    This task will call the `process_question` function from `main.py`.
    """
    from main import process_question           # Lazy import to avoid circular import issue.
    try:
        return process_question(question_data)
    except Exception as e:
        # Retry the task in case of failure
        raise self.retry(e=e)