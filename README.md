# Excuse Generator
An intelligent excuse generation system powered by AI agents that creates believable, news-backed excuses complete with evidence and ready-to-send messages.

## Overview
Excuse Generator is a multi-agent system that leverages fresh news data to craft creative and plausible excuses for any situation. The system scrapes real-time news, generates contextually relevant excuses, builds supporting evidence, and even drafts the perfect message to send.

## Features
- Real-time News Integration: Scrapes multiple news sources for the freshest content
- Multi-Agent Architecture: Specialized AI agents for each task (collection, creation, evidence building)
- Vector Memory: Stores excuses and evidence in Qdrant for future reference
- Redis Caching: Fast retrieval of recent news and generated content
- Interactive Streamlit UI: User-friendly interface for excuse generation and customization
- Evidence Building: Finds or creates supporting proof for your excuse
- Message Drafting: AI-powered communication templates ready to send

## Installation
Clone the repository and install dependencies:

#### Repository cloning
```bash
git clone https://github.com/yourusername/grinch_ai.git
cd grinch_ai
pip install -r requirements.txt
```

### Environment Setup
Create a .env file with your API keys:
```text
OPENAI_API_KEY=your_openai_key
NEWS_API_KEY=your_newsapi_key
```

## Usage

### Quick Start
Run the Streamlit application:

```bash
streamlit run app.py
```
Example: Generate an Excuse

```python
from agents.excuse_creator import ExcuseCreatorAgent

agent = ExcuseCreatorAgent()

request = ExcuseRequest(
     situation="in ritardo per un meeting",
     context="meeting di lavoro alle 9:00",
     recipient="capo",
     tone=ExcuseTone.PROFESSIONAL
)

excuses = agent.generate_excuses(request)
print(f"{i}. {excuse.text}")
print(f"  📊 Plausibility: {excuse.plausibility_score:.2f} | "
     f"   Creativity: {excuse.creativity_score:.2f} | "
     f"   Risk: {excuse.risk_level}")
print(f"  💡 Why: {excuse.explanation}\n")
```

## Project Structure
```text
grinch_ai
├─ README.md
├─ agents
│  ├─ __init__.py
│  ├─ evidence_builder.py
│  ├─ excuse_creator.py
│  ├─ news_collector.py
│  └─ orchestrator.py
├─ app.py                     # Main Streamlit application
├─ config
│  ├─ __init__.py
│  ├─ logs
│  ├─ output
│  │  ├─ photos
│  │  └─ tickets
│  └─ settings.py
├─ main.py
├─ requirements.txt
├─ storage
│  ├─ __init__.py
│  ├─ memory.py
│  └─ schemas.py              # Pydantic data models
├─ test_excuse_creator.py
├─ test_setup.py
└─ utils
   ├─ __init__.py
   ├─ helpers.py              # Utility functions
   └─ llm_client.py
```

### System Architecture
Agent Workflow
```text
User Input: "Need excuse for missing deadline"
         │
         ▼
    ORCHESTRATOR
    Analyzes request
         │
         ▼
    NEWS SCRAPER ────────┐
    Parallel collection  │
    ├─ NewsAPI           │
    ├─ GNews             │──▶ Fresh news articles
    └─ Web scraping      │
         │               │
         ▼               │
    ORCHESTRATOR ◀───────┘
    Filters relevant news
         │
         ▼
    EXCUSE GENERATOR
    Creates 3-5 options
         │
         ▼
    USER SELECTION
    Chooses preferred excuse
         │
         ▼
    EVIDENCE CREATOR
    Builds supporting proof
    ├─ Screenshots
    ├─ Images
    └─ Links
         │
         ▼
    COMMUNICATION AGENT
    Drafts message
         │
         ▼
    USER REVIEW
    Edit/Approve
         │
         ▼
    SEND (optional) + SAVE to memory
```

### Multi-Agent System

The system employs a DataPizza Pipeline architecture with specialized agents:

**News Collector** Agent:
- Scrapes multiple news sources in parallel
- Filters for relevance and recency
- Caches results in Redis for fast retrieval

**Excuse Creator** Agent:
- Analyzes news context
- Generates creative, believable excuses
- Provides multiple options with plausibility scores

**Evidence Builder** Agent:
- Searches for supporting images and screenshots
- Creates visual evidence when needed
- Validates evidence authenticity

**Communication** Agent:
- Crafts context-appropriate messages
- Adapts tone based on recipient and situation
- Generates multiple draft variations

**Vector Memory** with Qdrant:
Instead of traditional databases, the system uses Qdrant vector storage for intelligent excuse retrieval:

```text
Excuse Storage Flow:

Generated Excuse
       │
       ▼
Text Embedding (512-dim vector)
       │
       ▼
┌────────────────────────────┐
│ Qdrant Collection          │
│ ├─ Excuse text             │
│ ├─ Embedding vector        │
│ ├─ Metadata (date, source) │
│ ├─ Evidence links          │
│ └─ Success rating          │
└────────────────────────────┘
       │
       ▼
Semantic Search Enabled
"Find similar past excuses"
```

This allows the system to:
- Find similar excuses from history
- Learn from successful patterns
- Avoid repetitive excuse types
- Suggest improvements based on past performance

#### Caching Strategy
- Redis cache layer reduces API calls and improves response time:
- News Cache: 1-hour TTL for fresh articles
- Generated Excuses: 24-hour TTL for recent creations
- Evidence Assets: 7-day TTL for images and screenshots

#### Requirements
- Python 3.11+
- Docker (for local Qdrant instance)
- Redis server
- See requirements.txt for Python dependencies

#### API Keys Required
- OpenAI API (for AI agents)
- NewsAPI (for news collection)
- Qdrant Cloud or local instance
- Redis (local or cloud)
- Unsplash/Pexels (for image search)

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
[To be determined]

## Disclaimer
This tool is for entertainment and educational purposes. Use responsibly and ethically. The developers are not responsible for consequences of excuse usage.
