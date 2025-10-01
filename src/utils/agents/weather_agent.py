from agents import Agent
from src.utils.agents.setup import models, model_settings, PrintingAgentHooks
from src.utils.helpers import get_prompt_from_file
from src.utils.tools.weather_tool import (
    tool_get_current_weather,
    tool_get_daily_forecast,
    tool_get_hourly_forecast,
    tool_get_air_quality,
    tool_get_marine_forecast,
    tool_geocode_search,
    tool_get_historical_weather,
    tool_get_historical_forecast,
    tool_get_weather_bundle,
)
from src.utils.agents.factory import register_agent


@register_agent("weather")
async def create_weather_agent() -> Agent:
    """Create and return a Weather Agent.

    The agent loads its instructions from the `weather_agent` prompt file,
    uses the project's default core model and a light model setting, and
    attaches printing hooks for observability. All weather-related tools
    are registered on the agent so it can invoke them as needed.
    """
    instructions = await get_prompt_from_file("weather_agent")
    return Agent(
        name="Weather Agent",
        instructions=instructions,
        model=models["fast"],
        model_settings=model_settings["standard-med"],
        handoff_description="Handles weather-related queries and can call weather tools.",
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
