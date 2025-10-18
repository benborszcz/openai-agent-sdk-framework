from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any

from src.utils.chat import get_response

router = APIRouter()


class MessageItem(BaseModel):
    role: str
    content: str


class AgentRequest(BaseModel):
    messages: List[MessageItem]


class AgentResponse(BaseModel):
    final_output: str
    all_messages: List[Dict[str, Any]]


@router.post("/respond", response_model=AgentResponse)
async def agent_respond(request: AgentRequest):
    """Accepts a list of messages and returns the agent's response plus the next input list."""
    try:
        result = await get_response([m.dict() for m in request.messages])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Attempt to extract next messages; fall back to empty list if not available
    try:
        all_msgs = result.to_input_list()
    except Exception:
        all_msgs = []

    return AgentResponse(
        final_output=getattr(result, "final_output", str(result)), all_messages=all_msgs
    )
