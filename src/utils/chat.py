from agents import Runner, RunResult, TResponseInputItem
from src.utils.agents.meta_agent import create_meta_agent
from typing import Dict, Any, List, Optional

'''
Message:

class Message(TypedDict, total=False):
    content: Required[ResponseInputMessageContentListParam]
    """
    A list of one or many input items to the model, containing different content
    types.
    """

    role: Required[Literal["user", "system", "developer"]]
    """The role of the message input. One of `user`, `system`, or `developer`."""

    status: Literal["in_progress", "completed", "incomplete"]
    """The status of item.

    One of `in_progress`, `completed`, or `incomplete`. Populated when items are
    returned via API.
    """

    type: Literal["message"]
    """The type of the message input. Always set to `message`."""
'''

async def get_response(messages: List[TResponseInputItem]) -> RunResult:
    agent = await create_meta_agent()
    result: RunResult = await Runner.run(agent, input=messages)
    return result
