"""
Pydantic models and schemas for Deep Research Agent
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, TypedDict
from datetime import datetime


# ===== Request/Response Models =====

class ResearchConfig(BaseModel):
    """Configuration for research request"""
    depth: str = Field(default="standard", description="Research depth: quick/standard/comprehensive")
    max_iterations: int = Field(default=3, ge=1, le=10)
    max_web_results: int = Field(default=15, ge=1, le=50)


class ResearchRequest(BaseModel):
    """Research request from user"""
    query: str = Field(..., min_length=3, description="Research question")
    config: ResearchConfig = Field(default_factory=ResearchConfig)


class ResearchResponse(BaseModel):
    """Simplified research response - single AI answer"""
    session_id: str
    query: str
    response: str  # Single AI-generated answer
    sources: List[Dict[str, Any]]  # Sources used for citations
    timestamp: datetime = Field(default_factory=datetime.now)


class RefinementRequest(BaseModel):
    """Request to refine existing research"""
    refinement_query: str = Field(..., description="What to focus on or add")
    add_sources: Optional[List[str]] = Field(default=None)


class ProgressUpdate(BaseModel):
    """Progress update for streaming"""
    stage: str
    status: str  # pending/in_progress/completed/error
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)


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


# ===== Helper Models =====

class SearchResult(BaseModel):
    """Standardized search result"""
    title: str
    url: str
    snippet: str
    domain: str
    published_date: Optional[str] = None
    score: float = 0.0
    source_type: str = "web"  # web/reddit


class ScrapedContent(BaseModel):
    """Scraped web content"""
    url: str
    title: str
    author: Optional[str] = None
    published_date: Optional[str] = None
    domain: str
    content: str
    content_length: int
    success: bool = True
    error: Optional[str] = None


class ContentSummary(BaseModel):
    """Content summary with metadata"""
    title: str
    url: str
    summary: str
    source_type: str  # web/reddit
    key_facts: List[str] = []
    credibility_score: float = 0.5
    sentiment: str = "neutral"


class CrossReferenceAnalysis(BaseModel):
    """Cross-reference analysis results"""
    corroborated_facts: List[str] = []
    contradictions: List[str] = []
    unique_insights: List[str] = []
    overall_confidence: str = "medium"
