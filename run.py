import asyncio
from agents import Runner, RunResult
from src.utils.agents.router_agent import create_router_agent

async def main():
    agent = await create_router_agent()
    result: RunResult = await Runner.run(agent, input="Give me a study plan for learning Python.")
    print(result.final_output)

asyncio.run(main())
