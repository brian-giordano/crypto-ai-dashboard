from celery import Celery
from typing import Dict, Any
import os
from dotenv import load_dotenv


load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/")

# Create Celery app
celery_app = Celery(
    "crypto_tasks",
    broker=f"{REDIS_URL}",
    backend=f"{REDIS_URL}"
)

# Configure Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

# For long-running process question task
@celery_app.task(name="process_question_task")
def process_question_task(question_data: dict):
    """
    Celery task to process questions asynchronously.
    This task will cal the `process_question` function from `main.py`.
    """
    from main import process_question                   # import here to avoid circular imports

    return process_question(question_data)