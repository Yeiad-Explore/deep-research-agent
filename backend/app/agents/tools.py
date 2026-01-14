"""
Research Tools for LangGraph Agent
Combines Tavily AI Search, Azure OpenAI, and web scraping
"""
import logging
from typing import List, Dict, Any, Optional
import asyncio

logger = logging.getLogger(__name__)


class ResearchTools:
    """
    Collection of research tools for the LangGraph agent
    """

    def __init__(self, tavily_client, azure_client, web_scraper):
        """
        Initialize research tools

        Args:
            tavily_client: TavilySearchClient instance
            azure_client: AzureOpenAIClient instance
            web_scraper: WebScraper instance
        """
        self.tavily = tavily_client
        self.azure = azure_client
        self.scraper = web_scraper

    async def web_search(self, query: str, num_results: int = 15) -> List[Dict[str, Any]]:
        """
        Search the web using Tavily AI

        Args:
            query: Search query
            num_results: Maximum number of results

        Returns:
            List of search results
        """
        logger.info(f"Web search (Tavily): {query}")
        results = await self.tavily.web_search(query, num_results=num_results, search_depth="advanced")
        return results

    async def scrape_urls(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        Scrape content from multiple URLs concurrently

        Args:
            urls: List of URLs to scrape

        Returns:
            List of scraped content
        """
        logger.info(f"Scraping {len(urls)} URLs")
        results = await self.scraper.scrape_multiple(urls)
        return [r for r in results if r.get("success", False)]

    async def summarize_content(
        self,
        content: str,
        max_completion_tokens: int = 500
    ) -> str:
        """
        Summarize content using Azure OpenAI

        Args:
            content: Text to summarize
            max_completion_tokens: Maximum summary length

        Returns:
            Summary text
        """
        logger.info(f"Summarizing content ({len(content)} chars)")

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

        summary = await self.azure.chat_completion(messages, max_completion_tokens=max_completion_tokens)
        return summary

    async def extract_facts(self, text: str) -> Dict[str, List[str]]:
        """
        Extract entities and facts from text using Azure OpenAI

        Args:
            text: Input text

        Returns:
            Dictionary of extracted entities
        """
        logger.info("Extracting facts from text")

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

        response = await self.azure.chat_completion(messages, max_completion_tokens=800)

        try:
            import json
            return json.loads(response)
        except:
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
        Analyze sentiment of text using Azure OpenAI

        Args:
            text: Input text

        Returns:
            Sentiment analysis results
        """
        logger.info("Analyzing sentiment")

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

        response = await self.azure.chat_completion(messages, max_completion_tokens=200)

        try:
            import json
            return json.loads(response)
        except:
            return {
                "sentiment": "neutral",
                "confidence": 0.5,
                "tone": "unknown"
            }

    async def cross_reference(
        self,
        web_summaries: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Cross-reference information across web sources using Azure OpenAI

        Args:
            web_summaries: Web content summaries

        Returns:
            Cross-reference analysis with confidence scores
        """
        logger.info("Cross-referencing sources")

        web_text = "\n\n".join([f"[Web] {s.get('summary', '')}" for s in web_summaries])

        messages = [
            {
                "role": "system",
                "content": "You cross-reference information from multiple sources, identify contradictions, and assess confidence. Return as JSON."
            },
            {
                "role": "user",
                "content": f"""Cross-reference these sources and identify:
1. Corroborated facts (list of facts supported by multiple sources)
2. Contradictions (list of conflicting information)
3. Unique insights (information from single sources)
4. Overall confidence (high/medium/low)

WEB SOURCES:
{web_text}

Return as JSON with keys: corroborated_facts, contradictions, unique_insights, overall_confidence"""
            }
        ]

        response = await self.azure.chat_completion(messages, max_completion_tokens=1000)

        try:
            import json
            return json.loads(response)
        except:
            return {
                "corroborated_facts": [],
                "contradictions": [],
                "unique_insights": [],
                "overall_confidence": "medium"
            }

    async def identify_gaps(
        self,
        query: str,
        current_synthesis: str,
        sources: List[str]
    ) -> List[str]:
        """
        Identify gaps in research using Azure OpenAI

        Args:
            query: Original query
            current_synthesis: Current findings
            sources: Sources consulted

        Returns:
            List of refined search queries
        """
        logger.info("Identifying research gaps")
        gaps = await self.azure.analyze_gaps(query, current_synthesis, sources)
        return gaps
