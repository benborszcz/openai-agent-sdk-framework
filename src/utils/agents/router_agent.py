from agents import Agent
from src.utils.agents.setup import models, model_settings, PrintingAgentHooks
from src.utils.context.local_context import LocalContext
from src.utils.helpers import get_prompt_from_file
from src.utils.agents.chat_agent import chat_agent
from src.utils.agents.planning_agent import planning_agent
from src.utils.agents.weather_agent import weather_agent


instructions = get_prompt_from_file("router_agent")
router_agent = Agent[LocalContext](
    name="Router Agent",
    instructions=instructions,
    model=models["core"],
    model_settings=model_settings["standard-low"],
    handoffs=[chat_agent, planning_agent, weather_agent],
    hooks=PrintingAgentHooks(),
)
