import pytest
from httpx import AsyncClient
from src.api import app

@pytest.mark.asyncio
async def test_api_basic(monkeypatch):
    # The Runner.run is already patched via fixture; just call endpoint.
    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.post('/agent/respond', json={'messages': [{'role':'user','content':'Hello'}]})
    assert resp.status_code == 200
    data = resp.json()
    assert 'final_output' in data
    assert 'all_messages' in data
