import json
from agents import Agent, RunContextWrapper
from src.utils.agents.setup import models, model_settings, PrintingAgentHooks
from src.utils.helpers import get_prompt_from_file
from src.utils.context.local_context import LocalContext
from src.utils.tools.context_tool import set_context_value


def chat_agent_instructions(
    run_context: RunContextWrapper[LocalContext], agent: Agent[LocalContext]
):
    context = run_context.context.context
    print("Current context for chat agent:", context)
    return get_prompt_from_file(
        "chat_agent",
        {"context": json.dumps(context) if context else "No context available."},
    )


chat_agent = Agent[LocalContext](
    name="Chat Agent",
    instructions=chat_agent_instructions,
    model=models["core"],
    model_settings=model_settings["standard-min"],
    tools=[set_context_value],
    handoff_description="This is a chat agent that can handle conversational tasks.",
    hooks=PrintingAgentHooks(),
)
