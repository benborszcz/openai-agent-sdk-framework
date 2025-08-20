from agents import Agent
from src.utils.agents.setup import models, model_settings, PrintingAgentHooks
from src.utils.helpers import get_prompt_from_file
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX

async def create_planning_agent() -> Agent:
    instructions = await get_prompt_from_file("planning_agent")
    return Agent(
        name="Planning Agent",
        instructions=f"{RECOMMENDED_PROMPT_PREFIX}\n{instructions}",
        model=models["core"],
        model_settings=model_settings["standard-med"],
        handoff_description="This is a planning agent that can handle task planning and organization.",
        hooks=PrintingAgentHooks()
    )
