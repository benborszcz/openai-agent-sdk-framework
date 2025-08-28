from agents import Agent, tool
from src.utils.agents.setup import models, model_settings, PrintingAgentHooks
from src.utils.helpers import get_prompt_from_file
from src.utils.agents.planning_agent import create_planning_agent
from src.utils.agents.weather_agent import create_weather_agent

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
                tool_description="A tool for retrieving weather information. Takes in a natural language prompt and returns weather info."
            )
        ],
        hooks=PrintingAgentHooks()
    )
