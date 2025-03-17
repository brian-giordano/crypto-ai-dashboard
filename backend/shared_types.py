from pydantic import BaseModel
from typing import Dict, Any, Optional

class QueryRequest(BaseModel):
    """
    Represents a request to query the AI model.
    """
    question: str

class AIResponse(BaseModel):
    """
    Represents the AI's response, including text, sentiment, and metrics.
    """
    text: str
    sentiment: Optional[str] = None
    confidence: Optional[float] = None
    metrics: Optional[Dict[str, str]] = None