import asyncio
from agents import Agent
from src.utils.agents.setup import models, model_settings, PrintingAgentHooks
from src.utils.helpers import get_prompt_from_file
from src.utils.agents.factory import get_agent, register_agent

@register_agent("meta")
async def create_meta_agent() -> Agent:
    instructions = await get_prompt_from_file("meta_agent")
    planning_agent, weather_agent = await asyncio.gather(
        get_agent("planning"), get_agent("weather")
    )
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
                tool_description="A tool for retrieving weather information. Takes in a natural language prompt and returns weather info."
            )
        ],
        hooks=PrintingAgentHooks()
    )
