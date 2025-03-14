import sys
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from transformers import (
    pipeline, 
    AutoModelForSequenceClassification, 
    AutoTokenizer
)
from fastapi.middleware.cors import CORSMiddleware
import requests
from typing import Dict, Any, Optional, List
import time
from functools import lru_cache
import os
import uvicorn
import logging
import psutil
from dotenv import load_dotenv
import json
from redis import Redis
from datetime import timedelta
from urllib.parse import urlparse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from contextlib import asynccontextmanager

# Load environment variables
load_dotenv()

# Define pydantic request model for API documentation and validation
class SentimentRequest(BaseModel):
    text: str = Field(..., description="Text to analyze for sentiment")

class SentimentResponse(BaseModel):
    sentiment: str
    confidence: float
    cached: bool = Field(default=False, description="Indicates if result was from cache")

# Access environment variables
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")

# Load Redis URL from environment variables
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Parse the Redis URL
parsed_redis_url = urlparse(REDIS_URL)

# Redis Configuration
REDIS_CACHE_TTL = int(os.getenv("REDIS_CACHE_TTL", 300)) # 5 minutes

CACHE_TTLS = {
    'market_data': int(os.getenv("MARKET_DATA_TTL", 300)),     # 5 minutes
    'coin_data': int(os.getenv("COIN_DATA_TTL", 600)),       # 10 minutes
    'sentiment': int(os.getenv("SENTIMENT_TTL", 3600))       # 1 hour
}

# Initialize Redis client
redis_client = Redis(
    host=parsed_redis_url.hostname,
    port=parsed_redis_url.port,
    password=parsed_redis_url.password,
    decode_responses=True
)

try:
    # Test the Redis connection
    redis_client.ping()
    logging.info(f"Successfully connected to Redis at {parsed_redis_url.hostname}:{parsed_redis_url.port}")
    logging.info(f"Current Redis database: {redis_client.connection_pool.connection_kwargs.get('db', 0)}")
except Exception as e:
    logging.error(f"Failed to connect to Redis: {e}")

# Cache helper function
def get_cache_key(prefix: str, identifier: str) -> str:
    """Generate consistent cache keys"""
    return f"{prefix}:{identifier.lower()}"

def log_cache_status(cache_key: str, hit: bool):
    """Log cache hits and misses"""
    if hit:
        logging.info(f"Cache hit for {cache_key}")
    else: 
        logging.info(f"Cache miss for {cache_key}")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)     # Logs to console (for visibility in Render.)
    ]
)

