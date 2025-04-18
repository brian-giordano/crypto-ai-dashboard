from celery_app import celery_app
from redis_client import redis_client
from celery import shared_task
import logging
from services import CryptoDataService, SentimentAnalyzer, CRYPTO_KEYWORDS
from utils import get_coin_metrics, get_market_overview_metrics
from typing import Dict
import time

@shared_task
def process_question_task(question: str) -> dict:
    """
    Celery task to process questions asynchronously.
    This task will call the `process_question` function from `main.py`.
    """
    # from main import process_question           # Lazy import to avoid circular import issue.

    try:
        # Initialize services
        crypto_service = CryptoDataService(redis_client)
        sentiment_analyzer = SentimentAnalyzer(redis_client)

        # Log processing start
        logging.info(f"Processing question: {question}")
        start_time = time.time()

        # Extract context and identify crypto
        crypto_context = "the cryptocurrency market"
        question_lower = question.lower()

        for keyword in CRYPTO_KEYWORDS:
            if keyword in question_lower:
                crypto_context = CRYPTO_KEYWORDS[keyword]
                break

        # # Fetch data
        # metrics = {}
        # coin_data = None
        # market_data = None

        # Fetch data with caching
        metrics = {}
        if crypto_context != "the cryptocurrency market":
            coin_data = crypto_service.get_coin_by_name(crypto_context)
            if coin_data:
                metrics = get_coin_metrics(coin_data)
        else:
            market_data = crypto_service.get_market_data(limit=10)
            if market_data:
                metrics = get_market_overview_metrics(market_data)

        # Get sentiment with caching
        sentiment_result = sentiment_analyzer.analyze_sentiment_with_context(
            question,
            context=coin_data if 'coin_data' in locals() else None
        )

        sentiment = sentiment_result["label"]
        confidence = sentiment_result["score"]

        # Generate response
        response_text = crypto_service.generate_ai_response(question, sentiment, coin_data if 'coin_data' in locals() else None)
        sentiment_explanation = sentiment_analyzer.get_sentiment_explanation(sentiment, confidence, coin_data if 'coin_data' in locals() else None)
        response_text += f"\n\n{sentiment_explanation}"

        # Log processing time
        processing_time = time.time() - start_time
        logging.info(f"Question processed in {processing_time:.2f} seconds")

        # Return response data
        return {
            "text": response_text,
            "sentiment": sentiment,
            "confidence": confidence,
            "metrics": metrics
        }

    
    except Exception as e:
        logging.error(f"Error in process_question_task: {str(e)}")
        raise RuntimeError(f"Error in process_question_task: {str(e)}")

# Start Celery worker
if __name__ == "__main__":
    celery_app.start()