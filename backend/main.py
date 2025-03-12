from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import pipeline
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

# Load environment variables
load_dotenv()

# Access environment variables
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")

# Load Redis URL from environment variables
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Parse the Redis URL
parsed_redis_url = urlparse(REDIS_URL)

# Redis Configuration
REDIS_CACHE_TTL = 300 # 5 minutes

# Initialize Redis client
redis_client = Redis(
    host=parsed_redis_url.hostname,
    port=parsed_redis_url.port,
    password=parsed_redis_url.password,
    decode_responses=True
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

def log_memory_usage(stage: str):
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    logging.info(f"{stage} - Memory usage: {memory_info.rss / 1024 / 1024:.2f} MB")

# FastAPI App main
app = FastAPI()

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

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logging.error(f"Unhandled exception: {exc}")
    return {"detail": "An internal error occurred."}

# Initialize the sentiment analysis pipeline, using FinBERT from HuggingFace

# Log memory usage before initializing the pipeline
log_memory_usage("Before initializing sentiment pipeline")
logging.info("Initializing sentiment analysis pipeline...")

sentiment_pipeline = pipeline("sentiment-analysis", model="yiyanghkust/finbert-tone")

# Log memory usage after initializing the pipeline
log_memory_usage("After initializing sentiment pipeline")
logging.info("Sentiment analysis pipeline initialized successfully.")

# Define Pydantic models
class SentimentRequest(BaseModel):
    text: str

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
        """Get market data for top cryptocurrencies"""
        cache_key = f"market_data_{vs_currency}_{limit}"

        # Check if the cached data is still valid
        # if cache_key in self.cache and time.time() < self.cache_expiry.get(cache_key, 0):
        #     print(f"Using cached market data for {cache_key}")
        #     return self.cache[cache_key]

        try:
            # Try to get data from Redis
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                logging.info(f"Cache hit for {cache_key}")
                return json.loads(cached_data)

            # If data is not cached, fetch from API
            self._rate_limit()
            params = {
               "vs_currency": vs_currency,
                "order": "market_cap_desc",
                "per_page": limit,
                "page": 1,
                "sparkline": "true",
                "price_change_percentage": "24h"
            }
            response = requests.get(f"{self.base_url}/coins/markets", params=params)

            # If a rate limit is reached, return chached data if available
            if response.status_code == 429:
                logging.warning("Rate limit reached, checking cache for stale data")
                cached_data = self.redis_client.get(cache_key)
                if cached_data:
                    return json.loads(cached_data)
                return []

            response.raise_for_status()
            data = response.json()

            # Store in Redis with TTL
            self.redis_client.setex(
                cache_key,
                self.default_ttl,
                json.dumps(data)
            )
            logging.info(f"Cached fresh market data for {cache_key}")

            return data
        
        except Exception as e:
            logging.error(f"Error fetching market data: {e}")
            # Attempt to get stale data from cache
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                logging.info(f"Using stale cached data for {cache_key}")
                return json.loads(cached_data)
            return []

    def get_coin_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Find a coin by name or symbol in the top 100"""
        cache_key = f"coin:{name.lower()}"

        # Check if we have cached data that's still valid
        # if cache_key in self.cache and time.time() < self.cache_expiry.get(cache_key, 0):
        #     print(f"Using cached coin data for {name}")
        #     return self.cache[cache_key]


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

            # Try partial match
            if not coin:
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
def format_large_number(num):
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
    """Analyze sentiment with context awareness"""
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

    return {"label": sentiment, "score": confidence}

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

# AI Question endpoint
@app.post("/ask", response_model=AIResponse)
async def process_question(request: QueryRequest):
    try:
        question = request.question

        # Extract crypto context from question
        crypto_context = "the cryptocurrency market"
        for coin in ["bitcoin", "btc", "ethereum", "eth", "ripple", "xrp", "cardano", "ada"]:
            if coin in question.lower():
                crypto_context = coin
                break

        # Get real data for the mentioned crypto
        coin_data = None
        if crypto_context != "the cryptocurrency market":
            coin_data = crypto_service.get_coin_by_name(crypto_context)

        # Perform sentiment analysis
        sentiment_result = analyze_sentiment_with_context(question, coin_data)
        sentiment = sentiment_result["label"]  # Already uppercase from analyze_sentiment_with_context
        confidence = sentiment_result["score"]  # Already capped at 0.95

        # Override sentiment based on price data if available
        if coin_data and "price_change_percentage_24h" in coin_data:
            price_change = coin_data["price_change_percentage_24h"]
            # if the question is about price/trend and we have price data...
            if any(term in question.lower() for term in ["price", "trend", "movement", "going up", "going down"]):
                # Override sentiment based on actual price movement
                if price_change > 3: # Significant positive movement
                    sentiment = "POSITIVE"
                    confidence = min(max(confidence, 0.8), 0.95)  # Between 0.8 and 0.95
                elif price_change < -3: # Significant negative movement
                    sentiment = "NEGATIVE"
                    confidence = min(max(confidence, 0.8), 0.95)
                elif -1 < price_change < 1: # Minimal movement
                    sentiment = "NEUTRAL"
                    confidence = min(max(confidence, 0.8), 0.95)

        # Cap confidence for prediction questions
        if any(term in question.lower() for term in ["predict", "forecast", "future", "next week", "tomorrow"]):
            confidence = min(confidence, 0.7)  # Lower confidence for predictions

        # Generate response based on question and data
        response_text = generate_ai_response(question, sentiment, coin_data)

        # Add sentiment explanation to the response
        sentiment_explanation = get_sentiment_explanation(sentiment, confidence, coin_data)
        response_text += f"\n\n{sentiment_explanation}"

        # Get metrics
        metrics = {}
        if coin_data:
            metrics = {
                "price": f"${coin_data['current_price']}",
                "marketCap": f"${format_large_number(coin_data['market_cap'])}",
                "volume24h": f"${format_large_number(coin_data['total_volume'])}",
                "change24h": f"{coin_data['price_change_percentage_24h']}%"
            }
        else:
            # Use market overview data
            market_data = crypto_service.get_market_data(limit=10)
            if market_data:
                btc = next((coin for coin in market_data if coin["id"] == "bitcoin"), None)
                if btc:
                    metrics = {
                        "price": f"${btc['current_price']}",
                        "marketCap": f"${format_large_number(btc['market_cap'])}",
                        "volume24h": f"${format_large_number(btc['total_volume'])}",
                        "change24h": f"{btc['price_change_percentage_24h']}%"
                    }

        return AIResponse(
            text=response_text,
            sentiment=sentiment,
            confidence=confidence,
            metrics=metrics
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the application with Uvicorn if this file is executed directly
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000)) # Default to 8000 if port is not set
    uvicorn.run(app, host="0.0.0.0", port=port)