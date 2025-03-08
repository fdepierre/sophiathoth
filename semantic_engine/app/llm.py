import httpx
import logging
from typing import List, Dict, Any, Optional
import json

from app.config import settings
from app.embeddings import embedding_service

logger = logging.getLogger(__name__)


class LLMService:
    """Service for interacting with LLMs"""
    
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL
    
    async def generate_response(
        self,
        question: str,
        context: Optional[List[Dict[str, Any]]] = None,
        max_tokens: int = 500
    ) -> Dict[str, Any]:
        """
        Generate a response using LLM
        
        Args:
            question: The question to answer
            context: Optional context for the question
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            Dictionary with response, sources, and confidence
        """
        # Format context if provided
        context_str = ""
        if context:
            context_str = "Context information:\n"
            for i, item in enumerate(context):
                context_str += f"[{i+1}] {item['title']}: {item['content']}\n"
        
        # Create prompt
        prompt = f"""
        You are an AI assistant for a Tender Management System. Your task is to generate a response to a tender question based on the provided context.
        
        {context_str}
        
        Question: {question}
        
        Provide a clear, concise, and accurate response based on the context provided. If the context doesn't contain relevant information, state that you don't have enough information to provide a complete answer.
        
        Response:
        """
        
        try:
            # Call Ollama API
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "num_predict": max_tokens,
                            "temperature": 0.7
                        }
                    },
                    timeout=60.0
                )
                
                response.raise_for_status()
                result = response.json()
                
                # Extract generated text
                generated_text = result.get("response", "")
                
                # Calculate confidence based on context similarity
                confidence = 0.7  # Default confidence
                if context:
                    # Use the highest similarity score from context as confidence
                    confidence = max([item.get("similarity", 0.0) for item in context])
                
                return {
                    "response": generated_text,
                    "sources": context or [],
                    "confidence": confidence
                }
        
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {
                "response": "I'm sorry, I encountered an error while generating a response.",
                "sources": [],
                "confidence": 0.0
            }
    
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of text
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with sentiment analysis
        """
        prompt = f"""
        Analyze the sentiment of the following text. Provide a sentiment score from -1 (very negative) to 1 (very positive), and a brief explanation.
        
        Text: {text}
        
        Format your response as JSON with the following structure:
        {{
            "score": <float between -1 and 1>,
            "sentiment": "<positive|neutral|negative>",
            "explanation": "<brief explanation>"
        }}
        """
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False
                    },
                    timeout=30.0
                )
                
                response.raise_for_status()
                result = response.json()
                
                # Extract generated text and parse JSON
                generated_text = result.get("response", "")
                
                # Find JSON in the response
                try:
                    # Try to extract JSON from the text
                    json_start = generated_text.find("{")
                    json_end = generated_text.rfind("}") + 1
                    
                    if json_start >= 0 and json_end > json_start:
                        json_str = generated_text[json_start:json_end]
                        sentiment_data = json.loads(json_str)
                        return sentiment_data
                    else:
                        # Fallback if JSON parsing fails
                        return {
                            "score": 0.0,
                            "sentiment": "neutral",
                            "explanation": "Unable to parse sentiment from response."
                        }
                except json.JSONDecodeError:
                    return {
                        "score": 0.0,
                        "sentiment": "neutral",
                        "explanation": "Unable to parse sentiment from response."
                    }
        
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {
                "score": 0.0,
                "sentiment": "neutral",
                "explanation": f"Error analyzing sentiment: {str(e)}"
            }


# Create a singleton instance
llm_service = LLMService()
