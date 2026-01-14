"""
Configuration management for Deep Research Agent
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Tavily AI Search Configuration
    tavily_api_key: str

    # Azure OpenAI Configuration (GPT-5.1 for all LLM operations)
    azure_openai_api_key: str
    azure_openai_endpoint: str
    azure_openai_deployment_name: str = "gpt-5.1-chat"

    # Application Configuration
    cors_origins: str = "http://localhost:3000,http://localhost:8000"
    max_iterations: int = 3  # Reduced from 5 for faster research
    default_search_results: int = 15
    langgraph_recursion_limit: int = 100  # Allow 4 nodes × max iterations

    # Search Configuration
    search_timeout: int = 30
    max_retries: int = 3

    # Content Scraping
    max_content_length: int = 50000
    scrape_timeout: int = 10

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins into a list"""
        return [origin.strip() for origin in self.cors_origins.split(",")]


# Global settings instance
settings = Settings()
