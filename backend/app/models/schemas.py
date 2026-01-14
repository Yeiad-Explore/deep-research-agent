"""
Pydantic models and schemas for Deep Research Tool
"""
from typing import List, Dict, Any, TypedDict


# ===== LangGraph State Schema =====

class ResearchState(TypedDict, total=False):
    """
    Simplified state schema for LangGraph research agent
    """
    # Input
    query: str                              # User's research question
    research_config: Dict[str, Any]         # Configuration dict

    # Search Results
    web_results: List[Dict[str, Any]]       # Tavily web search results

    # Content
    scraped_web_content: List[Dict[str, Any]]   # Scraped webpage content

    # Analysis - Simplified
    all_content: str                            # Combined content from all sources

    # Final Response
    final_response: str                         # Single AI-generated answer
    sources: List[Dict[str, Any]]               # All citation sources

    # Control Flow
    research_complete: bool                     # Completion flag
    errors: List[str]                           # Error tracking

    # Metadata
    search_keywords: List[str]                  # Generated search terms
