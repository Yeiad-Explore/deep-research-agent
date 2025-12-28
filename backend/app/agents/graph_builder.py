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
        user_agent="DeepResearchAgent/1.0",
        request_delay=settings.reddit_request_delay
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

    # Add nodes to graph (4 nodes - simplified)
    workflow.add_node("query_planner", nodes.query_planner)
    workflow.add_node("multi_source_searcher", nodes.multi_source_searcher)
    workflow.add_node("content_scraper", nodes.content_scraper)
    workflow.add_node("answer_generator", nodes.answer_generator)

    # Define simplified graph flow (no iteration loop)
    # START → Query Planner
    workflow.set_entry_point("query_planner")

    # Query Planner → Multi-Source Searcher
    workflow.add_edge("query_planner", "multi_source_searcher")

    # Multi-Source Searcher → Content Scraper
    workflow.add_edge("multi_source_searcher", "content_scraper")

    # Content Scraper → Answer Generator
    workflow.add_edge("content_scraper", "answer_generator")

    # Answer Generator → END (always complete in one pass)
    workflow.add_edge("answer_generator", END)

    # Compile the graph with recursion limit
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

    # Initialize simplified state
    initial_state: ResearchState = {
        "query": query,
        "research_config": config or {},
        "research_complete": False,
        "errors": [],
        "web_results": [],
        "reddit_posts": [],
        "reddit_comments": [],
        "scraped_web_content": [],
        "sources": [],
        "search_keywords": [],
        "relevant_subreddits": [],
        "all_content": "",
        "final_response": ""
    }

    # Get graph
    graph = get_research_graph()

    # Run graph with recursion limit
    try:
        final_state = await graph.ainvoke(
            initial_state,
            config={"recursion_limit": settings.langgraph_recursion_limit}
        )
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

    # Initialize simplified state
    initial_state: ResearchState = {
        "query": query,
        "research_config": config or {},
        "research_complete": False,
        "errors": [],
        "web_results": [],
        "reddit_posts": [],
        "reddit_comments": [],
        "scraped_web_content": [],
        "sources": [],
        "search_keywords": [],
        "relevant_subreddits": [],
        "all_content": "",
        "final_response": ""
    }

    # Get graph
    graph = get_research_graph()

    # Stream graph execution with recursion limit
    try:
        async for state in graph.astream(
            initial_state,
            config={"recursion_limit": settings.langgraph_recursion_limit}
        ):
            yield state
    except Exception as e:
        logger.error(f"Error during streaming research: {e}", exc_info=True)
        raise
