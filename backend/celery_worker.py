from celery import Celery
from typing import Dict, Any
import os
from dotenv import load_dotenv
from redis import Redis
import sys

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/")
print(f"Using Redis URL: {REDIS_URL}")  # Log the Redis URL

# Test Redis connection
try:
    redis_client = Redis.from_url(REDIS_URL)
    redis_client.ping()  # Test the connection
    print("Successfully connected to Redis.")
except Exception as e:
    print(f"Failed to connect to Redis: {e}")
    sys.exit(1)  # Exit if the connection fails

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