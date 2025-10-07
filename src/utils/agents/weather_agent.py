from agents import Agent
from src.utils.agents.setup import models, model_settings, PrintingAgentHooks
from src.utils.context.local_context import LocalContext
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

instructions = get_prompt_from_file("weather_agent")
weather_agent = Agent[LocalContext](
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
