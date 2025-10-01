import pytest
from src.utils.agents.factory import get_agent, clear_cache

@pytest.mark.asyncio
async def test_agent_caching():
    clear_cache()
    a1 = await get_agent('meta')
    a2 = await get_agent('meta')
    assert a1 is a2
