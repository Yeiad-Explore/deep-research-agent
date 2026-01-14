# 🔬 Deep Research Agent

AI-powered deep web research agent combining LangGraph orchestration, Tavily AI Search, and Azure OpenAI GPT-5.1 for comprehensive web research and synthesis.

## 🌟 Features

- **Deep Web Research**: Comprehensive web search and content analysis
- **LangGraph Orchestration**: Sophisticated AI workflow with parallel execution
- **Tavily AI Search**: AI-optimized web search specifically designed for LLM applications
- **Real-Time Streaming**: WebSocket-based progress updates
- **Cross-Reference Validation**: Verifies facts across multiple web sources
- **Comprehensive Reports**: Generates detailed research syntheses with citations
- **Interactive UI**: Modern, responsive interface with live updates
- **Modern Frontend**: Next.js frontend with shadcn/ui, animations, and better UX

## 📋 Prerequisites

- Python 3.9+
- API Keys:
  - Tavily AI API key (for web search)
  - Azure OpenAI API credentials (GPT-5.1)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
cd "deepresearch agent"
```

### 2. Set Up Backend

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

# Configure environment variables
cp .env.example .env
# Edit .env with your API keys
```

### 3. Configure API Keys

Edit `backend/.env` and add your API credentials:

```env
# Tavily AI Search Configuration
TAVILY_API_KEY=your_tavily_api_key_here

# Azure OpenAI Configuration (GPT-5.1 for all LLM operations)
AZURE_OPENAI_API_KEY=your_azure_openai_api_key
AZURE_OPENAI_ENDPOINT=https://your-endpoint.cognitiveservices.azure.com/openai/v1
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-5.1-chat

# Application Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
MAX_ITERATIONS=3
DEFAULT_SEARCH_RESULTS=15
```

**Important Notes:**
- **Tavily AI** provides AI-optimized search results with up to 20 results in advanced mode
- **GPT-5.1** only supports `temperature=1` and uses `max_completion_tokens` parameter

### 4. Run the Application

**Using startup scripts:**

Windows:
```bash
# From project root
.\start.bat
```

macOS/Linux:
```bash
# From project root
chmod +x start.sh
./start.sh
```

**Manual start:**
```bash
# From the backend directory
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 5. Set Up Frontend (Optional - Modern Next.js Frontend)

The project includes two frontend options:

**Option A: Modern Next.js Frontend (Recommended)**
```bash
cd frontend-nextjs
npm install
npm run dev
```

The Next.js frontend will be available at: http://localhost:3000

**Option B: Legacy HTML Frontend**

The application will be available at:
- Frontend: http://localhost:8000 (served by FastAPI)
- API Docs: http://localhost:8000/docs

**Note:** The backend CORS is configured to allow both `http://localhost:3000` (Next.js) and `http://localhost:8000` (legacy frontend).

## 📚 API Documentation

### POST /api/research

Start a new research session.

**Request:**
```json
{
  "query": "What are the latest developments in Python 3.13?",
  "config": {
    "depth": "standard",
    "max_iterations": 3,
    "max_web_results": 15
  }
}
```

**Response:**
```json
{
  "session_id": "uuid",
  "query": "...",
  "response": "...",
  "sources": [...],
  "timestamp": "..."
}
```

### WebSocket /ws/research

Real-time streaming research with progress updates.

**Connect:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/research');

ws.send(JSON.stringify({
  query: "your research query",
  config: { depth: "standard", max_web_results: 15 }
}));

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Progress update:', data);
};
```

### GET /api/research/{session_id}

Retrieve a completed research session.

### POST /api/research/{session_id}/refine

Refine existing research with additional focus.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Backend                       │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   LangGraph  │  │  Tavily AI   │  │ Azure OpenAI │ │
│  │ Orchestrator │  │    Search    │  │  GPT-5.1     │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│  ┌──────────────┐  ┌──────────────┐                    │
│  │ Web Scraper  │  │   Research   │                    │
│  │              │  │     Tools    │                    │
│  └──────────────┘  └──────────────┘                    │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│              Next.js Frontend                            │
│  WebSocket Streaming • Live Updates • Export Features   │
└─────────────────────────────────────────────────────────┘
```

