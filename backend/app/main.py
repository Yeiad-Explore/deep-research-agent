"""
FastAPI Main Application for Deep Research Agent
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from pathlib import Path

from app.config import settings
from app.api.routes import router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Deep Research Agent API",
    description="AI-powered deep research agent with LangGraph, Parallel.ai, and YARS",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)

# Get path to frontend directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

# Mount static files (CSS, JS)
if FRONTEND_DIR.exists():
    app.mount("/css", StaticFiles(directory=str(FRONTEND_DIR / "css")), name="css")
    app.mount("/js", StaticFiles(directory=str(FRONTEND_DIR / "js")), name="js")


@app.get("/")
async def root():
    """
    Serve the frontend HTML
    """
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    else:
        return {
            "message": "Deep Research Agent API",
            "version": "1.0.0",
            "docs": "/docs",
            "status": "Frontend not found - API only"
        }


@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "service": "Deep Research Agent",
        "version": "1.0.0"
    }


@app.on_event("startup")
async def startup_event():
    """
    Startup event handler
    """
    logger.info("=" * 60)
    logger.info("Deep Research Agent Starting Up")
    logger.info("=" * 60)
    logger.info(f"CORS Origins: {settings.cors_origins_list}")
    logger.info(f"Max Iterations: {settings.max_iterations}")
    logger.info(f"Frontend Directory: {FRONTEND_DIR}")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """
    Shutdown event handler
    """
    logger.info("Deep Research Agent Shutting Down")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
