import os
import dotenv

from agents import ModelSettings, AgentHooks
from openai.types.shared import Reasoning
from typing import Any, TypeVar

from agents import Agent, AgentBase
from agents.run_context import RunContextWrapper, TContext
from agents.tool import Tool

TAgent = TypeVar("TAgent", bound=AgentBase)

dotenv.load_dotenv()

"""
Model Choice Explanations:

Fast: Suitable for quick tasks with lower complexity.
Core: Balances speed and detail for general tasks.
Expert: Offers more depth and nuance for complex queries.

Brief: Focuses on concise responses with essential information.
Standard: Balances detail and brevity for general tasks.
Detailed: Provides comprehensive responses with in-depth analysis.
"""

models = {
    "fast": "gpt-5-nano",
    "core": "gpt-5-mini",
    "expert": "gpt-5"
}

model_settings = {
    "brief-min": ModelSettings(reasoning=Reasoning(effort="minimal"), verbosity="low"),
    "brief-low": ModelSettings(reasoning=Reasoning(effort="low"), verbosity="low"),
    "brief-med": ModelSettings(reasoning=Reasoning(effort="medium"), verbosity="low"),
    "brief-high": ModelSettings(reasoning=Reasoning(effort="high"), verbosity="low"),
    "standard-min": ModelSettings(reasoning=Reasoning(effort="minimal"), verbosity="medium"),
    "standard-low": ModelSettings(reasoning=Reasoning(effort="low"), verbosity="medium"),
    "standard-med": ModelSettings(reasoning=Reasoning(effort="medium"), verbosity="medium"),
    "standard-high": ModelSettings(reasoning=Reasoning(effort="high"), verbosity="medium"),
    "detailed-min": ModelSettings(reasoning=Reasoning(effort="minimal"), verbosity="high"),
    "detailed-low": ModelSettings(reasoning=Reasoning(effort="low"), verbosity="high"),
    "detailed-med": ModelSettings(reasoning=Reasoning(effort="medium"), verbosity="high"),
    "detailed-high": ModelSettings(reasoning=Reasoning(effort="high"), verbosity="high"),
}

class PrintingAgentHooks(AgentHooks):
    """A class that receives callbacks on various lifecycle events for a specific agent. You can
    set this on `agent.hooks` to receive events for that specific agent.

    Subclass and override the methods you need.
    """

    async def on_start(self, context: RunContextWrapper[TContext], agent: TAgent) -> None:
        """Called before the agent is invoked. Called each time the running agent is changed to this
        agent."""
        print(f"Agent {agent.name} is starting")

    async def on_end(
        self,
        context: RunContextWrapper[TContext],
        agent: TAgent,
        output: Any,
    ) -> None:
        """Called when the agent produces a final output."""
        print(f"Agent {agent.name} has finished")

    async def on_handoff(
        self,
        context: RunContextWrapper[TContext],
        agent: TAgent,
        source: TAgent,
    ) -> None:
        """Called when the agent is being handed off to. The `source` is the agent that is handing
        off to this agent."""
        print(f"Handoff from {source.name} to {agent.name}")

    async def on_tool_start(
        self,
        context: RunContextWrapper[TContext],
        agent: TAgent,
        tool: Tool,
    ) -> None:
        """Called concurrently with tool invocation."""
        print(f"Tool {tool.name} started for agent {agent.name}")

    async def on_tool_end(
        self,
        context: RunContextWrapper[TContext],
        agent: TAgent,
        tool: Tool,
        result: str,
    ) -> None:
        """Called after a tool is invoked."""
        print(f"Tool {tool.name} ended for agent {agent.name}")