from agents import Agent
from src.utils.agents.setup import models, model_settings, PrintingAgentHooks
from src.utils.helpers import get_prompt_from_file
from src.utils.context.local_context import LocalContext
from src.utils.tools.code_interpreter import code_interpreter

instructions = get_prompt_from_file("code_agent")
code_agent = Agent[LocalContext](
    name="Code Agent",
    instructions=instructions,
    model=models["core"],
    model_settings=model_settings["standard-high"],
    tools=[code_interpreter],
    handoff_description="This is a code agent that can execute Python code to perform computations, generate plots, and analyze data.",
    hooks=PrintingAgentHooks()
)