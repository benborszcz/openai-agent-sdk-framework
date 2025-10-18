from agents import Agent
from src.utils.agents.setup import models, model_settings, PrintingAgentHooks
from src.utils.helpers import get_prompt_from_file
from src.utils.agents.planning_agent import planning_agent
from src.utils.agents.weather_agent import weather_agent
from src.utils.guardrails.us_weather_guardrail import us_weather_guardrail
from src.utils.guardrails.no_poem_guardrail import no_poem_guardrail
from src.utils.context.local_context import LocalContext
from src.utils.tools.osu_fb_tool import query_ohio_state_football_tool

instructions = get_prompt_from_file("meta_agent")
meta_agent = Agent[LocalContext](
    name="Meta Agent",
    instructions=instructions,
    model=models["core"],
    model_settings=model_settings["standard-low"],
    tools=[
        planning_agent.as_tool(
            tool_name="planning",
            tool_description="A tool for planning tasks and managing schedules.",
        ),
        weather_agent.as_tool(
            tool_name="weather",
            tool_description="A tool for retrieving weather information. Takes in a natural language prompt and returns weather info.",
        ),
        query_ohio_state_football_tool,
    ],
    hooks=PrintingAgentHooks(),
    input_guardrails=[us_weather_guardrail],
    output_guardrails=[no_poem_guardrail],
)
