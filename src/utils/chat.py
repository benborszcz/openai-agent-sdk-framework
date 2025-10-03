from agents import Runner, RunResult, TResponseInputItem
from typing import List
from src.utils.agents.meta_agent import meta_agent

async def get_response(messages: List[TResponseInputItem]) -> RunResult:
    agent = meta_agent
    result: RunResult = await Runner.run(agent, input=messages)
    return result
