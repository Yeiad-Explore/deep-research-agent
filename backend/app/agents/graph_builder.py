"""
LangGraph Graph Builder for Deep Research Agent
Constructs the research workflow graph with parallel execution
"""
import logging
from langgraph.graph import StateGraph, END
from app.models.schemas import ResearchState
from app.agents.nodes import ResearchNodes
from app.agents.tools import ResearchTools
from app.llm.tavily_client import TavilySearchClient
from app.llm.azure_client import AzureOpenAIClient
from app.scrapers.yars_client import YARSRedditClient
from app.scrapers.web_scraper import WebScraper
from app.config import settings

logger = logging.getLogger(__name__)


def should_continue_research(state: ResearchState) -> str:
    """
    Conditional edge function to determine if research should continue

    Args:
        state: Current research state

    Returns:
        Next node name or END
    """
    is_complete = state.get("research_complete", False)
    iteration = state.get("iteration", 0)
    max_iterations = state.get("max_iterations", 3)

    if is_complete:
        logger.info("Research marked as complete - ending")
        return "end"
    elif iteration >= max_iterations:
        logger.info(f"Max iterations ({max_iterations}) reached - ending")
        return "end"
    else:
        logger.info(f"Research incomplete - continuing (iteration {iteration}/{max_iterations})")
        return "continue"


def build_research_graph():
    """
    Build the LangGraph StateGraph for research workflow

    Returns:
        Compiled graph ready for execution
    """
    logger.info("Building research graph...")

    # Initialize clients
    tavily_client = TavilySearchClient(
        api_key=settings.tavily_api_key
    )

    azure_client = AzureOpenAIClient(
        api_key=settings.azure_openai_api_key,
        endpoint=settings.azure_openai_endpoint,
        deployment_name=settings.azure_openai_deployment_name
    )

    yars_client = YARSRedditClient(
        user_agent="DeepResearchAgent/1.0"
    )

    web_scraper = WebScraper(
        timeout=settings.scrape_timeout,
        max_content_length=settings.max_content_length
    )

    # Initialize tools
    tools = ResearchTools(
        tavily_client=tavily_client,
        yars_client=yars_client,
        azure_client=azure_client,
        web_scraper=web_scraper
    )

    # Initialize nodes
    nodes = ResearchNodes(tools)

    # Create StateGraph
    workflow = StateGraph(ResearchState)

    # Add nodes to graph
    workflow.add_node("query_planner", nodes.query_planner)
    workflow.add_node("multi_source_searcher", nodes.multi_source_searcher)
    workflow.add_node("content_scraper", nodes.content_scraper)
    workflow.add_node("content_analyzer", nodes.content_analyzer)
    workflow.add_node("consensus_builder", nodes.consensus_builder)
    workflow.add_node("cross_reference", nodes.cross_reference_validator)
    workflow.add_node("synthesis", nodes.synthesis_generator)
    workflow.add_node("quality_checker", nodes.quality_checker)
    workflow.add_node("gap_filler", nodes.gap_filler)

    # Define graph flow
    # START → Query Planner
    workflow.set_entry_point("query_planner")

    # Query Planner → Multi-Source Searcher
    workflow.add_edge("query_planner", "multi_source_searcher")

    # Multi-Source Searcher → Content Scraper
    workflow.add_edge("multi_source_searcher", "content_scraper")

    # Content Scraper → Content Analyzer
    workflow.add_edge("content_scraper", "content_analyzer")

    # Content Analyzer → Consensus Builder
    workflow.add_edge("content_analyzer", "consensus_builder")

    # Consensus Builder → Cross-Reference Validator
    workflow.add_edge("consensus_builder", "cross_reference")

    # Cross-Reference → Synthesis Generator
    workflow.add_edge("cross_reference", "synthesis")

    # Synthesis → Quality Checker
    workflow.add_edge("synthesis", "quality_checker")

    # Quality Checker → Conditional (Complete or Continue)
    workflow.add_conditional_edges(
        "quality_checker",
        should_continue_research,
        {
            "end": END,
            "continue": "gap_filler"
        }
    )

    # Gap Filler → Multi-Source Searcher (for next iteration)
    workflow.add_edge("gap_filler", "multi_source_searcher")

    # Compile the graph
    app = workflow.compile()

    logger.info("Research graph built successfully")
    return app


# Global graph instance
research_graph = None


def get_research_graph():
    """
    Get or create the research graph instance

    Returns:
        Compiled research graph
    """
    global research_graph
    if research_graph is None:
        research_graph = build_research_graph()
    return research_graph


async def run_research(query: str, config: dict = None) -> dict:
    """
    Run research using the graph

    Args:
        query: Research query
        config: Research configuration

    Returns:
        Final research state
    """
    logger.info(f"Starting research for: {query}")

    # Initialize state
    initial_state: ResearchState = {
        "query": query,
        "research_config": config or {},
        "max_iterations": config.get("max_iterations", 3) if config else 3,
        "iteration": 0,
        "research_complete": False,
        "errors": [],
        "web_results": [],
        "reddit_posts": [],
        "reddit_comments": [],
        "reddit_threads": [],
        "scraped_web_content": [],
        "reddit_discussions": [],
        "web_summaries": [],
        "reddit_summaries": [],
        "expert_opinions": [],
        "community_consensus": {},
        "cross_reference": {},
        "corroborated_facts": [],
        "contradictions": [],
        "sources": [],
        "confidence_scores": {},
        "search_keywords": [],
        "relevant_subreddits": [],
        "identified_gaps": [],
        "refinement_queries": []
    }

    # Get graph
    graph = get_research_graph()

    # Run graph
    try:
        final_state = await graph.ainvoke(initial_state)
        logger.info("Research completed successfully")
        return final_state
    except Exception as e:
        logger.error(f"Error during research: {e}", exc_info=True)
        raise


async def stream_research(query: str, config: dict = None):
    """
    Stream research progress using graph

    Args:
        query: Research query
        config: Research configuration

    Yields:
        State updates as they occur
    """
    logger.info(f"Starting streaming research for: {query}")

    # Initialize state
    initial_state: ResearchState = {
        "query": query,
        "research_config": config or {},
        "max_iterations": config.get("max_iterations", 3) if config else 3,
        "iteration": 0,
        "research_complete": False,
        "errors": [],
        "web_results": [],
        "reddit_posts": [],
        "reddit_comments": [],
        "reddit_threads": [],
        "scraped_web_content": [],
        "reddit_discussions": [],
        "web_summaries": [],
        "reddit_summaries": [],
        "expert_opinions": [],
        "community_consensus": {},
        "cross_reference": {},
        "corroborated_facts": [],
        "contradictions": [],
        "sources": [],
        "confidence_scores": {},
        "search_keywords": [],
        "relevant_subreddits": [],
        "identified_gaps": [],
        "refinement_queries": []
    }

    # Get graph
    graph = get_research_graph()

    # Stream graph execution
    try:
        async for state in graph.astream(initial_state):
            yield state
    except Exception as e:
        logger.error(f"Error during streaming research: {e}", exc_info=True)
        raise
