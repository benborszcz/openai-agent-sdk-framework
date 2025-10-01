from agents import Runner, RunResult, TResponseInputItem
from typing import List
from src.utils.agents.factory import get_agent

async def get_response(messages: List[TResponseInputItem]) -> RunResult:
    # Obtain cached meta agent (constructed once via factory).
    agent = await get_agent("meta")
    result: RunResult = await Runner.run(agent, input=messages)
    return result
