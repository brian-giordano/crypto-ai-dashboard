import logging
from typing import Dict
import os

# Cache TTL configurations 
CACHE_TTLS: Dict[str, int] = {
    'market_data': int(os.getenv("MARKET_DATA_TTL", 300)),     # 5 minutes
    'coin_data': int(os.getenv("COIN_DATA_TTL", 600)),        # 10 minutes
    'sentiment': int(os.getenv("SENTIMENT_TTL", 3600)),       # 1 hour
    'full_response': int(os.getenv("FULL_RESPONSE_TTL", 1800)) # 30 minutes
}

def get_cache_key(prefix: str, identifier: str) -> str:
    """Generate consistent cache keys"""
    return f"{prefix}:{identifier.lower()}"

def log_cache_status(cache_key: str, hit: bool):
    """Log cache hits and misses"""
    if hit:
        logging.info(f"Cache hit for {cache_key}")
    else:
        logging.info(f"Cache miss for {cache_key}")