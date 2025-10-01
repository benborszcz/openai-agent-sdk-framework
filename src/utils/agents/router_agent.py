import asyncio
from agents import Agent
from src.utils.agents.setup import models, model_settings, PrintingAgentHooks
from src.utils.helpers import get_prompt_from_file
from src.utils.agents.factory import get_agent, register_agent

@register_agent("router")
async def create_router_agent() -> Agent:
    instructions = await get_prompt_from_file("router_agent")
    # Acquire dependent agents via factory (cached)
    chat, planning, weather = await asyncio.gather(
        get_agent("chat"), get_agent("planning"), get_agent("weather")
    )
    return Agent(
        name="Router Agent",
        instructions=instructions,
        model=models["core"],
        model_settings=model_settings["standard-low"],
        handoffs=[chat, planning, weather],
        hooks=PrintingAgentHooks()
    )
