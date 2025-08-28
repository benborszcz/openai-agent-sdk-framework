from agents import Agent
from src.utils.agents.setup import models, model_settings, PrintingAgentHooks
from src.utils.helpers import get_prompt_from_file
from src.utils.agents.chat_agent import create_chat_agent
from src.utils.agents.planning_agent import create_planning_agent
from src.utils.agents.weather_agent import create_weather_agent

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
