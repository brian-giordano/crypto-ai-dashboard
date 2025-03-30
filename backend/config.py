import os
from dotenv import load_dotenv

# load environment variables
load_dotenv()

# Redis configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

print(f"Using Redis URL: {REDIS_URL}")
print(f"Using Frontend URL: {FRONTEND_URL}")