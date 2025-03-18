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

## Start the Celery worker
if __name__ == "__main__":
    celery_app.start()