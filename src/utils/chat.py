from agents import Runner, RunResult, TResponseInputItem
from typing import List
from src.utils.agents.meta_agent import meta_agent
from src.utils.agents.chat_agent import chat_agent
from src.utils.agents.code_agent import code_agent
from src.utils.context.local_context import LocalContext

async def get_response(messages: List[TResponseInputItem]) -> RunResult:
    agent = code_agent
    run_context = LocalContext(context={})
    result: RunResult = await Runner.run(agent, input=messages, context=run_context)
    return result
