from agents import Runner, RunResult, TResponseInputItem
from src.utils.agents.meta_agent import create_meta_agent
from typing import Dict, Any, List, Optional

async def get_response(messages: List[TResponseInputItem]) -> RunResult:
    agent = await create_meta_agent()
    result: RunResult = await Runner.run(agent, input=messages)
    return result
