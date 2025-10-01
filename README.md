# OpenAI Agent SDK Framework

A comprehensive framework for building multi-agent AI systems using the OpenAI Agents SDK. This framework provides a flexible, modular architecture for creating specialized agents that can collaborate, use tools, and handle complex tasks through intelligent routing and delegation.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Agent System](#agent-system)
- [Tools System](#tools-system)
- [Configuration](#configuration)
- [API Usage](#api-usage)
- [Code Structure](#code-structure)
- [Examples](#examples)

## Overview

This framework implements a multi-agent system where specialized agents work together to handle different types of tasks. The system uses:

- **Agent Orchestration**: A meta-agent pattern that coordinates between specialized agents
- **Tool Integration**: Extensible tool system for adding custom functionality
- **Flexible Configuration**: Model settings and reasoning effort levels can be tuned per agent
- **Dual Interface**: Both CLI and REST API access modes

## Architecture

### Multi-Agent System

The framework uses a hierarchical agent architecture:

```
Meta Agent (Coordinator)
├── Planning Agent → Handles task planning and organization
├── Weather Agent → Provides weather data and forecasts
└── (Extensible) → Add your own specialized agents
```

Alternatively, a Router Agent pattern is also available for handoff-based workflows:

```
Router Agent
├── Chat Agent → General conversational tasks
├── Planning Agent → Task planning
└── Weather Agent → Weather queries
```

### Key Components

1. **Agents** (`src/utils/agents/`): Specialized AI agents with specific capabilities
2. **Tools** (`src/utils/tools/`): Functions that agents can invoke to perform actions
3. **Services** (`src/services/`): External API integrations (e.g., Open-Meteo weather API)
4. **Configuration** (`src/utils/agents/setup.py`): Model settings and agent hooks
5. **Routing** (`src/routes/`): FastAPI endpoints for web access

## Installation

### Prerequisites

- Python 3.8+
- OpenAI API key

### Setup

1. Clone the repository:
```bash
git clone https://github.com/benborszcz/openai-agent-sdk-framework.git
cd openai-agent-sdk-framework
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your OpenAI API key:
```bash
OPENAI_API_KEY=your_api_key_here
```

## Quick Start

### CLI Mode

Run the interactive command-line interface:

```bash
python -m src.main
```

Then chat with the agent:
```
User: What's the weather like in Tokyo?
Agent: [Weather information response]
User: exit
```

### API Mode

Start the FastAPI server:

```bash
python run.py
```

The API will be available at `http://127.0.0.1:8000`. Send requests to `/agent/respond`:

```bash
curl -X POST http://127.0.0.1:8000/agent/respond \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "What is the weather in New York?"}
    ]
  }'
```

## Agent System

### Agent Configuration

Agents are configured with multiple parameters that control their behavior:

```python
Agent(
    name="Agent Name",                    # Unique identifier
    instructions="System prompt...",      # Behavior instructions
    model="gpt-5-mini",                   # Model to use
    model_settings=ModelSettings(...),    # Reasoning and verbosity
    tools=[...],                          # Available tools
    handoffs=[...],                       # Other agents for delegation
    hooks=PrintingAgentHooks()           # Lifecycle event handlers
)
```

### Model Selection

The framework provides three model tiers (defined in `src/utils/agents/setup.py`):

- **Fast** (`gpt-5-nano`): Quick tasks with lower complexity
- **Core** (`gpt-5-mini`): Balanced speed and detail for general tasks
- **Expert** (`gpt-5`): Complex queries requiring depth and nuance

### Model Settings

Each agent can be configured with different reasoning effort and verbosity levels:

```python
model_settings = {
    "brief-min": ModelSettings(reasoning=Reasoning(effort="minimal"), verbosity="low"),
    "brief-low": ModelSettings(reasoning=Reasoning(effort="low"), verbosity="low"),
    "brief-med": ModelSettings(reasoning=Reasoning(effort="medium"), verbosity="low"),
    "brief-high": ModelSettings(reasoning=Reasoning(effort="high"), verbosity="low"),
    
    "standard-min": ModelSettings(reasoning=Reasoning(effort="minimal"), verbosity="medium"),
    "standard-low": ModelSettings(reasoning=Reasoning(effort="low"), verbosity="medium"),
    "standard-med": ModelSettings(reasoning=Reasoning(effort="medium"), verbosity="medium"),
    "standard-high": ModelSettings(reasoning=Reasoning(effort="high"), verbosity="medium"),
    
    "detailed-min": ModelSettings(reasoning=Reasoning(effort="minimal"), verbosity="high"),
    "detailed-low": ModelSettings(reasoning=Reasoning(effort="low"), verbosity="high"),
    "detailed-med": ModelSettings(reasoning=Reasoning(effort="medium"), verbosity="high"),
    "detailed-high": ModelSettings(reasoning=Reasoning(effort="high"), verbosity="high"),
}
```

**Reasoning Effort**:
- `minimal`: Fastest responses with basic reasoning
- `low`: Quick responses with some analysis
- `medium`: Balanced reasoning and response time
- `high`: Deep analysis and comprehensive responses

**Verbosity**:
- `low`: Concise, essential information only
- `medium`: Balanced detail and brevity
- `high`: Comprehensive, in-depth responses

### Available Agents

#### Meta Agent (`src/utils/agents/meta_agent.py`)

The meta agent coordinates between specialized agents using tools. It delegates tasks to appropriate agents:

```python
async def create_meta_agent() -> Agent:
    instructions = await get_prompt_from_file("meta_agent")
    planning_agent = await create_planning_agent()
    weather_agent = await create_weather_agent()
    return Agent(
        name="Meta Agent",
        instructions=instructions,
        model=models["core"],
        model_settings=model_settings["standard-low"],
        tools=[
            planning_agent.as_tool(
                tool_name="planning",
                tool_description="A tool for planning tasks and managing schedules."
            ),
            weather_agent.as_tool(
                tool_name="weather",
                tool_description="A tool for retrieving weather information..."
            )
        ],
        hooks=PrintingAgentHooks()
    )
```

**Key Features**:
- Uses the "core" model for balanced performance
- Delegates to planning and weather agents via tools
- Minimal reasoning effort for fast routing decisions

#### Planning Agent (`src/utils/agents/planning_agent.py`)

Handles task planning and organization:

```python
async def create_planning_agent() -> Agent:
    instructions = await get_prompt_from_file("planning_agent")
    return Agent(
        name="Planning Agent",
        instructions=f"{RECOMMENDED_PROMPT_PREFIX}\n{instructions}",
        model=models["core"],
        model_settings=model_settings["standard-med"],
        handoff_description="This is a planning agent that can handle task planning...",
        hooks=PrintingAgentHooks()
    )
```

**Key Features**:
- Medium reasoning effort for thoughtful planning
- Can be handed off to or invoked as a tool
- Supports task breakdown and scheduling

#### Weather Agent (`src/utils/agents/weather_agent.py`)

Specialized agent for weather-related queries with multiple weather tools:

```python
async def create_weather_agent() -> Agent:
    instructions = await get_prompt_from_file("weather_agent")
    return Agent(
        name="Weather Agent",
        instructions=instructions,
        model=models["fast"],
        model_settings=model_settings["standard-med"],
        handoff_description="Handles weather-related queries...",
        tools=[
            tool_get_current_weather,
            tool_get_daily_forecast,
            tool_get_hourly_forecast,
            tool_get_air_quality,
            tool_get_marine_forecast,
            tool_geocode_search,
            tool_get_historical_weather,
            tool_get_historical_forecast,
            tool_get_weather_bundle,
        ],
        hooks=PrintingAgentHooks(),
    )
```

**Key Features**:
- Uses "fast" model for quick responses
- Comprehensive weather data access via Open-Meteo API
- Geocoding support for location queries
- Historical data and forecasting capabilities

#### Chat Agent (`src/utils/agents/chat_agent.py`)

General conversational agent:

```python
async def create_chat_agent() -> Agent:
    instructions = await get_prompt_from_file("chat_agent")
    return Agent(
        name="Chat Agent",
        instructions=instructions,
        model=models["core"],
        model_settings=model_settings["standard-min"],
        handoff_description="This is a chat agent that can handle conversational tasks.",
        hooks=PrintingAgentHooks()
    )
```

**Key Features**:
- Minimal reasoning for fast conversational responses
- Handles general questions and discussions
- No specialized tools required

#### Router Agent (`src/utils/agents/router_agent.py`)

Alternative to the meta agent pattern, using handoffs instead of tools:

```python
async def create_router_agent() -> Agent:
    instructions = await get_prompt_from_file("router_agent")
    return Agent(
        name="Router Agent",
        instructions=instructions,
        model=models["core"],
        model_settings=model_settings["standard-low"],
        handoffs=[
            await create_chat_agent(),
            await create_planning_agent(),
            await create_weather_agent()
        ],
        hooks=PrintingAgentHooks()
    )
```

**Key Features**:
- Routes conversations to appropriate specialized agents
- Uses handoff mechanism instead of tool delegation
- Lower reasoning effort for fast routing decisions

### Agent Hooks

The `PrintingAgentHooks` class (in `src/utils/agents/setup.py`) provides observability into agent operations:

```python
class PrintingAgentHooks(AgentHooks):
    async def on_tool_start(
        self,
        context: RunContextWrapper[TContext],
        agent: TAgent,
        tool: Tool,
    ) -> None:
        """Called concurrently with tool invocation."""
        print(f"Tool {tool.name} started for agent {agent.name}")

    async def on_tool_end(
        self,
        context: RunContextWrapper[TContext],
        agent: TAgent,
        tool: Tool,
        result: str,
    ) -> None:
        """Called after a tool is invoked."""
        print(f"Tool {tool.name} ended for agent {agent.name}")
```

You can extend `AgentHooks` to add logging, monitoring, or custom behavior at various lifecycle events.

## Tools System

Tools are functions that agents can invoke to perform specific actions. The framework uses the `@function_tool` decorator to expose Python functions as agent tools.

### Creating a Tool

Example from `src/utils/tools/example_tool.py`:

```python
from agents import function_tool

@function_tool
async def example_tool(param: str) -> str:
    """An example tool that processes the input parameter and repeats it."""
    processed_result = f"{param}"
    return processed_result
```

**Key Points**:
- Use the `@function_tool` decorator
- Provide a clear docstring (agents see this as the tool description)
- Use type hints for parameters and return values
- Support async/await for I/O operations

### Weather Tools

The framework includes comprehensive weather tools (`src/utils/tools/weather_tool.py`) that wrap the Open-Meteo API:

1. **tool_get_current_weather**: Get current weather conditions
2. **tool_get_daily_forecast**: Multi-day weather forecast
3. **tool_get_hourly_forecast**: Hourly weather predictions
4. **tool_get_air_quality**: Air quality data
5. **tool_get_marine_forecast**: Marine conditions (waves, wind)
6. **tool_geocode_search**: Convert location names to coordinates
7. **tool_get_historical_weather**: Past weather data
8. **tool_get_historical_forecast**: Historical forecast data
9. **tool_get_weather_bundle**: Combined current + forecast data

Example weather tool implementation:

```python
@function_tool
async def tool_get_current_weather(location: str) -> str:
    """Get current weather for a location (e.g. 'San Francisco' or 'Tokyo, Japan')."""
    try:
        # Geocode the location
        geo_result = await geocode_search(location, count=1)
        results = geo_result.get("results", [])
        if not results:
            return f"Could not find location: {location}"
        
        place = results[0]
        lat, lon = place["latitude"], place["longitude"]
        name = place.get("name", location)
        
        # Fetch weather
        weather = await get_current_weather(lat, lon)
        temp = weather.get("temperature")
        windspeed = weather.get("windspeed")
        
        return f"Current weather in {name}: {temp}°C, wind {windspeed} km/h"
    except Exception as e:
        return f"Error fetching weather: {e}"
```

### Adding New Tools

To add a new tool:

1. Create a new file in `src/utils/tools/` or add to an existing file
2. Define an async function with the `@function_tool` decorator
3. Add comprehensive docstring explaining what the tool does
4. Import and add the tool to the appropriate agent's `tools` list

Example:

```python
from agents import function_tool

@function_tool
async def my_custom_tool(query: str) -> str:
    """Description of what this tool does. The agent will see this description."""
    # Your implementation here
    result = perform_some_action(query)
    return result
```

Then add it to an agent:

```python
agent = Agent(
    name="My Agent",
    tools=[my_custom_tool, other_tool],
    # ... other config
)
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

The framework uses `python-dotenv` to load environment variables automatically.

### Prompt Management

Agent instructions are stored as text files in `src/utils/agents/prompts/`:

- `meta_agent.txt`: Meta agent system prompt
- `planning_agent.txt`: Planning agent instructions
- `weather_agent.txt`: Weather agent instructions
- `chat_agent.txt`: Chat agent instructions
- `router_agent.txt`: Router agent instructions

The `get_prompt_from_file()` helper function (`src/utils/helpers.py`) loads and optionally templates these prompts:

```python
async def get_prompt_from_file(filename: str, values: dict = None) -> str:
    """
    Reads the prompt from src/utils/agents/prompts/{filename}.txt asynchronously 
    and replaces {{key}} with values from the dictionary.
    """
    base_dir = os.path.join(os.path.dirname(__file__), 'agents', 'prompts')
    file_path = os.path.join(base_dir, f"{filename}.txt")
    async with aiofiles.open(file_path, mode='r', encoding='utf-8') as f:
        prompt = await f.read()
    if values:
        for k, v in values.items():
            prompt = prompt.replace(f"{{{{{k}}}}}", str(v))
    return prompt
```

This allows you to:
- Separate agent instructions from code
- Easily modify agent behavior without changing code
- Use template variables with `{{variable_name}}` syntax

## API Usage

### Starting the Server

The FastAPI server is launched via `run.py`:

```python
import uvicorn

if __name__ == "__main__":
    uvicorn.run("src.api:app", host="127.0.0.1", port=8000, reload=True)
```

Run it with:
```bash
python run.py
```

### API Structure

The API is defined in `src/api.py`:

```python
from fastapi import FastAPI
from src.routes.agent_routes import router as agent_router

app = FastAPI()
app.include_router(agent_router, prefix="/agent")

@app.get("/")
async def root():
    return {"message": "Template Agentic Framework v0.0.1-alpha"}
```

### Endpoints

#### POST `/agent/respond`

Send messages to the agent system and receive responses.

**Request Body**:
```json
{
  "messages": [
    {
      "role": "user",
      "content": "What's the weather in Paris?"
    }
  ]
}
```

**Response**:
```json
{
  "final_output": "The current weather in Paris is...",
  "all_messages": [
    {
      "role": "user",
      "content": "What's the weather in Paris?"
    },
    {
      "role": "assistant",
      "content": "The current weather in Paris is..."
    }
  ]
}
```

**Implementation** (`src/routes/agent_routes.py`):

```python
@router.post("/respond", response_model=AgentResponse)
async def agent_respond(request: AgentRequest):
    """Accepts a list of messages and returns the agent's response plus the next input list."""
    try:
        result = await get_response([m.dict() for m in request.messages])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    try:
        all_msgs = result.to_input_list()
    except Exception:
        all_msgs = []

    return AgentResponse(
        final_output=getattr(result, "final_output", str(result)), 
        all_messages=all_msgs
    )
```

## Code Structure

### Directory Layout

```
openai-agent-sdk-framework/
├── src/
│   ├── api.py                      # FastAPI application setup
│   ├── main.py                     # CLI entry point
│   ├── routes/
│   │   └── agent_routes.py         # API endpoints
│   ├── services/
│   │   └── open_meteo.py          # Weather API client
│   ├── utils/
│   │   ├── agents/
│   │   │   ├── setup.py           # Agent configuration & hooks
│   │   │   ├── meta_agent.py      # Meta agent (tool-based routing)
│   │   │   ├── router_agent.py    # Router agent (handoff-based)
│   │   │   ├── planning_agent.py  # Planning specialist
│   │   │   ├── weather_agent.py   # Weather specialist
│   │   │   ├── chat_agent.py      # Chat specialist
│   │   │   └── prompts/           # Agent instruction files
│   │   ├── tools/
│   │   │   ├── example_tool.py    # Example tool template
│   │   │   └── weather_tool.py    # Weather API tools
│   │   ├── chat.py                # Main chat orchestration
│   │   └── helpers.py             # Utility functions
├── run.py                          # API server launcher
├── requirements.txt                # Python dependencies
├── .env                           # Environment variables (create this)
└── README.md                      # This file
```

### Core Flow

#### CLI Mode (`src/main.py`)

```python
async def main():
    messages = []
    while True:
        message = input("User: ")
        if message == "exit":
            break
        messages.append({"role": "user", "content": message})
        result = await get_response(messages)
        print(f"Agent: {result.final_output}")
        messages = result.to_input_list()  # Maintain conversation history
```

The CLI:
1. Collects user input in a loop
2. Sends messages to the agent system via `get_response()`
3. Displays the agent's response
4. Maintains conversation history by updating the messages list

#### Chat Orchestration (`src/utils/chat.py`)

```python
async def get_response(messages: List[TResponseInputItem]) -> RunResult:
    agent = await create_meta_agent()
    result: RunResult = await Runner.run(agent, input=messages)
    return result
```

This is the main entry point that:
1. Creates the meta agent (which includes all sub-agents)
2. Runs the agent with the provided messages
3. Returns the complete result including agent output and updated message history

### Service Layer

#### Open-Meteo Service (`src/services/open_meteo.py`)

A comprehensive async client for the Open-Meteo weather API:

```python
async def get_current_weather(
    lat: float, lon: float, *, timezone: str = "auto", 
    client: Optional[httpx.AsyncClient] = None
) -> Dict[str, Any]:
    """Get current weather for given coordinates."""
    # Implementation with retry logic and error handling
```

**Features**:
- Async/await for efficient I/O
- Automatic retry with exponential backoff
- Multiple API endpoints (forecast, air quality, marine, etc.)
- Reusable HTTP client for connection pooling
- Type hints for better IDE support

## Examples

### Example 1: Simple Weather Query

**CLI**:
```
User: What's the weather in Tokyo?
Agent: The current weather in Tokyo is 18°C with winds at 12 km/h.
```

**Behind the scenes**:
1. User message goes to meta agent
2. Meta agent recognizes this is a weather query
3. Delegates to weather agent via tool
4. Weather agent calls `tool_geocode_search("Tokyo")`
5. Weather agent calls `tool_get_current_weather()` with coordinates
6. Result is returned to user

### Example 2: Complex Multi-Agent Task

**CLI**:
```
User: Help me plan a weekend trip to San Francisco and check the weather
Agent: I'll help you plan that trip. Let me check the weather first...
[Weather agent provides forecast]
[Planning agent suggests activities based on weather]
Agent: Here's your weekend plan: ...
```

**Behind the scenes**:
1. Meta agent recognizes both planning and weather components
2. First delegates to weather agent for forecast
3. Then delegates to planning agent with weather context
4. Planning agent creates itinerary considering weather
5. Coordinated response returned to user

### Example 3: Using the API

**Python client**:
```python
import httpx
import asyncio

async def chat_with_agent():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://127.0.0.1:8000/agent/respond",
            json={
                "messages": [
                    {"role": "user", "content": "What's the weather in London?"}
                ]
            }
        )
        result = response.json()
        print(result["final_output"])
        return result["all_messages"]

asyncio.run(chat_with_agent())
```

### Example 4: Creating a Custom Agent

```python
from agents import Agent
from src.utils.agents.setup import models, model_settings, PrintingAgentHooks
from src.utils.helpers import get_prompt_from_file

async def create_custom_agent() -> Agent:
    instructions = await get_prompt_from_file("custom_agent")  # Create this file
    return Agent(
        name="Custom Agent",
        instructions=instructions,
        model=models["core"],
        model_settings=model_settings["standard-med"],
        tools=[
            # Add your custom tools here
        ],
        hooks=PrintingAgentHooks()
    )
```

Then integrate it into the meta agent:

```python
async def create_meta_agent() -> Agent:
    # ... existing code ...
    custom_agent = await create_custom_agent()
    return Agent(
        # ... existing config ...
        tools=[
            # ... existing tools ...
            custom_agent.as_tool(
                tool_name="custom",
                tool_description="Description of what your custom agent does"
            )
        ]
    )
```

## Advanced Topics

### Agent-as-Tool Pattern

The framework uses the "agent-as-tool" pattern where agents can invoke other agents as if they were tools:

```python
planning_agent.as_tool(
    tool_name="planning",
    tool_description="A tool for planning tasks and managing schedules."
)
```

This provides:
- **Modularity**: Each agent is independent and reusable
- **Composability**: Agents can be combined in different configurations
- **Scalability**: Easy to add new specialized agents
- **Separation of Concerns**: Each agent focuses on its domain

### Handoff vs. Tool Delegation

The framework supports two patterns for agent coordination:

**Tool Delegation** (Meta Agent):
- Agents are invoked as tools
- Coordinator maintains control
- Better for orchestrated workflows
- Used in `meta_agent.py`

**Handoff** (Router Agent):
- Control is transferred to specialist agent
- Specialist continues the conversation
- Better for continuous interactions
- Used in `router_agent.py`

Choose based on your use case:
- Use **tools** when you need the coordinator to process results
- Use **handoffs** when specialists should maintain conversation context

### Conversation State Management

The framework maintains conversation state through message lists:

```python
messages = result.to_input_list()
```

This converts the `RunResult` back into a list of messages that can be sent in the next turn, preserving:
- User messages
- Assistant responses
- Tool calls and results
- Agent handoffs

## Extending the Framework

### Adding a New Agent

1. Create a new file in `src/utils/agents/`:
```python
# src/utils/agents/my_agent.py
from agents import Agent
from src.utils.agents.setup import models, model_settings, PrintingAgentHooks
from src.utils.helpers import get_prompt_from_file

async def create_my_agent() -> Agent:
    instructions = await get_prompt_from_file("my_agent")
    return Agent(
        name="My Agent",
        instructions=instructions,
        model=models["core"],
        model_settings=model_settings["standard-med"],
        tools=[
            # Your tools here
        ],
        hooks=PrintingAgentHooks()
    )
```

2. Create the prompt file:
```
# src/utils/agents/prompts/my_agent.txt
You are a specialized agent that...
```

3. Integrate into the meta agent:
```python
# In src/utils/agents/meta_agent.py
from src.utils.agents.my_agent import create_my_agent

async def create_meta_agent() -> Agent:
    # ... existing code ...
    my_agent = await create_my_agent()
    return Agent(
        # ...
        tools=[
            # ... existing tools ...
            my_agent.as_tool(
                tool_name="my_tool",
                tool_description="Description of your agent's capabilities"
            )
        ]
    )
```

### Adding a New Tool

1. Create the tool function:
```python
# src/utils/tools/my_tool.py
from agents import function_tool

@function_tool
async def my_custom_tool(param1: str, param2: int = 10) -> str:
    """
    Clear description of what this tool does.
    
    Args:
        param1: Description of param1
        param2: Description of param2 (default: 10)
    
    Returns:
        Description of return value
    """
    # Your implementation
    result = f"Processed {param1} with {param2}"
    return result
```

2. Add to an agent:
```python
from src.utils.tools.my_tool import my_custom_tool

async def create_my_agent() -> Agent:
    return Agent(
        # ...
        tools=[
            my_custom_tool,
            # other tools...
        ]
    )
```

### Custom Hooks

Implement custom hooks for logging, monitoring, or side effects:

```python
from agents import AgentHooks
import logging

class LoggingAgentHooks(AgentHooks):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def on_tool_start(self, context, agent, tool):
        self.logger.info(f"Agent {agent.name} calling tool {tool.name}")
    
    async def on_tool_end(self, context, agent, tool, result):
        self.logger.info(f"Tool {tool.name} returned: {result[:100]}")
    
    # Add other hook methods as needed
```

## Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'agents'`
- **Solution**: Install the openai-agents package: `pip install openai-agents`

**Issue**: Agent not responding / API errors
- **Solution**: Check that your `.env` file contains a valid `OPENAI_API_KEY`

**Issue**: Weather tools not working
- **Solution**: Ensure you have internet connectivity; Open-Meteo API is public and doesn't require a key

**Issue**: Import errors
- **Solution**: Make sure you're running from the project root and src is in your Python path

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [OpenAI Agents SDK](https://github.com/openai/agents-sdk)
- Weather data provided by [Open-Meteo API](https://open-meteo.com/)
- FastAPI for the web framework

## Support

For issues, questions, or contributions, please visit the [GitHub repository](https://github.com/benborszcz/openai-agent-sdk-framework).