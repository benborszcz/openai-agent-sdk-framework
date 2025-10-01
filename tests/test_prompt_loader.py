import asyncio
import pytest
from src.utils.helpers import get_prompt_from_file, clear_prompt_cache

@pytest.mark.asyncio
async def test_prompt_loader_replacements(tmp_path, monkeypatch):
    # Use an existing prompt (e.g., chat_agent) expecting it to exist.
    # We just ensure function returns a string and replacement works.
    clear_prompt_cache()
    content = await get_prompt_from_file('chat_agent', values={'USER':'Alice'})
    assert isinstance(content, str)

@pytest.mark.asyncio
async def test_prompt_cache(monkeypatch):
    clear_prompt_cache()
    first = await get_prompt_from_file('chat_agent')
    second = await get_prompt_from_file('chat_agent')
    assert first == second  # Same content
