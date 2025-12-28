"""
FastAPI Routes for Deep Research Agent
"""
import logging
import uuid
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from app.models.schemas import (
    ResearchRequest,
    ResearchResponse,
    RefinementRequest,
    ProgressUpdate
)
from app.agents.graph_builder import run_research, stream_research
import json

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory session storage (replace with database in production)
research_sessions: Dict[str, Dict[str, Any]] = {}


@router.post("/api/research", response_model=dict)
async def create_research(request: ResearchRequest):
    """
    Create and run a research session

    Args:
        request: Research request with query and config

    Returns:
        Research results
    """
    try:
        session_id = str(uuid.uuid4())
        logger.info(f"Starting research session {session_id}: {request.query}")

        # Run research
        final_state = await run_research(
            query=request.query,
            config=request.config.model_dump()
        )

        # Create simplified response
        response_data = {
            "session_id": session_id,
            "query": request.query,
            "response": final_state.get("final_response", ""),
            "sources": final_state.get("sources", []),
            "timestamp": datetime.now().isoformat()
        }

        # Store session
        research_sessions[session_id] = response_data

        logger.info(f"Research session {session_id} completed")
        return response_data

    except Exception as e:
        logger.error(f"Error in research: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/research/{session_id}")
async def get_research(session_id: str):
    """
    Retrieve a research session by ID

    Args:
        session_id: Session identifier

    Returns:
        Research session data
    """
    if session_id not in research_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    return research_sessions[session_id]


@router.post("/api/research/{session_id}/refine")
async def refine_research(session_id: str, request: RefinementRequest):
    """
    Refine existing research with additional queries

    Args:
        session_id: Session to refine
        request: Refinement parameters

    Returns:
        Updated research results
    """
    if session_id not in research_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        original_session = research_sessions[session_id]
        logger.info(f"Refining session {session_id}: {request.refinement_query}")

        # Create refined query
        refined_query = f"{original_session['query']} - Focus on: {request.refinement_query}"

        # Run research with refined query
        final_state = await run_research(
            query=refined_query,
            config={"max_iterations": 2}
        )

        # Update session with refined answer
        original_session["response"] = final_state.get("final_response", "")
        original_session["sources"].extend(final_state.get("sources", []))
        original_session["timestamp"] = datetime.now().isoformat()

        research_sessions[session_id] = original_session

        logger.info(f"Session {session_id} refined successfully")
        return original_session

    except Exception as e:
        logger.error(f"Error refining research: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/subreddits/discover")
async def discover_subreddits(topic: str, limit: int = 10):
    """
    Discover relevant subreddits for a topic

    Args:
        topic: Topic to search
        limit: Maximum subreddits to return

    Returns:
        List of relevant subreddits
    """
    try:
        from app.scrapers.yars_client import YARSRedditClient

        yars = YARSRedditClient(user_agent="DeepResearchAgent/1.0")

        subreddits = await yars.get_subreddit_recommendations(topic, limit)
        await yars.close()

        return {"topic": topic, "subreddits": subreddits}

    except Exception as e:
        logger.error(f"Error discovering subreddits: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/reddit/analyze-thread")
async def analyze_thread(thread_url: str, depth: str = "full"):
    """
    Analyze a specific Reddit thread

    Args:
        thread_url: Reddit thread URL
        depth: Analysis depth (full/summary)

    Returns:
        Thread analysis
    """
    try:
        from app.scrapers.yars_client import YARSRedditClient

        yars = YARSRedditClient(user_agent="DeepResearchAgent/1.0")

        comment_limit = 100 if depth == "full" else 25
        thread_data = await yars.get_post_with_comments(thread_url, comment_limit)
        sentiment = await yars.analyze_thread_sentiment(thread_url)

        await yars.close()

        return {
            "thread_url": thread_url,
            "post": thread_data.get("post", {}),
            "comments": thread_data.get("comments", []),
            "total_comments": thread_data.get("total_comments", 0),
            "sentiment": sentiment
        }

    except Exception as e:
        logger.error(f"Error analyzing thread: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/ws/research")
async def websocket_research(websocket: WebSocket):
    """
    WebSocket endpoint for streaming research progress

    Args:
        websocket: WebSocket connection
    """
    await websocket.accept()
    logger.info("WebSocket connection established")

    try:
        # Receive research request
        data = await websocket.receive_text()
        request_data = json.loads(data)

        query = request_data.get("query")
        config = request_data.get("config", {})

        if not query:
            await websocket.send_json({
                "status": "error",
                "message": "Query is required"
            })
            return

        session_id = str(uuid.uuid4())

        # Send initial acknowledgment
        await websocket.send_json({
            "status": "started",
            "session_id": session_id,
            "query": query
        })

        # Stream research progress
        async for state_update in stream_research(query, config):
            # Extract node name from state update
            node_name = list(state_update.keys())[0] if state_update else "unknown"
            node_state = state_update.get(node_name, {})

            # Send progress update
            progress = {
                "status": "in_progress",
                "stage": node_name,
                "message": f"Completed {node_name}",
                "data": {
                    "web_results": len(node_state.get("web_results", [])),
                    "reddit_posts": len(node_state.get("reddit_posts", [])),
                    "reddit_comments": len(node_state.get("reddit_comments", [])),
                    "scraped_content": len(node_state.get("scraped_web_content", []))
                }
            }

            await websocket.send_json(progress)

            # Check if complete
            if node_state.get("research_complete"):
                # Send simplified final result
                result = {
                    "status": "complete",
                    "session_id": session_id,
                    "result": {
                        "response": node_state.get("final_response", ""),
                        "sources": node_state.get("sources", [])
                    }
                }

                # Store session
                research_sessions[session_id] = result["result"]

                await websocket.send_json(result)
                break

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        await websocket.send_json({
            "status": "error",
            "message": str(e)
        })
    finally:
        await websocket.close()
