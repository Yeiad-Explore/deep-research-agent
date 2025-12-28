"""
Tavily AI Search Client
High-quality AI-powered search specifically designed for LLM applications
"""
import logging
from typing import List, Dict, Any, Optional
from tavily import TavilyClient

logger = logging.getLogger(__name__)


class TavilySearchClient:
    """
    Tavily AI search client for high-quality web search results
    """

    def __init__(self, api_key: str):
        """
        Initialize Tavily client

        Args:
            api_key: Tavily API key
        """
        self.client = TavilyClient(api_key=api_key)

    async def web_search(
        self,
        query: str,
        num_results: int = 10,
        search_depth: str = "advanced",
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform web search using Tavily AI

        Args:
            query: Search query string
            num_results: Maximum number of results (max 20 for advanced)
            search_depth: "basic" or "advanced" (advanced is more thorough)
            include_domains: Optional list of domains to include
            exclude_domains: Optional list of domains to exclude

        Returns:
            List of search results with metadata
        """
        try:
            # Tavily search is synchronous, but we wrap it for async compatibility
            response = self.client.search(
                query=query,
                max_results=min(num_results, 20),
                search_depth=search_depth,
                include_domains=include_domains or [],
                exclude_domains=exclude_domains or []
            )

            results = response.get("results", [])

            # Standardize result format
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "snippet": result.get("content", ""),  # Tavily provides full content
                    "domain": self._extract_domain(result.get("url", "")),
                    "published_date": result.get("published_date", None),
                    "score": result.get("score", 0.0)
                })

            logger.info(f"Tavily search completed: {len(formatted_results)} results for '{query}'")
            return formatted_results

        except Exception as e:
            logger.error(f"Error during Tavily search: {e}")
            return []

    async def search_with_context(
        self,
        query: str,
        num_results: int = 5
    ) -> Dict[str, Any]:
        """
        Search and get AI-generated context (Tavily's special feature)

        Args:
            query: Search query
            num_results: Maximum results

        Returns:
            Dictionary with results and AI-generated context
        """
        try:
            response = self.client.search(
                query=query,
                max_results=num_results,
                search_depth="advanced",
                include_answer=True  # Get AI-generated answer
            )

            return {
                "results": response.get("results", []),
                "answer": response.get("answer", ""),  # AI-generated summary
                "query": query
            }

        except Exception as e:
            logger.error(f"Error during Tavily context search: {e}")
            return {"results": [], "answer": "", "query": query}

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc
        except:
            return ""
