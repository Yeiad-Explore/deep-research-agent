"""
Simplified LangGraph Nodes for Deep Research
Simple 4-node workflow: Plan -> Search -> Scrape -> Answer
"""
import logging
import asyncio
from typing import Dict, Any, List
from app.models.schemas import ResearchState

logger = logging.getLogger(__name__)


class ResearchNodes:
    """
    Simplified collection of LangGraph nodes for research workflow
    """

    def __init__(self, tools):
        """
        Initialize nodes with research tools

        Args:
            tools: ResearchTools instance
        """
        self.tools = tools

    async def query_planner(self, state: ResearchState) -> ResearchState:
        """
        Node 1: Query Planner
        Analyzes query and creates search strategy
        """
        logger.info("=== Query Planner Node ===")

        query = state["query"]
        config = state.get("research_config", {})

        # Use Azure OpenAI to plan research
        messages = [
            {
                "role": "system",
                "content": "You are a research planning expert. Analyze queries and determine optimal search keywords. Return as JSON."
            },
            {
                "role": "user",
                "content": f"""Analyze this query and create a search plan:

Query: {query}

Return JSON with:
{{
  "search_keywords": ["keyword1", "keyword2", ...]
}}"""
            }
        ]

        plan_response = await self.tools.azure.chat_completion(
            messages, max_completion_tokens=500
        )

        # Parse plan
        try:
            import json
            research_plan = json.loads(plan_response)
        except:
            research_plan = {
                "search_keywords": [query]
            }

        # Update state
        state["search_keywords"] = research_plan.get("search_keywords", [query])

        logger.info(f"Plan created: {len(state['search_keywords'])} keywords")

        return state

    async def multi_source_searcher(self, state: ResearchState) -> ResearchState:
        """
        Node 2: Web Searcher
        Searches the web using Tavily AI
        """
        logger.info("=== Web Searcher Node ===")

        query = state["query"]
        keywords = state.get("search_keywords", [query])
        config = state.get("research_config", {})

        # Web search
        search_query = " ".join(keywords[:3])  # Use first 3 keywords
        num_results = config.get("max_web_results", 15)

        try:
            web_results = await self.tools.web_search(search_query, num_results)
        except Exception as e:
            logger.error(f"Error in web search: {e}")
            web_results = []

        # Update state
        state["web_results"] = web_results

        # Build sources list
        sources = []
        for result in web_results:
            sources.append({
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "type": "web"
            })

        state["sources"] = sources

        logger.info(f"Search complete: {len(web_results)} web results")

        return state

    async def content_scraper(self, state: ResearchState) -> ResearchState:
        """
        Node 3: Content Scraper
        Scrapes full content from URLs
        """
        logger.info("=== Content Scraper Node ===")

        web_results = state.get("web_results", [])

        # Extract URLs from top 10 web results
        urls = [result.get("url") for result in web_results[:10] if result.get("url")]

        # Scrape all URLs in parallel
        scraped_content = await self.tools.scrape_urls(urls)

        state["scraped_web_content"] = scraped_content

        logger.info(f"Scraped {len(scraped_content)} web pages successfully")

        return state

    async def answer_generator(self, state: ResearchState) -> ResearchState:
        """
        Node 4: Answer Generator
        Combines all research and generates a single AI answer
        """
        logger.info("=== Answer Generator Node ===")

        query = state["query"]

        # Combine all content
        web_content = state.get("scraped_web_content", [])

        # Build combined content string
        all_content_parts = []

        # Add web content
        for item in web_content:
            if item.get("success"):
                title = item.get("title", "Unknown")
                content = item.get("content", "")[:3000]  # Limit each source
                all_content_parts.append(f"WEB SOURCE: {title}\n{content}")

        all_content = "\n\n---\n\n".join(all_content_parts)

        # Generate answer using all gathered content
        answer = await self.tools.azure.generate_answer(
            query=query,
            all_content=all_content,
            sources=state.get("sources", [])
        )

        state["final_response"] = answer
        state["all_content"] = all_content
        state["research_complete"] = True

        logger.info(f"Answer generated: {len(answer)} characters")

        return state

    # Simplified quality checker - always returns "end" to complete in one iteration
    async def quality_checker(self, state: ResearchState) -> ResearchState:
        """
        Simplified Quality Checker - always marks research as complete
        """
        logger.info("=== Quality Checker: Research Complete ===")
        state["research_complete"] = True
        return state
