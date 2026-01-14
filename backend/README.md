# Deep Research Tool

Simple command-line tool for deep web research using LangGraph, Tavily AI, and Azure OpenAI.

## Features

- **Deep Web Research**: Comprehensive web search and content analysis
- **LangGraph Orchestration**: AI workflow with parallel execution
- **Tavily AI Search**: AI-optimized web search
- **Simple CLI**: Run from command prompt

## Prerequisites

- Python 3.9+
- API Keys:
  - Tavily AI API key (for web search)
  - Azure OpenAI API credentials (GPT-5.1)

## Setup

### 1. Install Dependencies

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the `backend` directory:

```env
# Tavily AI Search Configuration
TAVILY_API_KEY=your_tavily_api_key_here

# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_azure_openai_api_key
AZURE_OPENAI_ENDPOINT=https://your-endpoint.cognitiveservices.azure.com/openai/v1
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-5.1-chat

# Application Configuration
MAX_ITERATIONS=3
DEFAULT_SEARCH_RESULTS=15
```

## Usage

Run research from the command line:

```bash
# Basic usage
python research.py "What are the latest developments in Python 3.13?"

# With options
python research.py "Your research question" --max-results 20 --max-iterations 3
```

### Command Line Options

- `query` (required): Your research question
- `--max-results`: Maximum number of web results (default: 15)
- `--max-iterations`: Maximum iterations (default: 3)

### Example

```bash
python research.py "What are the benefits of using TypeScript over JavaScript?" --max-results 15
```

## Research Workflow

The research process follows a simple 4-node workflow:

1. **Query Planner**: Analyzes query and creates search strategy
2. **Web Searcher**: Searches the web using Tavily AI
3. **Content Scraper**: Gathers content from URLs (parallel execution)
4. **Answer Generator**: Generates comprehensive answer with citations

## Project Structure

```
backend/
├── research.py              # CLI entry point
├── app/
│   ├── config.py            # Configuration
│   ├── models/
│   │   └── schemas.py       # Pydantic models
│   ├── agents/
│   │   ├── graph_builder.py # LangGraph construction
│   │   ├── nodes.py         # Research agent nodes
│   │   └── tools.py         # Research tools
│   ├── llm/
│   │   ├── tavily_client.py # Tavily AI Search client
│   │   └── azure_client.py  # Azure OpenAI client
│   └── scrapers/
│       └── web_scraper.py   # Web scraper
├── requirements.txt
└── README.md
```

## Technology Stack

- **LangGraph** - AI agent orchestration
- **Tavily Python** - AI-optimized search
- **OpenAI Python SDK** - Azure OpenAI integration
- **Pydantic** - Data validation
- **httpx** - Async HTTP client
- **BeautifulSoup4** - Web scraping

## License

This project is provided as-is for educational and research purposes.
