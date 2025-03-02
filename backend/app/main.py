from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import pipeline
from fastapi.middleware.cors import CORSMiddleware
import requests
from typing import Dict, Any, Optional, List

app = FastAPI()

# Add CORS middleware to allow requests from frontend
app.add_middleware(
    CORSMiddleware, 
    allow_origins=["http://localhost:3000", "https://crypto-ai-dashboard-lovat.vercel.app"], # Removed trailing slash
    allow_credentials=True, 
    allow_methods=["*"], 
    allow_headers=["*"],
)

# Initialize the sentiment analysis pipeline
sentiment_pipeline = pipeline("sentiment-analysis")

# Define Pydantic models
class SentimentRequest(BaseModel):
    text: str

class QueryRequest(BaseModel):
    question: str  # Changed from 'text' to 'question' to match your endpoint
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

    def get_market_data(self, vs_currency: str = "usd", limit: int = 100) -> List[Dict[str, Any]]:
        """Get market data for top cryptocurrencies"""
        try:
            params = {
               "vs_currency": vs_currency,
                "order": "market_cap_desc",
                "per_page": limit,
                "page": 1,
                "sparkline": True,
                "price_change_percentage": "24h" 
            }
            response = requests.get(f"{self.base_url}/coins/markets", params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching market data: {e}")
            return []
        
    def get_coin_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Find a coin by name or symbol in the top 100"""
        try:
            market_data = self.get_market_data(limit=100)
            name_lower = name.lower()

            # Try exact match
            for coin in market_data:
                if coin["id"].lower() == name_lower or coin["symbol"].lower() == name_lower:
                    return coin
                
            # Try partial match
            for coin in market_data:
                if name_lower in coin["id"].lower() or name_lower in coin["symbol"].lower():
                    return coin
                
            return None
        except Exception as e:
            print(f"Error finding coin: {e}")
            return None
        
# Initialize the crypto data service
crypto_service = CryptoDataService()

# Basic route
@app.get("/")
async def read_root():
    return {"message": "Welcome to the Crypto AI Dashboard Backend!"}

# Sentiment analysis endpoint
@app.post("/analyze-sentiment/")
async def analyse_sentiment(request: SentimentRequest):
    result = sentiment_pipeline(request.text)
    return {"sentiment": result[0]["label"], "score": result[0]["score"]}

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

    if coin_data:
        coin_name = coin_data["name"]
        price_change = coin_data["price_change_percentage_24h"]
        price_direction = "up" if price_change > 0 else "down"

        if "trend" in question_lower or "price" in question_lower:
            return f"{coin_name} is trending {price_direction} {abs(price_change):.2f}% in the last 24 hours. The current price is ${coin_data['current_price']}"
        
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

# AI Question endpoint - changed to /ask to match your Next.js API route
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
        sentiment_result = sentiment_pipeline(question)
        sentiment = sentiment_result[0]["label"]
        confidence = sentiment_result[0]["score"]

        # Generate response based on question and data
        response_text = generate_ai_response(question, sentiment, coin_data)

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
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)