from redis import Redis
from urllib.parse import urlparse
import logging
from config import REDIS_URL

# Parse the Redis URL
parsed_redis_url = urlparse(REDIS_URL)

# Initialize Redis client
redis_client = Redis(
    host=parsed_redis_url.hostname,
    port=parsed_redis_url.port,
    password=parsed_redis_url.password,
    decode_responses=True  # Ensures Redis returns strings instead of bytes
)

# Test Redis connection
try:
    redis_client.ping()
    logging.info(f"Successfully connected to Redis at {parsed_redis_url.hostname}:{parsed_redis_url.port}")
except Exception as e:
    logging.error(f"Failed to connect to Redis: {e}")
    raise