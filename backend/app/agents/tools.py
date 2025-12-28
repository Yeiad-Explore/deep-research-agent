"""
Research Tools for LangGraph Agent
Combines Tavily AI Search, YARS Reddit, Azure OpenAI, and web scraping
"""
import logging
from typing import List, Dict, Any, Optional
import asyncio

logger = logging.getLogger(__name__)


class ResearchTools:
    """
    Collection of research tools for the LangGraph agent
    """

    def __init__(self, tavily_client, yars_client, azure_client, web_scraper):
        """
        Initialize research tools

        Args:
            tavily_client: TavilySearchClient instance
            yars_client: YARSRedditClient instance
            azure_client: AzureOpenAIClient instance
            web_scraper: WebScraper instance
        """
        self.tavily = tavily_client
        self.yars = yars_client
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

    async def reddit_post_search(
        self,
        query: str,
        subreddits: Optional[List[str]] = None,
        limit: int = 50,
        time_filter: str = "month"
    ) -> List[Dict[str, Any]]:
        """
        Search Reddit posts using YARS

        Args:
            query: Search query
            subreddits: List of subreddits to search
            limit: Maximum posts
            time_filter: Time filter

        Returns:
            List of Reddit posts
        """
        logger.info(f"Reddit post search: {query} in {subreddits or 'all'}")
        posts = await self.yars.search_posts(
            query,
            subreddits=subreddits,
            limit=limit,
            time_filter=time_filter
        )
        return posts

    async def reddit_comment_search(
        self,
        query: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Search Reddit comments using YARS

        Args:
            query: Search query
            limit: Maximum comments

        Returns:
            List of Reddit comments
        """
        logger.info(f"Reddit comment search: {query}")
        comments = await self.yars.search_comments(query, limit=limit)
        return comments

    async def discover_subreddits(self, topic: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Discover relevant subreddits for a topic

        Args:
            topic: Topic to search
            limit: Maximum subreddits

        Returns:
            List of subreddit information
        """
        logger.info(f"Discovering subreddits for: {topic}")
        subreddits = await self.yars.get_subreddit_recommendations(topic, limit=limit)
        return subreddits

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

    async def analyze_reddit_thread(
        self,
        post_url: str,
        comment_limit: int = 100
    ) -> Dict[str, Any]:
        """
        Deep analysis of a Reddit thread

        Args:
            post_url: Reddit post URL
            comment_limit: Maximum comments to analyze

        Returns:
            Thread analysis with post and comments
        """
        logger.info(f"Analyzing Reddit thread: {post_url}")
        thread_data = await self.yars.get_post_with_comments(post_url, comment_limit)
        return thread_data

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

    async def build_consensus(
        self,
        reddit_summaries: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Build community consensus from Reddit discussions using Azure OpenAI

        Args:
            reddit_summaries: List of Reddit discussion summaries

        Returns:
            Consensus analysis
        """
        logger.info("Building community consensus")

        if not reddit_summaries:
            return {
                "sentiment": "neutral",
                "agreement_level": "unknown",
                "themes": [],
                "majority_opinion": "",
                "minority_opinions": []
            }

        # Combine all Reddit content
        combined_text = "\n\n---\n\n".join([
            f"{s.get('title', '')}\n{s.get('summary', '')}"
            for s in reddit_summaries
        ])

        messages = [
            {
                "role": "system",
                "content": "You analyze community discussions to identify consensus, themes, and diverse opinions. Return as JSON."
            },
            {
                "role": "user",
                "content": f"""Analyze these Reddit discussions and identify:
1. Overall sentiment (positive/negative/neutral/mixed)
2. Agreement level (high/medium/low)
3. Key themes (list)
4. Majority opinion (string)
5. Minority/contrarian opinions (list)

Discussions:
{combined_text}

Return as JSON with keys: sentiment, agreement_level, themes, majority_opinion, minority_opinions"""
            }
        ]

        response = await self.azure.chat_completion(messages, max_completion_tokens=800)

        try:
            import json
            consensus = json.loads(response)
            return consensus
        except:
            return {
                "sentiment": "neutral",
                "agreement_level": "unknown",
                "themes": [],
                "majority_opinion": "Unable to determine consensus",
                "minority_opinions": []
            }

    async def cross_reference(
        self,
        web_summaries: List[Dict[str, Any]],
        reddit_summaries: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Cross-reference information across sources using Azure OpenAI

        Args:
            web_summaries: Web content summaries
            reddit_summaries: Reddit discussion summaries

        Returns:
            Cross-reference analysis with confidence scores
        """
        logger.info("Cross-referencing sources")

        web_text = "\n\n".join([f"[Web] {s.get('summary', '')}" for s in web_summaries])
        reddit_text = "\n\n".join([f"[Reddit] {s.get('summary', '')}" for s in reddit_summaries])

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

REDDIT DISCUSSIONS:
{reddit_text}

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

    async def identify_expert_opinions(
        self,
        comments: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Identify expert opinions from Reddit comments using Azure OpenAI

        Args:
            comments: List of Reddit comments

        Returns:
            List of identified expert opinions
        """
        logger.info("Identifying expert opinions")
        expert_opinions = await self.azure.extract_expert_opinions(comments)
        return expert_opinions

    async def synthesize_report(
        self,
        query: str,
        web_summaries: List[Dict[str, Any]],
        reddit_summaries: List[Dict[str, Any]],
        consensus: Dict[str, Any],
        cross_ref: Dict[str, Any],
        sources: List[Dict[str, Any]]
    ) -> str:
        """
        Generate comprehensive research report using Azure OpenAI

        Args:
            query: Original query
            web_summaries: Web summaries
            reddit_summaries: Reddit summaries
            consensus: Community consensus
            cross_ref: Cross-reference analysis
            sources: All sources

        Returns:
            Final research report
        """
        logger.info("Synthesizing final report")
        report = await self.azure.comprehensive_synthesis(
            query,
            web_summaries,
            reddit_summaries,
            consensus,
            sources
        )
        return report

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