## 🔄 Research Workflow

The research process follows a LangGraph state machine with 4 optimized nodes:

1. **Query Planner**: Analyzes query and creates research strategy
   - Generates optimal search keywords
   - Plans research approach

2. **Web Searcher**: Searches the web using Tavily AI
   - Tavily AI web search (advanced mode)
   - Returns up to 20 high-quality results

3. **Content Scraper**: Gathers content from URLs
   - Web page scraping with BeautifulSoup
   - Content extraction and cleaning
   - **All scraping tasks run in parallel**

4. **Answer Generator**: Generates comprehensive answer
   - Combines all scraped web content
   - Uses Azure OpenAI GPT-5.1 for synthesis
   - Structures findings with citations
   - Creates detailed research answer

### Performance Optimizations

The workflow is optimized for speed:

- **Parallel execution**: All I/O-bound operations use `asyncio.gather()` for concurrent execution
- **Efficient scraping**: Multiple URLs scraped simultaneously
- **Reduced defaults**: Optimized iteration count and result limits for faster results
- **Recursion limit**: Set to 100 to support multiple iterations without errors

## 🎯 Use Cases

- **Product Research**: Web specs + Reddit user reviews
- **Technical Topics**: Documentation + developer discussions
- **Current Events**: News + community reactions
- **Comparative Analysis**: Professional reviews + user experiences
- **Troubleshooting**: Official docs + Reddit solutions
- **Market Research**: Industry reports + community sentiment
- **Technology Evaluation**: Technical docs + real-world experiences

## 📦 Project Structure

```
deepresearch agent/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI entry point
│   │   ├── config.py               # Configuration (Pydantic Settings)
│   │   ├── models/
│   │   │   └── schemas.py          # Pydantic models & TypedDict
│   │   ├── agents/
│   │   │   ├── graph_builder.py    # LangGraph construction
│   │   │   ├── nodes.py            # Research agent nodes
│   │   │   └── tools.py            # Research tools
│   │   ├── llm/
│   │   │   ├── tavily_client.py    # Tavily AI Search client
│   │   │   └── azure_client.py     # Azure OpenAI GPT-5.1 client
│   │   ├── scrapers/
│   │   │   └── web_scraper.py      # Web scraper (aiohttp)
│   │   └── api/
│   │       └── routes.py           # API endpoints & WebSocket
│   ├── requirements.txt
│   ├── .env.example
│   └── .env                        # Your API keys (create this)
├── frontend/                        # Legacy HTML/CSS/JS frontend
│   ├── index.html                  # Main UI
│   ├── css/
│   │   └── styles.css
│   └── js/
│       ├── main.js                 # Application logic
│       ├── api.js                  # API client
│       └── ui.js                   # UI updates
├── frontend-nextjs/                 # Modern Next.js frontend (Recommended)
│   ├── app/                        # Next.js app directory
│   ├── components/                 # React components
│   │   ├── ui/                     # shadcn/ui components
│   │   └── research/               # Research-specific components
│   ├── lib/                        # Utilities and API client
│   ├── types/                      # TypeScript types
│   └── package.json
├── plan.md                         # Original project plan
├── README.md                       # This file
├── ARCHITECTURE.tex                # System architecture (LaTeX)
├── start.bat                       # Windows startup script
└── start.sh                        # Unix startup script
```

## 🔧 Configuration Options

### Research Depth
- **Quick**: 1-2 iterations, faster results
- **Standard**: 2-3 iterations, balanced (default)
- **Comprehensive**: 3-5 iterations, thorough research

### Web Search Options
- Number of results (default: 15, max: 20 for advanced)
- Search depth: basic or advanced (Tavily)
- Domain filtering (include/exclude specific domains)

### Scraping Options
- Timeout settings
- Maximum content length
- Retry configuration with exponential backoff

## 🛠️ Development

### Technology Stack

**Backend:**
- FastAPI - Modern async web framework
- LangGraph - AI agent orchestration
- Tavily Python - AI-optimized search
- OpenAI Python SDK - Azure OpenAI integration
- Pydantic - Data validation and settings
- aiohttp - Async HTTP client
- BeautifulSoup4 - Web scraping
- Tenacity - Retry logic

