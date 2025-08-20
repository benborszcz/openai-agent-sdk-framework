from agents import Agent, AgentHooks
from src.utils.agents.setup import models, model_settings, PrintingAgentHooks
from src.utils.helpers import get_prompt_from_file

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
