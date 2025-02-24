from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline

app = FastAPI()

# Initialize the sentiment analysis pipeline
sentiment_pipeline = pipeline("sentiment-analysis")

# Define a Pydantic model for the input data
class SentimentRequest(BaseModel):
    text: str

# Basic route
@app.get("/")
async def read_root():
    return {"message": "Welcome to the Crypto AI Dashboard Backend!"}

# Sentiment analysis endpoint
@app.post("/analyze-sentiment/")
async def analyse_sentiment(request: SentimentRequest):
    result = sentiment_pipeline(request.text)
    return {"sentiment": result[0]["label"], "score": result[0]["score"]}