**Frontend:**
- **Next.js 14** - Modern React framework with App Router
- **React 18** - UI library with TypeScript
- **shadcn/ui** - High-quality component library
- **Tailwind CSS** - Utility-first CSS framework
- **Framer Motion** - Smooth animations and transitions
- **WebSocket API** - Real-time communication
- Legacy HTML/CSS/JS frontend also available in `frontend/` directory

### Adding New LLM Providers

Create a new client in `backend/app/llm/`:

```python
class NewLLMClient:
    async def chat_completion(self, messages, max_completion_tokens=2000):
        # Implementation
        pass
```

### Adding New Data Sources

1. Create scraper in `backend/app/scrapers/`
2. Add tool method in `backend/app/agents/tools.py`
3. Integrate into research nodes in `backend/app/agents/nodes.py`

### Customizing Research Nodes

Modify nodes in `backend/app/agents/nodes.py`:

```python
async def custom_node(self, state: ResearchState) -> ResearchState:
    # Your custom logic
    state["custom_data"] = result
    return state
```

Add to graph in `backend/app/agents/graph_builder.py`:

```python
workflow.add_node("custom_node", nodes.custom_node)
workflow.add_edge("previous_node", "custom_node")
```

## 🐛 Troubleshooting

### WebSocket Connection Issues

If WebSocket streaming doesn't work:
1. Check CORS settings in `config.py`
2. Ensure port 8000 is accessible
3. Verify no firewall blocking
4. Check browser console for errors
5. Try using HTTP fallback (POST /api/research)

### Tavily API Errors

**Error: 401 Unauthorized**
- Verify your Tavily API key is correct
- Check your account has credits

**Error: Rate limit exceeded**
- Tavily has monthly request limits
- Reduce `max_web_results` in config
- Wait and retry

### Azure OpenAI Errors

**Error: Unsupported parameter 'temperature'**
- GPT-5.1 only supports temperature=1.0 (default)
- This has been fixed in the latest version

**Error: Unsupported parameter 'max_tokens'**
- GPT-5.1 uses `max_completion_tokens` instead
- This has been fixed in the latest version

### Rate Limiting

The application includes:
- Automatic retries with exponential backoff (via Tenacity)
- Configurable timeout settings
- Error handling for rate limit scenarios

## 🔒 Security Considerations

- API keys are stored in `.env` (never commit this file)
- CORS is configured for localhost only by default
- Web scraping respects robots.txt
- Rate limiting prevents API abuse
- Input validation via Pydantic models

## 📊 Performance Tips

1. **Reduce iterations** for faster results (1-2 instead of 3-5)
2. **Limit sources**: Fewer web results = faster processing
3. **Use Quick depth** for simple queries
4. **Adjust max_web_results** based on your needs (default: 15)

## 🧪 Testing

The application includes error handling and logging:

```bash
# Check logs for debugging
tail -f backend/app.log  # On Unix
type backend\app.log     # On Windows
```

Test individual components:

```python
# Test Tavily search
from app.llm.tavily_client import TavilySearchClient
client = TavilySearchClient(api_key="your_key")
results = await client.web_search("test query")
```

## 📄 License

This project is provided as-is for educational and research purposes.

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

Areas for contribution:
- Additional data sources
- New LLM providers
- Enhanced UI features
- Performance optimizations
- Documentation improvements

## 📧 Support

For issues and questions, please create an issue in the repository.

## 🙏 Acknowledgments

- **LangGraph** by LangChain - AI agent orchestration
- **Tavily AI** - AI-optimized search API
- **Azure OpenAI** - GPT-5.1 language model
- **FastAPI** - Modern Python web framework

## 📈 Roadmap

- [ ] Support for additional LLM providers (Anthropic, Google)
- [ ] Database for research session persistence
- [ ] Export to multiple formats (PDF, Markdown, JSON)
- [ ] Advanced filtering and search within results
- [ ] User authentication and saved searches
- [ ] Scheduled/automated research runs
- [ ] API rate limit monitoring dashboard
- [ ] Multi-language support

---

**Built with**: LangGraph • Tavily AI • Azure OpenAI GPT-5.1 • FastAPI • Next.js

**Version**: 1.0.0
**Last Updated**: December 2025