def log_memory_usage(stage: str):
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    logging.info(f"{stage} - Memory usage: {memory_info.rss / 1024 / 1024:.2f} MB")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for the FastAPI app"""
    # Startup
    logging.info("Starting application startup tasks...")
    try:
        # Preload market data
        data = crypto_service.get_market_data(limit=100)
        if data:
            logging.info("Successfully preloaded market data")
            logging.info(f"Preloaded data for {len(data)} cryptocurrencies")
        else:
            logging.warning("No market data was preloaded")
    except Exception as e:
        logging.error("Erorr during startup preloading: {e}")
    
    logging.info("Completed startup tasks")

    yield # Server is running

    # Shutdown
    logging.info("Shutting down application...")

# FastAPI App main
app = FastAPI(lifespan=lifespan)

# Add CORS middleware to allow requests from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        frontend_url,  # Local frontend
        "https://crypto-ai-dashboard-lovat.vercel.app",  # Production frontend
    ], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Preload market data at as app startup


# Request timing middlewear
class TimingMiddlewear(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response
    
app.add_middleware(TimingMiddlewear)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logging.error(f"Unhandled exception: {exc}")
    return {"detail": "An internal error occurred."}

# Log memory usage before initializing the pipeline
log_memory_usage("Before initializing sentiment pipeline")
logging.info("Initializing sentiment analysis pipeline...")

# Load the model globally
sentiment_pipeline = pipeline("sentiment-analysis", model="yiyanghkust/finbert-tone")

# Log memory usage after initializing the pipeline
log_memory_usage("After initializing sentiment pipeline")
logging.info("Sentiment analysis pipeline initialized successfully.")

# Define Pydantic models

class QueryRequest(BaseModel):
    question: str  
    context: Dict[str, Any] = None  # Optional context like selected crypto

class AIResponse(BaseModel):
    text: str
    sentiment: str = None
    confidence: float = None
    metrics: Dict[str, str] = None

# CoinGecko API Service
class CryptoDataService:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.last_request_time = 0
        self.min_request_interval = 2
        self.redis_client = redis_client
        self.default_ttl = REDIS_CACHE_TTL

    def _rate_limit(self):
        """Ensure rate limits arent exceeded"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        self.last_request_time = time.time()

    def get_market_data(self, vs_currency: str = "usd", limit: int = 100) -> List[Dict[str, Any]]:
        """Get market data with improved caching"""
        cache_key = get_cache_key('market_data', f"{vs_currency}_{limit}")
        logging.info(f"Generated cache key: {cache_key}")

        try:
            # Try to get cached data from Redis first
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                log_cache_status(cache_key, True)
                return json.loads(cached_data)
            
            log_cache_status(cache_key, False)

            # Rate limiting
            self._rate_limit()

            # Fetch from API
            params = {
                "vs_currency": vs_currency,
                "order": "market_cap_desc",
                "per_page": limit,
                "page": 1,
                "sparkline": "true",
                "price_change_percentage": "24h"
            }
            response = requests.get(f"{self.base_url}/coins/markets", params=params)

            # Handle rate limiting
            if response.status_code == 429:
                logging.warning("Rate limit reached, checking cache for stale data")
                cached_data = self.redis_client.get(cache_key)
                if cached_data:
                    return json.loads(cached_data)
                return []

            response.raise_for_status()
            data = response.json()

            # Cache the new data
            self.redis_client.setex(
                cache_key,
                CACHE_TTLS['market_data'],
                json.dumps(data)
            )

            return data
        
        except Exception as e:
            logging.error(f"Error fetching market data: {e}")
            # Try to get stale data from cache
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                logging.info(f"Using stale cached data for {cache_key}")
                return json.loads(cached_data)
            return []

    def get_coin_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Find a coin by name or symbol in the top 100"""
        cache_key = get_cache_key('coin', name)

        # Try to get data from Redis
        try:
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                logging.info(f"Cache hit for coin {name}")
                return json.loads(cached_data)

            # If not in cache, search in market data
            market_data = self.get_market_data(limit=100)
            name_lower = name.lower()

            # Try exact match
            coin = next(
                (coin for coin in market_data
                 if coin["id"].lower() == name_lower
                 or coin["symbol"].lower() == name_lower),
                 None
            )

            # Cache the results (even if None)
            self.redis_client.setex(
                cache_key,
                self.default_ttl,
                json.dumps(coin) if coin else "null"
            )

            return coin
            
        except Exception as e:
            logging.error(f"Error finding coin: {e}")
            # Try to get stale data from cache
            cached_data = self.redis_client.get(cache_key)
            if cached_data and cached_data != "null":
                return json.loads(cached_data)
            return None

# Initialize the crypto data service
crypto_service = CryptoDataService()

# Basic route
@app.get("/")
@app.head("/")  # Added to handle HEAD requests
async def read_root():
    return {"message": "Welcome to the Crypto AI Dashboard Backend!"}

# Health check endpoint
@app.get("/healthz")
async def health_check():
    return {"status": "ok"}

# Redis health check endpoint
@app.get("/healthz/redis")
async def redis_health_check():
    try:
        redis_client.ping()
        return {"status": "ok", "message": "Redis connection is healthy"}
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Redis connection failed: {str(e)}"
        )

# Fetch from api/crypto endpoint
@app.get("/api/crypto")
async def get_crypto_data():
    """Fetch cryptocurrency market data with Redis caching"""
    try:
        data = crypto_service.get_market_data()
        if not data:
            raise HTTPException(
                status_code=503,
                detail="Unable to fetch crypto data"
            )
        return data
    except Exception as e:
        logging.error(f"Error in /api/crypto endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

# Sentiment analysis endpoint
@app.post("/analyze-sentiment/")
async def analyse_sentiment(request: SentimentRequest):
    logging.info(f"Received sentiment analysis request: {request.text}")
    result = sentiment_pipeline(request.text)
    logging.info(f"Sentiment analysis result: {result}")
    return {"sentiment": result[0]["label"].upper(), "score": min(result[0]["score"], 0.95)}

# Helper function to format large numbers
def format_large_number(num: float) -> str:
    """Format large numbers to K, M, B, T format"""
    if num >= 1_000_000_000_000:
        return f"{num / 1_000_000_000_000:.2f}T"
    elif num >= 1_000_000_000:
        return f"{num / 1_000_000_000:.2f}B"
    elif num >= 1_000_000:
        return f"{num / 1_000_000:.2f}M"
    elif num >= 1_000:
        return f"{num / 1_000:.2f}K"
    return f"{num:.2f}"

def generate_ai_response(question, sentiment, coin_data):
    """Generate a response based on the question and data"""
    question_lower = question.lower()

    # Extract key terms from the question
    key_terms = []
    for term in ["price", "trend", "market cap", "volume", "prediction", "future", "sentiment"]:
        if term in question_lower:
            key_terms.append(term)

    if coin_data:
        coin_name = coin_data["name"]
        price_change = coin_data["price_change_percentage_24h"]
        price_direction = "up" if price_change > 0 else "down"

        if "price" in key_terms or "trend" in key_terms:
            sentiment_desc = ""
            if price_change > 5:
                sentiment_desc = "showing strong bullish momentum"
            elif price_change > 2:
                sentiment_desc = "trending positively"
            elif price_change < -5:
                sentiment_desc = "showing significant bearish pressure"
            elif price_change < -2:
                sentiment_desc = "trending negatively"
            else:
                sentiment_desc = "relatively stable"

            return f"{coin_name} is {sentiment_desc}, moving {price_direction} {abs(price_change):.2f}% in the last 24 hours. The current price is ${coin_data['current_price']}."

        elif "predict" in question_lower or "forecast" in question_lower:
            return f"While I can't predict prices with certainty, {coin_name} has moved {price_direction} {abs(price_change):.2f}% in the last 24 hours with a trading volume of ${format_large_number(coin_data['total_volume'])}."

        else:
            return f"{coin_name} currently has a market cap of ${format_large_number(coin_data['market_cap'])} and is trading at ${coin_data['current_price']}. In the last 24 hours, the price has changed by {price_change:.2f}%."

    else:
        # General market response
        if "top" in question_lower and any(num in question_lower for num in ["5", "10", "five", "ten"]):
            market_data = crypto_service.get_market_data(limit=5)
            coins = [f"{i+1}. {coin['name']} (${coin['current_price']})" for i, coin in enumerate(market_data[:5])]
            return f"The top 5 cryptos by market cap are: \n" + "\n".join(coins)

        elif "sentiment" in question_lower or "market" in question_lower:
            market_data = crypto_service.get_market_data(limit=10)
            positive_count = sum(1 for coin in market_data if coin["price_change_percentage_24h"] > 0)
            sentiment = "bullish" if positive_count > 5 else "bearish"
            return f"The overall market sentiment appears to be {sentiment}. {positive_count} of the top 10 cryptocurrencies are showing positive price movement in the last 24 hours."

        else:
            return "Based on current market data, cryptocurrencies are showing mixed performance. For specific insights, try asking about a particular coin or market metric."


# Context-aware sentiment analysis
def analyze_sentiment_with_context(question, context=None):
    """Analyze sentiment with context awareness and caching"""
    # Generate cache key
    cache_key = get_cache_key('sentiment', question)

    logging.info(f"Generated cache key for sentiment: {cache_key}")

    # Check cache first
    cached_result = redis_client.get(cache_key)
    if cached_result:
        log_cache_status(cache_key, True)
        logging.info(f"Returning cached sentiment result for key: {cache_key}")
        return json.loads(cached_result)
    
    log_cache_status(cache_key, False)
    logging.info("Performing sentiment analysis...")
    
    # Basic sentiment analysis
    result = sentiment_pipeline(question)[0]
    sentiment = result["label"].upper()  # Standardize to uppercase
    confidence = min(result["score"], 0.95)  # Cap at 95%

    # Context-aware adjustments
    if context and isinstance(context, dict) and "price_change_percentage_24h" in context:
        price_change = context["price_change_percentage_24h"]

        # If question contains positive terms but price is down significantly
        if sentiment == "POSITIVE" and price_change < -5 and any(term in question.lower() for term in ["price", "trend", "going up"]):
            sentiment = "NEGATIVE"  # Override to negative
            confidence = min(confidence, 0.8)  # Cap confidence

        # If question contains negative terms but price is up significantly
        elif sentiment == "NEGATIVE" and price_change > 5 and any(term in question.lower() for term in ["price", "trend", "going down"]):
            sentiment = "POSITIVE"  # Override to positive
            confidence = min(confidence, 0.8)  # Cap confidence

    # For prediction questions, reduce confidence
    if any(term in question.lower() for term in ["predict", "forecast", "future"]):
        confidence = min(confidence, 0.7)  # Cap confidence for predictions

    # Create final result AFTER all adjustments
    final_result = {"label": sentiment, "score": confidence}

    # Cache final result
    redis_client.setex(
        cache_key,
        CACHE_TTLS['sentiment'],
        json.dumps(final_result)
    )

    logging.info(f"Cacehd sentiment for key: {cache_key}")

    return final_result

# Add sentiment explanation
def get_sentiment_explanation(sentiment, confidence, coin_data=None):
    """Generate an explanation for the sentiment"""
    # Convert sentiment to lowercase for comparison
    sentiment_lower = sentiment.lower()

    if not coin_data:
        if sentiment_lower == "positive":
            return "The sentiment appears positive based on the optimistic language in your question."
        elif sentiment_lower == "negative":
            return "The sentiment appears negative based on the cautious language in your question."
        else:
            return "The sentiment appears neutral based on the balanced language in your question."

    # With coin data
    price_change = coin_data.get("price_change_percentage_24h", 0)

    if sentiment_lower == "positive":
        if price_change > 0:
            return f"The sentiment is positive due to the {price_change:.2f}% price increase in the last 24 hours."
        else:
            return "Despite the recent price movement, the overall sentiment remains positive based on market indicators."

    elif sentiment_lower == "negative":
        if price_change < 0:
            return f"The sentiment is negative due to the {abs(price_change):.2f}% price decrease in the last 24 hours."
        else:
            return "Despite the recent positive price movement, there are concerns in the market leading to a negative sentiment."

    else:
        return "The market sentiment appears neutral, indicating a balance between positive and negative factors."

# ask endpoint (AI):    Process user questions about crypto, with sentiment analysis and market data. 
#                       Implements caching, performance monitoring, and error handling. 

@app.post("/ask", response_model=AIResponse)
async def process_question(request: QueryRequest):
    start_time = time.time()
    cache_key = get_cache_key('full_response', request.question)
    metrics = {}

    try:
        """
        Performance monitoring metrics:
        - Context Extraction: Time taken to identify cryptocurrency from question
        - Data Fetching: Time taken to retrieve market/coin data (including cache checks)
        - Sentiment Analysis: Time taken for sentiment analysis (including cache)
        - Response Generation: Time taken to generate and format the response
        """
        
        timing_metrics = {}
        def log_step_time(step_name: str, start: float) -> float:
            """Log the time taken for each processing step and return the end time."""
            end = time.time()
            duration = end - start
            timing_metrics[step_name] = duration
            logging.info(f"{step_name}: {duration:.2f}s")
            return end
        
        # Step 1: Check cache
        cached_response = redis_client.get(cache_key)
        if cached_response:
            log_cache_status(cache_key, True)
            return AIResponse(**json.loads(cached_response))
        log_cache_status(cache_key, False)

        # Step 2: Extract context and identify crypto
        step_start = time.time()
        question = request.question.lower()
        crypto_context = "the cryptocurrency market"

        # use set for O(1) lookup
        crypto_keywords = {
            # Bitcoin and variations
            "bitcoin": "bitcoin", "btc": "bitcoin",
            "wrapped bitcoin": "bitcoin",
            "bitcoin cash": "bitcoin-cash", "bch": "bitcoin-cash",

            # Ethereum and variations
            "ethereum": "ethereum", "eth": "ethereum",
            "lido staked ether": "ethereum", "steth": "ethereum",

            # Stablecoins
            "tether": "tether", "usdt": "tether",
            "usdc": "usd-coin", "usd coin": "usd-coin",
            "dai": "dai",
            "ethena usde": "ethena-usd",

            # Major altcoins
            "cardano": "cardano", "ada": "cardano",
            "dogecoin": "dogecoin", "doge": "dogecoin",
            "ripple": "ripple", "xrp": "ripple",
            "solana": "solana", "sol": "solana",
            "polkadot": "polkadot", "dot": "polkadot",
            "chainlink": "chainlink", "link": "chainlink",
            "avalanche": "avalanche-2", "avax": "avalanche-2",
            "litecoin": "litecoin", "ltc": "litecoin",

            # Other notable coins
            "tron": "tron", "trx": "tron",
            "stellar": "stellar", "xlm": "stellar",
            "hedera": "hedera", "hbar": "hedera",
            "shiba inu": "shiba-inu", "shib": "shiba-inu",
            "leo": "leo-token",
            "mantra": "mantra-dao", "om": "mantra-dao",
            "sui": "sui",
            "toncoin": "the-open-network", "ton": "the-open-network",
            "pi network": "pi-network", "pi": "pi-network"
        }

        for keyword in crypto_keywords:
            if keyword in question:
                crypto_context = crypto_keywords[keyword]
                break

        step_start = log_step_time("Context Extraction", step_start)

        # Step 3: Parallel data fetching
        step_start = time.time()
        coin_data = None
        market_data = None

        # Fetch both coin and market data if needed
        if crypto_context != "the cryptocurrency market":
            coin_data = crypto_service.get_coin_by_name(crypto_context)
            if coin_data:
                metrics = get_coin_metrics(coin_data)
        else:
            # Fetch market overview data for general questions
            market_data = crypto_service.get_market_data(limit=10)
            if market_data:
                metrics = get_market_overview_metrics(market_data)
            
        step_start = log_step_time("Data Fetching", step_start)

        # Step 4: Sentiment Analysis
        step_start = time.time()
        sentiment_result = analyze_sentiment_with_context(question, coin_data)
        sentiment = sentiment_result["label"]
        confidence = sentiment_result["score"]
        step_start = log_step_time("Sentiment Analysis", step_start)

        # Step 5: Generate Response
        step_start = time.time()
        response_text = generate_ai_response(question, sentiment, coin_data)
        sentiment_explanation = get_sentiment_explanation(sentiment, confidence, coin_data)
        response_text += f"\n\n{sentiment_explanation}"
        step_start = log_step_time("Response Generation", step_start)

        # Create response object
        response = AIResponse(
            text=response_text,
            sentiment=sentiment,
            confidence=confidence,
            metrics=metrics
        )

        # Cache the response
        try:
            redis_client.setex(
                cache_key,
                CACHE_TTLS['sentiment'],
                json.dumps(response.dict())
            )
            logging.info(f"Response cached with key: {cache_key}")
        except Exception as e:
            logging.warning(f"Failed to cache response: {e}")

        # Log total processing time
        total_time = time.time() - start_time
        logging.info(f"Total processing time: {total_time:.2f}s")
        logging.info("Step timing breakdown:")
        for step, duration in timing_metrics.items():
            logging.info(f"  {step}: {duration:.2f}s ({(duration/total_time)*100:.1f}%)")

        return response
    
    except Exception as e:
        logging.error(f"Error processing question: {str(e)}", exc_info=True)

        # Attempt to serve stale cache in case of error
        try:
            stale_response = redis_client.get(cache_key)
            if stale_response:
                logging.info("Serving stale cached response due to error")
                return AIResponse(**json.loads(stale_response))
        except Exception as cache_error:
            logging.error(f"Failed to retrieve stale cache: {str(cache_error)}")

        # Fallback response
        return AIResponse(
            text="I apologize, but I'm having trouble processing your request at this time. Please try again.",
            sentiment="NEUTRAL",
            confidence=0.5,
            metrics=metrics
        )
    
def get_coin_metrics(coin_data: Dict[str, Any]) -> Dict[str, str]:
    """Generate metrics for a specific cryptocurrency"""
    return {
        "price": f"${coin_data['current_price']}",
        "marketCap": f"${format_large_number(coin_data['market_cap'])}",
        "volume24h": f"${format_large_number(coin_data['total_volume'])}",
        "change24h": f"{coin_data['price_change_percentage_24h']}%"
    }

def get_market_overview_metrics(market_data: List[Dict[str, Any]]) -> Dict[str, str]:
    """Generate metrics for overall market overview"""
    total_market_cap = sum(coin['market_cap'] for coin in market_data)
    total_volume = sum(coin['total_volume'] for coin in market_data)
    avg_change = sum(coin['price_change_percentage_24h'] for coin in market_data) / len(market_data)

    return {
        "totalMarketCap": f"${format_large_number(total_market_cap)}",
        "totalVolume": f"${format_large_number(total_volume)}",
        "avgChange24h": f"{avg_change:.2f}%",
        "coinsAnalyzed": f"{len(market_data)}"
    }
       
# Run the application with Uvicorn if this file is executed directly
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000)) # Default to 8000 if port is not set
    uvicorn.run(app, host="0.0.0.0", port=port)