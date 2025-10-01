# OpenAI Agent SDK Framework

A template for building multi-agent AI systems using the OpenAI Agents SDK. This framework provides a modular architecture for creating specialized agents that collaborate through routing and delegation.

## Installation

### Prerequisites
- Python 3.8+
- OpenAI API key

### Setup
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file with your OpenAI API key: `OPENAI_API_KEY=your_api_key_here`

## Quick Start

### CLI Mode
Run the interactive CLI: `python -m src.main`

### API Mode
Start the server: `python run.py`
API available at `http://127.0.0.1:8000`

Send requests to `/agent/respond`:
```bash
curl -X POST http://127.0.0.1:8000/agent/respond \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Hello"}]}'
```

## Architecture

### Multi-Agent System
- **Meta Agent**: Coordinates between specialized agents using tools
- **Router Agent**: Routes conversations to appropriate agents via handoffs
- **Specialized Agents**: Planning, Weather, Chat, etc.

### Key Components
- **Agents** (`src/utils/agents/`): Specialized AI agents
- **Tools** (`src/utils/tools/`): Functions agents can invoke
- **Services** (`src/services/`): External API integrations
- **Routes** (`src/routes/`): API endpoints

## Code Structure

```
openai-agent-sdk-framework/
├── src/
│   ├── api.py                      # FastAPI app
│   ├── main.py                     # CLI entry point
│   ├── routes/agent_routes.py      # API endpoints
│   ├── services/open_meteo.py      # Weather API client
│   └── utils/
│       ├── agents/                 # Agent definitions
│       ├── tools/                  # Tool functions
│       ├── chat.py                 # Chat orchestration
│       └── helpers.py              # Utilities
├── run.py                          # Server launcher
├── requirements.txt                # Dependencies
└── README.md
```

## Extending the Framework

### Adding a New Agent
1. Create `src/utils/agents/new_agent.py`
2. Define agent with instructions, model, tools
3. Add to meta/router agent configuration

### Adding a New Tool
1. Create tool function with `@function_tool` decorator
2. Add to appropriate agent's tools list

### Configuration
- Models and settings in `src/utils/agents/setup.py`
- Prompts in `src/utils/agents/prompts/`
- Environment variables in `.env`