# main.py:  - use WebSockets to provide real-time updates to the client
#           - use Celery to offload long-running tasks like AI processing and sentiment analysis
#           - use Redis as both a caching layer and the Celery broker/backend

# Standard imports
import asyncio
import json
import logging
import os
import sys
import time
from typing import Dict, Any, Optional
from urllib.parse import urlparse
from contextlib import contextmanager
from dataclasses import dataclass


# Third-party imports
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import uvicorn
from dotenv import load_dotenv
from celery.result import AsyncResult


# Local imports
from services import CryptoDataService, SentimentAnalyzer, CRYPTO_KEYWORDS
from redis_client import redis_client
from shared_types import QueryRequest, AIResponse
from config import REDIS_URL, FRONTEND_URL
from cache_utils import CACHE_TTLS, get_cache_key, log_cache_status
from tasks import process_question_task

# Load environment variables
# load_dotenv()

# Configuration
# FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
# REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
PRODUCTION_URL = "https://crypto-ai-dashboard-lovat.vercel.app"
# print("FRONTEND_URL: ", FRONTEND_URL)

# For timing process logs
@dataclass
class StepTiming:
    name: str
    start: float
    duration: Optional[float] = None

class ProcessingTimer:
    def __init__(self):
        self.start_time = time.perf_counter()
        self.steps: Dict[str, StepTiming] = {}

    @contextmanager
    def step(self, name: str):
        step_start = time.perf_counter()
        try:
            yield
        finally:
            duration = time.perf_counter() - step_start
            self.steps[name] = StepTiming(name, step_start, duration)

    def log_summary(self):
        total_time = time.perf_counter() - self.start_time
        logging.info(f"Total processing time: {total_time:.3f}s")
        logging.info("Step timing breakdown:")

        for step in self.steps.values():
            step.percentage = (step.duration / total_time) * 100
            logging.info(
                f"  {step.name}: {step.duration:.3f}s ({step.percentage:.1f}%)"
            )

        return {
            'total_time': total_time,
            'steps': {name: step.duration for name, step in self.steps.items()}
        }


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)     # Logs to console (for visibility in Render.)
    ]
)

# FastAPI App main
app = FastAPI()

# Add CORS middleware to allow requests from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        FRONTEND_URL,
        PRODUCTION_URL,
    ], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request timing middlewear
class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response
    
app.add_middleware(TimingMiddleware)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logging.error(f"Unhandled exception: {exc}")
    return {"detail": "An internal error occurred."}

# Initialize the crypto data service
crypto_service = CryptoDataService(redis_client)

# Initialize sentiment analyzer
sentiment_analyzer = SentimentAnalyzer(redis_client)

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
    
# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logging.info(f"Client {client_id} connected")

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logging.info(f"Client {client_id} disconnected")

    async def send_message(self, client_id: str, message: dict):
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_json(message)
                logging.info(f"Message sent to client {client_id}")
            except Exception as e:
                logging.error(f"Error sending message to client {client_id}: {e}")
                await self.disconnect(client_id)

manager = ConnectionManager()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            # Wait for messages from client
            data = await websocket.receive_text()

            # Process the received data
            try:
                # Parse the question
                request_data = json.loads(data)

                # Send processing status
                await manager.send_message(client_id, {
                    "status": "processing",
                    "message": "Processing your questions..."
                })

                # Start the Celery task to process the question
                task = process_question_task.delay(request_data)

                # Use AsyncResult to check task status
                while True:
                    result = AsyncResult(task.id)
                    if result.ready():
                        if result.successful():
                            await manager.send_message(client_id, {
                                "status": "complete",
                                "response": result.result,
                            })
                        else:
                            await manager.send_message(client_id, {
                                "status": "error",
                                "message": "Failed to process your question."
                            })
                        break
                    await asyncio.sleep(1)               # Avoid blocking the event loop

            except Exception as e:
                logging.error(f"Error processing message: {e}")
                await manager.send_message(client_id, {
                    "status": "error",
                    "message": str(e)
                })

    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        logging.error(f"Websocket error: {e}")
        manager.disconnect(client_id)

# Sentiment analysis endpoint
@app.post("/analyze-sentiment/")
async def analyse_sentiment(request: QueryRequest):
    logging.info(f"Received sentiment analysis request: {request.question}")
    result = sentiment_analyzer.analyze_sentiment_with_context(request.question)
    logging.info(f"Sentiment analysis result: {result}")
    return {"sentiment": result["label"].upper(), "score": min(result["score"], 0.95)}

# ask endpoint (AI):    Process user questions about crypto, with sentiment analysis and market data. 
#                       Implements caching, performance monitoring, and error handling. 

@app.post("/ask", response_model=AIResponse)
async def process_question(request: QueryRequest) -> AIResponse:
    """
    Process a user's question about cryptocurrency with sentiment analysis and market data.

    Parameters:
        request (QueryRequest): The question and optional context

    Returns:
        AIResponse: Generated response with sentiment analysis and metrics
    """
    timer = ProcessingTimer()
    
    try:
        # Step 1: Check cache
        cache_key = get_cache_key('full_response', request.question)
        with timer.step("Cache Check"):
            cached_response = redis_client.get(cache_key)
            if cached_response:
                log_cache_status(cache_key, True)
                return AIResponse(**json.loads(cached_response))
            log_cache_status(cache_key, False)

        # Step 2: Start Celery task
        with timer.step("Task Creation"):
            # Create a task to process the question
            task = process_question_task.delay(request.question)
            
            # Wait for the task to complete with a timeout
            try:
                result = task.get(timeout=30)  # 30 seconds timeout
                if result:
                    # Cache the response
                    try:
                        redis_client.setex(
                            cache_key,
                            CACHE_TTLS['sentiment'],
                            json.dumps(result)
                        )
                        logging.info(f"Response cached with key: {cache_key}")
                    except Exception as e:
                        logging.warning(f"Failed to cache response for key {cache_key}: {str(e)}")

                    # Return the response
                    return AIResponse(**result)
                
            except TimeoutError:
                logging.error("Task processing timed out")
                raise HTTPException(
                    status_code=504,
                    detail="Request timed out while processing"
                )
            except Exception as e:
                logging.error(f"Task processing failed: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail="Failed to process request"
                )

    except Exception as e:
        logging.error(f"Error processing question: {request.question}. Error: {str(e)}", exc_info=True)

        # Attempt to serve stale cache in case of error
        try:
            stale_response = redis_client.get(cache_key)
            if stale_response:
                logging.info("Serving stale cached response due to error")
                return AIResponse(**json.loads(stale_response))
        except Exception as cache_error:
            logging.error(f"Failed to retrieve stale cache for key: {cache_key}: {str(cache_error)}")

        # Fallback response
        return AIResponse(
            text="I apologize, but I'm having trouble processing your request at this time. Please try again.",
            sentiment="NEUTRAL",
            confidence=0.5,
            metrics={}
        )
       
# Run the application with Uvicorn if this file is executed directly
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000)) # Default to 8000 if port is not set
    uvicorn.run(app, host="0.0.0.0", port=port, workers=4)