"""
Parallel.ai Unified Client for Search and LLM Operations
"""
import httpx
import logging
from typing import List, Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class ParallelAIClient:
    """
    Unified client for Parallel.ai API providing both web search and LLM capabilities
    """

    def __init__(self, api_key: str, base_url: str = "https://api.parallel.ai/v1"):
        """
        Initialize Parallel.ai client

        Args:
            api_key: Parallel.ai API key
            base_url: Base URL for Parallel.ai API
        """
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def web_search(
        self,
        query: str,
        num_results: int = 10,
        filter_domains: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform web search using Parallel.ai

        Args:
            query: Search query string
            num_results: Maximum number of results to return
            filter_domains: Optional list of domains to prioritize

        Returns:
            List of search results with metadata
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                payload = {
                    "query": query,
                    "num_results": num_results,
                    "filter_domains": filter_domains or []
                }

                response = await client.post(
                    f"{self.base_url}/search",
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()

                data = response.json()
                results = data.get("results", [])

                # Standardize result format
                formatted_results = []
                for result in results:
                    formatted_results.append({
                        "title": result.get("title", ""),
                        "url": result.get("url", ""),
                        "snippet": result.get("snippet", ""),
                        "domain": result.get("domain", ""),
                        "published_date": result.get("date", None),
                        "score": result.get("relevance_score", 0.0)
                    })

                logger.info(f"Web search completed: {len(formatted_results)} results for '{query}'")
                return formatted_results

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error during web search: {e}")
            raise
        except Exception as e:
            logger.error(f"Error during web search: {e}")
            return []

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "default",
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> str:
        """
        Generate chat completion using Parallel.ai LLM

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model name to use
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature

        Returns:
            Generated text response
        """
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                payload = {
                    "model": model,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature
                }

                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()

                data = response.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")

                logger.info(f"Chat completion generated: {len(content)} characters")
                return content

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error during chat completion: {e}")
            raise
        except Exception as e:
            logger.error(f"Error during chat completion: {e}")
            return ""

    async def summarize_content(
        self,
        content: str,
        max_tokens: int = 500
    ) -> str:
        """
        Summarize long content using Parallel.ai

        Args:
            content: Text content to summarize
            max_tokens: Maximum length of summary

        Returns:
            Summarized text
        """
        messages = [
            {
                "role": "system",
                "content": "You are a professional summarizer. Create concise, accurate summaries that capture key points and facts."
            },
            {
                "role": "user",
                "content": f"Summarize the following content, focusing on key facts and main points:\n\n{content}"
            }
        ]

        return await self.chat_completion(messages, max_tokens=max_tokens, temperature=0.5)

    async def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract key entities, facts, and dates from text

        Args:
            text: Input text

        Returns:
            Dictionary with extracted entities
        """
        messages = [
            {
                "role": "system",
                "content": "You are an entity extraction expert. Extract key entities, facts, and dates from text. Return as JSON."
            },
            {
                "role": "user",
                "content": f"Extract entities (people, organizations, locations), key facts, and dates from:\n\n{text}\n\nReturn as JSON with keys: people, organizations, locations, facts, dates"
            }
        ]

        response = await self.chat_completion(messages, max_tokens=800, temperature=0.3)

        # Parse JSON response
        try:
            import json
            return json.loads(response)
        except json.JSONDecodeError:
            logger.warning("Failed to parse entity extraction response as JSON")
            return {
                "people": [],
                "organizations": [],
                "locations": [],
                "facts": [],
                "dates": []
            }

    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of text (useful for Reddit/social content)

        Args:
            text: Input text

        Returns:
            Sentiment analysis results
        """
        messages = [
            {
                "role": "system",
                "content": "You are a sentiment analysis expert. Analyze the sentiment and tone of text. Return as JSON."
            },
            {
                "role": "user",
                "content": f"Analyze sentiment of this text. Return JSON with: sentiment (positive/negative/neutral), confidence (0-1), tone (professional/casual/aggressive/etc):\n\n{text}"
            }
        ]

        response = await self.chat_completion(messages, max_tokens=200, temperature=0.3)

        try:
            import json
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "sentiment": "neutral",
                "confidence": 0.5,
                "tone": "unknown"
            }
