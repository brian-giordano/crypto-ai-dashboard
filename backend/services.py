import logging
from typing import Dict, Any, Optional, List
from redis import Redis
import redis
from transformers import pipeline
import requests
import json
from cache_utils import CACHE_TTLS, get_cache_key, log_cache_status
import time
from utils import format_large_number, cap_confidence

CRYPTO_KEYWORDS = {
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

class CryptoDataService:
    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client
        self.base_url = "https://api.coingecko.com/api/v3"
        self.last_request_time = 0
        self.min_request_interval = 2

    def _rate_limit(self):
        """Ensure rate limits aren't exceeded"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        self.last_request_time = time.time()

    def extract_crypto_context(self, question: str) -> Optional[str]:
        """Extract cryptocurrency context from the question"""
        question_lower = question.lower()
        for keyword, context in CRYPTO_KEYWORDS.items():
            if keyword in question_lower:
                return context
        return None

    def get_market_data(self, vs_currency: str = "usd", limit: int = 100) -> List[Dict[str, Any]]:
        """Fetch cryptocurrency market data with Redis caching"""
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
        """Fetch coin data by name from CoinGecko"""
        try:
            cache_key = get_cache_key("coin", name)
            cached_data = self.redis_client.get(cache_key)

            if cached_data:
                log_cache_status(cache_key, True)
                return json.loads(cached_data)

            log_cache_status(cache_key, False)
            response = requests.get(
                f"{self.base_url}/coins/markets",
                params={"vs_currency": "usd", "ids": name},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if data:
                    self.redis_client.setex(
                        cache_key,
                        CACHE_TTLS['coin_data'],
                        json.dumps(data[0])
                    )
                    return data[0]
            else:
                logging.error(f"CoinGecko API error: {response.status_code}")

        except requests.exceptions.RequestException as e:
            logging.error(f"Request error in get_coin_by_name: {e}")
        except json.JSONDecodeError as e:
            logging.error(f"JSON decode error in get_coin_by_name: {e}")
        except Exception as e:
            logging.error(f"Unexpected error in get_coin_by_name: {e}")

        return None
    
    def generate_ai_response(self, question: str, sentiment: str, coin_data: Optional[Dict[str, Any]] = None) -> str:
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
                market_data = self.get_market_data(limit=5)
                coins = [f"{i+1}. {coin['name']} (${coin['current_price']})" for i, coin in enumerate(market_data[:5])]
                return f"The top 5 cryptos by market cap are: \n" + "\n".join(coins)

            elif "sentiment" in question_lower or "market" in question_lower:
                market_data = self.get_market_data(limit=10)
                positive_count = sum(1 for coin in market_data if coin["price_change_percentage_24h"] > 0)
                sentiment = "bullish" if positive_count > 5 else "bearish"
                return f"The overall market sentiment appears to be {sentiment}. {positive_count} of the top 10 cryptocurrencies are showing positive price movement in the last 24 hours."

            else:
                return "Based on current market data, cryptocurrencies are showing mixed performance. For specific insights, try asking about a particular coin or market metric."

class SentimentAnalyzer:
    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client
        self.sentiment_pipeline = pipeline("sentiment-analysis",
                                           model="yiyanghkust/finbert-tone")

    def analyze_sentiment_with_context(self, question: str,
                                       context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Analyze sentiment with optional context"""
        cache_key = get_cache_key("sentiment", question)
        cached_result = self.redis_client.get(cache_key)
        if cached_result:
            log_cache_status(cache_key, True)
            return json.loads(cached_result)

        log_cache_status(cache_key, False)
        result = self.sentiment_pipeline(question)[0]

        # Adjust sentiment based on context if provided
        if context and 'price_change_24h' in context:
            price_change = context['price_change_24h']
            if (result['label'] == 'POSITIVE' and price_change > 0) or \
                (result['label'] == 'NEGATIVE' and price_change < 0):
                result['score'] = min(result['score'] * 1.1, 0.95)  # Boost confidence if aligned

        self.redis_client.setex(cache_key, CACHE_TTLS['sentiment'],
                                json.dumps(result))
        return result

    def get_sentiment_explanation(self, sentiment: str, confidence: float,
                                coin_data: Optional[Dict[str, Any]] = None) -> str:
        """Generate an explanation for the sentiment analysis result"""
        confidence = cap_confidence(confidence)
        sentiment_lower = sentiment.lower()

        # Confidence levels
        confidence_desc = "strongly" if confidence > 0.8 else \
                          "moderately" if confidence > 0.6 else \
                          "slightly"

        if not coin_data:
            if sentiment_lower == "positive":
                return f"The sentiment appears {confidence_desc} positive ({confidence:.1%} confidence) based on the optimistic language in your question."
            elif sentiment_lower == "negative":
                return f"The sentiment appears {confidence_desc} negative ({confidence:.1%} confidence) based on the cautious language in your question."
            else:
                return f"The sentiment appears neutral ({confidence:.1%} confidence) based on the balanced language in your question."

        price_change = coin_data.get("price_change_percentage_24h", 0)

        if sentiment_lower == "positive":
            if price_change > 0:
                return f"The sentiment is {confidence_desc} positive ({confidence:.1%} confidence), supported by the {price_change:.2f}% price increase in the last 24 hours."
            else:
                return f"Despite the {abs(price_change):.2f}% price decrease, the sentiment remains {confidence_desc} positive ({confidence:.1%} confidence) based on market indicators."

        elif sentiment_lower == "negative":
            if price_change < 0:
                return f"The sentiment is {confidence_desc} negative ({confidence:.1%} confidence), reflecting the {abs(price_change):.2f}% price decrease in the last 24 hours."
            else:
                return f"Despite the {price_change:.2f}% price increase, the sentiment is {confidence_desc} negative ({confidence:.1%} confidence) based on market concerns."

        else:  # neutral
            if abs(price_change) < 2:
                return f"The market sentiment appears neutral ({confidence:.1%} confidence), with relatively stable price movement ({price_change:.2f}%)."
            else:
                return f"Despite {abs(price_change):.2f}% price {'increase' if price_change > 0 else 'decrease'}, the overall sentiment remains neutral ({confidence:.1%} confidence)."
