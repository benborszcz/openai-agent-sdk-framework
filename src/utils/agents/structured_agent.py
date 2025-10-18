from agents import Agent
from src.utils.agents.setup import models, model_settings, PrintingAgentHooks
from src.utils.helpers import get_prompt_from_file
from src.utils.context.local_context import LocalContext
from src.types.example_structure import ExampleStructure

instructions = get_prompt_from_file("code_agent")

structured_agent = Agent[LocalContext](
    name="Structured Agent",
    instructions=instructions,
    model=models["core"],
    model_settings=model_settings["standard-min"],
    handoff_description="This is a structured agent that can handle structured output tasks.",
    hooks=PrintingAgentHooks(),
    output_type=ExampleStructure,
)
