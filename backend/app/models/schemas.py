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
    include_reddit: bool = Field(default=True)
    subreddits: Optional[List[str]] = Field(default=None)
    time_filter: str = Field(default="month")
    max_web_results: int = Field(default=15, ge=1, le=50)
    max_reddit_posts: int = Field(default=50, ge=1, le=100)


class ResearchRequest(BaseModel):
    """Research request from user"""
    query: str = Field(..., min_length=3, description="Research question")
    config: ResearchConfig = Field(default_factory=ResearchConfig)


class ResearchResponse(BaseModel):
    """Research response to user"""
    session_id: str
    query: str
    final_synthesis: str
    web_summaries: List[Dict[str, Any]]
    reddit_summaries: List[Dict[str, Any]]
    community_consensus: Dict[str, Any]
    cross_reference: Dict[str, Any]
    sources: List[Dict[str, Any]]
    confidence_scores: Dict[str, Any]
    iterations_completed: int
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
    Enhanced state schema for LangGraph research agent
    """
    # Input
    query: str                              # User's research question
    research_config: Dict[str, Any]         # Configuration dict

    # Search Results
    web_results: List[Dict[str, Any]]       # Parallel.ai web search results
    reddit_posts: List[Dict[str, Any]]      # YARS Reddit posts
    reddit_comments: List[Dict[str, Any]]   # YARS Reddit comments
    reddit_threads: List[Dict[str, Any]]    # Full thread analyses

    # Content
    scraped_web_content: List[Dict[str, Any]]   # Scraped webpage content
    reddit_discussions: List[Dict[str, Any]]    # Analyzed Reddit discussions

    # Analysis
    web_summaries: List[Dict[str, Any]]         # Summaries of web content
    reddit_summaries: List[Dict[str, Any]]      # Summaries of Reddit discussions
    expert_opinions: List[Dict[str, Any]]       # Extracted expert opinions from Reddit
    community_consensus: Dict[str, Any]         # Reddit community consensus

    # Cross-Reference
    cross_reference: Dict[str, Any]             # Cross-reference analysis
    corroborated_facts: List[str]               # Facts supported by multiple sources
    contradictions: List[Dict[str, Any]]        # Conflicting information

    # Synthesis
    preliminary_synthesis: str                  # Initial synthesis
    final_synthesis: str                        # Final research report
    sources: List[Dict[str, Any]]               # All citation sources
    confidence_scores: Dict[str, Any]           # Confidence in findings

    # Control Flow
    iteration: int                              # Current iteration
    max_iterations: int                         # Max iterations
    research_complete: bool                     # Completion flag
    errors: List[str]                           # Error tracking

    # Metadata
    search_keywords: List[str]                  # Generated search terms
    relevant_subreddits: List[str]              # Identified subreddits
    research_plan: Dict[str, Any]               # Research strategy plan

    # Gap Analysis
    identified_gaps: List[str]                  # Knowledge gaps
    refinement_queries: List[str]               # Queries for next iteration


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


class RedditPost(BaseModel):
    """Reddit post model"""
    id: str
    title: str
    body: str
    url: str
    score: int
    upvote_ratio: float
    num_comments: int
    author: str
    subreddit: str
    created_utc: str


class RedditComment(BaseModel):
    """Reddit comment model"""
    body: str
    score: int
    author: str
    post_title: str
    post_url: str
    subreddit: str
    created_utc: str


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


class ConsensusAnalysis(BaseModel):
    """Community consensus analysis"""
    sentiment: str = "neutral"
    agreement_level: str = "unknown"
    themes: List[str] = []
    majority_opinion: str = ""
    minority_opinions: List[str] = []
    confidence: float = 0.5


class CrossReferenceAnalysis(BaseModel):
    """Cross-reference analysis results"""
    corroborated_facts: List[str] = []
    contradictions: List[str] = []
    unique_insights: List[str] = []
    overall_confidence: str = "medium"
