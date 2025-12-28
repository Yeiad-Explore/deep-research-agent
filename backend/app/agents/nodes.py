"""
LangGraph Agent Nodes for Deep Research
Each node performs a specific stage in the research pipeline
"""
import logging
import asyncio
from typing import Dict, Any, List
from app.models.schemas import ResearchState

logger = logging.getLogger(__name__)


class ResearchNodes:
    """
    Collection of LangGraph nodes for research workflow
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
        Node 1: Intelligent Query Planner
        Analyzes query and creates research strategy
        """
        logger.info("=== Query Planner Node ===")

        query = state["query"]
        config = state.get("research_config", {})

        # Use Azure OpenAI to analyze query and plan research
        messages = [
            {
                "role": "system",
                "content": """You are a research planning expert. Analyze queries and create comprehensive research strategies.
You determine:
1. Search keywords for web search
2. Whether Reddit is needed (for opinions, experiences, current discussions)
3. Relevant subreddits to search
4. Sub-questions to answer
5. Research approach"""
            },
            {
                "role": "user",
                "content": f"""Analyze this research query and create a research plan:

Query: {query}

Return JSON with:
{{
  "search_keywords": ["keyword1", "keyword2", ...],
  "needs_reddit": true/false,
  "suggested_subreddits": ["sub1", "sub2", ...],
  "sub_questions": ["question1", "question2", ...],
  "research_approach": "description of approach"
}}"""
            }
        ]

        plan_response = await self.tools.azure.chat_completion(
            messages, max_completion_tokens=800
        )

        # Parse plan
        try:
            import json
            research_plan = json.loads(plan_response)
        except:
            research_plan = {
                "search_keywords": [query],
                "needs_reddit": config.get("include_reddit", True),
                "suggested_subreddits": config.get("subreddits", []),
                "sub_questions": [query],
                "research_approach": "comprehensive web and community search"
            }

        # Update state
        state["research_plan"] = research_plan
        state["search_keywords"] = research_plan.get("search_keywords", [query])
        state["relevant_subreddits"] = (
            config.get("subreddits") or research_plan.get("suggested_subreddits", [])
        )
        state["iteration"] = state.get("iteration", 0)

        logger.info(f"Research plan created: {len(state['search_keywords'])} keywords, "
                   f"{len(state['relevant_subreddits'])} subreddits")

        return state

    async def multi_source_searcher(self, state: ResearchState) -> ResearchState:
        """
        Node 2: Parallel Multi-Source Searcher
        Searches web and Reddit concurrently
        """
        logger.info("=== Multi-Source Searcher Node ===")

        query = state["query"]
        keywords = state.get("search_keywords", [query])
        subreddits = state.get("relevant_subreddits", [])
        config = state.get("research_config", {})

        # Prepare parallel search tasks
        tasks = []

        # Web search (Parallel.ai)
        primary_keyword = keywords[0] if keywords else query
        tasks.append(self.tools.web_search(
            primary_keyword,
            num_results=config.get("max_web_results", 15)
        ))

        # Reddit post search (YARS)
        if config.get("include_reddit", True):
            tasks.append(self.tools.reddit_post_search(
                query,
                subreddits=subreddits if subreddits else None,
                limit=config.get("max_reddit_posts", 50),
                time_filter=config.get("time_filter", "month")
            ))

            # Reddit comment search
            tasks.append(self.tools.reddit_comment_search(
                query,
                limit=30
            ))

            # Subreddit discovery if none specified
            if not subreddits:
                tasks.append(self.tools.discover_subreddits(query, limit=5))
        else:
            # Append empty results for Reddit if disabled
            tasks.extend([asyncio.sleep(0, result=[]), asyncio.sleep(0, result=[])])
            tasks.append(asyncio.sleep(0, result=[]))

        # Execute all searches in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        web_results = results[0] if not isinstance(results[0], Exception) else []
        reddit_posts = results[1] if len(results) > 1 and not isinstance(results[1], Exception) else []
        reddit_comments = results[2] if len(results) > 2 and not isinstance(results[2], Exception) else []
        discovered_subs = results[3] if len(results) > 3 and not isinstance(results[3], Exception) else []

        # Update state
        state["web_results"] = web_results
        state["reddit_posts"] = reddit_posts
        state["reddit_comments"] = reddit_comments

        # Add discovered subreddits
        if discovered_subs and not subreddits:
            state["relevant_subreddits"] = [s.get("name") for s in discovered_subs[:5]]

        logger.info(f"Search complete: {len(web_results)} web, {len(reddit_posts)} posts, "
                   f"{len(reddit_comments)} comments")

        return state

    async def content_scraper(self, state: ResearchState) -> ResearchState:
        """
        Node 3: Content Scraper
        Scrapes content from web URLs and Reddit threads
        """
        logger.info("=== Content Scraper Node ===")

        web_results = state.get("web_results", [])
        reddit_posts = state.get("reddit_posts", [])

        # Prepare scraping tasks
        tasks = []

        # Scrape top web URLs
        web_urls = [r.get("url") for r in web_results[:10] if r.get("url")]
        if web_urls:
            tasks.append(self.tools.scrape_urls(web_urls))

        # Scrape top Reddit threads
        reddit_urls = [p.get("url") for p in reddit_posts[:5] if p.get("url") and p.get("num_comments", 0) > 10]
        reddit_thread_tasks = [
            self.tools.analyze_reddit_thread(url, comment_limit=50)
            for url in reddit_urls
        ]
        tasks.extend(reddit_thread_tasks)

        # Execute scraping in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        scraped_web = results[0] if results and not isinstance(results[0], Exception) else []
        reddit_threads = [r for r in results[1:] if not isinstance(r, Exception) and r.get("post")]

        state["scraped_web_content"] = scraped_web
        state["reddit_threads"] = reddit_threads

        logger.info(f"Scraping complete: {len(scraped_web)} web pages, {len(reddit_threads)} threads")

        return state

    async def content_analyzer(self, state: ResearchState) -> ResearchState:
        """
        Node 4: Multi-Source Content Analyzer
        Analyzes and summarizes all content
        """
        logger.info("=== Content Analyzer Node ===")

        scraped_web = state.get("scraped_web_content", [])
        reddit_threads = state.get("reddit_threads", [])

        # Analyze web content
        web_summary_tasks = [
            self.tools.summarize_content(content.get("content", ""), max_completion_tokens=500)
            for content in scraped_web if content.get("content")
        ]

        # Analyze Reddit threads
        reddit_summary_tasks = []
        for thread in reddit_threads:
            post = thread.get("post", {})
            comments = thread.get("comments", [])
            combined = f"{post.get('title', '')}\n{post.get('body', '')}\n\nTop Comments:\n"
            combined += "\n".join([c.get("body", "")[:500] for c in comments[:10]])
            reddit_summary_tasks.append(
                self.tools.summarize_content(combined, max_completion_tokens=500)
            )

        # Execute all summarizations in parallel
        all_tasks = web_summary_tasks + reddit_summary_tasks
        if not all_tasks:
            state["web_summaries"] = []
            state["reddit_summaries"] = []
            return state

        summaries = await asyncio.gather(*all_tasks, return_exceptions=True)

        # Separate results
        web_count = len(web_summary_tasks)
        web_summaries = []
        reddit_summaries = []

        for i, summary in enumerate(summaries):
            if isinstance(summary, Exception):
                continue

            if i < web_count:
                web_summaries.append({
                    "title": scraped_web[i].get("title", ""),
                    "url": scraped_web[i].get("url", ""),
                    "summary": summary,
                    "source_type": "web"
                })
            else:
                reddit_idx = i - web_count
                if reddit_idx < len(reddit_threads):
                    thread = reddit_threads[reddit_idx]
                    reddit_summaries.append({
                        "title": thread.get("post", {}).get("title", ""),
                        "url": thread.get("post", {}).get("url", ""),
                        "summary": summary,
                        "source_type": "reddit",
                        "num_comments": thread.get("total_comments", 0)
                    })

        state["web_summaries"] = web_summaries
        state["reddit_summaries"] = reddit_summaries

        logger.info(f"Analysis complete: {len(web_summaries)} web summaries, "
                   f"{len(reddit_summaries)} reddit summaries")

        return state

    async def consensus_builder(self, state: ResearchState) -> ResearchState:
        """
        Node 5: Reddit Community Consensus Builder
        Builds consensus from Reddit discussions
        """
        logger.info("=== Consensus Builder Node ===")

        reddit_summaries = state.get("reddit_summaries", [])
        reddit_comments = state.get("reddit_comments", [])

        if not reddit_summaries and not reddit_comments:
            state["community_consensus"] = {
                "sentiment": "neutral",
                "agreement_level": "unknown",
                "themes": []
            }
            return state

        # Build consensus
        consensus = await self.tools.build_consensus(reddit_summaries)

        # Extract expert opinions from comments
        expert_opinions = await self.tools.identify_expert_opinions(reddit_comments)

        state["community_consensus"] = consensus
        state["expert_opinions"] = expert_opinions

        logger.info(f"Consensus built: {consensus.get('sentiment')} sentiment, "
                   f"{len(expert_opinions)} expert opinions")

        return state

    async def cross_reference_validator(self, state: ResearchState) -> ResearchState:
        """
        Node 6: Cross-Reference Validator
        Cross-references information across sources
        """
        logger.info("=== Cross-Reference Validator Node ===")

        web_summaries = state.get("web_summaries", [])
        reddit_summaries = state.get("reddit_summaries", [])

        if not web_summaries and not reddit_summaries:
            state["cross_reference"] = {}
            return state

        # Cross-reference sources
        cross_ref = await self.tools.cross_reference(web_summaries, reddit_summaries)

        state["cross_reference"] = cross_ref
        state["corroborated_facts"] = cross_ref.get("corroborated_facts", [])
        state["contradictions"] = cross_ref.get("contradictions", [])

        logger.info(f"Cross-reference complete: {len(state['corroborated_facts'])} corroborated facts, "
                   f"{len(state['contradictions'])} contradictions")

        return state

    async def synthesis_generator(self, state: ResearchState) -> ResearchState:
        """
        Node 7: Comprehensive Synthesis Generator
        Generates final research report
        """
        logger.info("=== Synthesis Generator Node ===")

        query = state["query"]
        web_summaries = state.get("web_summaries", [])
        reddit_summaries = state.get("reddit_summaries", [])
        consensus = state.get("community_consensus", {})
        cross_ref = state.get("cross_reference", {})

        # Collect all sources
        sources = []
        for ws in web_summaries:
            sources.append({"type": "web", "title": ws.get("title"), "url": ws.get("url")})
        for rs in reddit_summaries:
            sources.append({"type": "reddit", "title": rs.get("title"), "url": rs.get("url")})

        # Generate comprehensive synthesis
        synthesis = await self.tools.synthesize_report(
            query,
            web_summaries,
            reddit_summaries,
            consensus,
            cross_ref,
            sources
        )

        state["final_synthesis"] = synthesis
        state["sources"] = sources
        state["confidence_scores"] = {
            "overall": cross_ref.get("overall_confidence", "medium"),
            "web_sources": len(web_summaries),
            "reddit_sources": len(reddit_summaries),
            "corroboration": len(state.get("corroborated_facts", []))
        }

        logger.info(f"Synthesis complete: {len(synthesis)} characters")

        return state

    async def quality_checker(self, state: ResearchState) -> ResearchState:
        """
        Node 8: Quality Checker & Iteration Decider
        Evaluates research quality and decides if more iteration needed
        """
        logger.info("=== Quality Checker Node ===")

        iteration = state.get("iteration", 0)
        max_iterations = state.get("max_iterations", 3)
        web_summaries = state.get("web_summaries", [])
        reddit_summaries = state.get("reddit_summaries", [])
        synthesis = state.get("final_synthesis", "")

        # Check quality criteria
        has_sufficient_sources = len(web_summaries) >= 3
        has_diverse_sources = len(web_summaries) > 0 and len(reddit_summaries) > 0
        has_content = len(synthesis) > 500

        # Decide if complete
        if iteration >= max_iterations:
            state["research_complete"] = True
            logger.info("Max iterations reached - marking complete")
        elif has_sufficient_sources and has_diverse_sources and has_content:
            state["research_complete"] = True
            logger.info("Quality criteria met - marking complete")
        else:
            state["research_complete"] = False
            logger.info(f"Quality check: sources={has_sufficient_sources}, "
                       f"diverse={has_diverse_sources}, content={has_content}")

        return state

    async def gap_filler(self, state: ResearchState) -> ResearchState:
        """
        Node 9: Gap Filler
        Identifies gaps and generates refined queries for next iteration
        """
        logger.info("=== Gap Filler Node ===")

        query = state["query"]
        synthesis = state.get("final_synthesis", "")
        sources = [s.get("title", "") for s in state.get("sources", [])]

        # Identify gaps
        gaps = await self.tools.identify_gaps(query, synthesis, sources)

        state["identified_gaps"] = gaps
        state["refinement_queries"] = gaps
        state["iteration"] = state.get("iteration", 0) + 1

        logger.info(f"Gaps identified: {len(gaps)}")

        return state
