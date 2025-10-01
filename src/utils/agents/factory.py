"""Agent factory & cache.

Provides a lightweight extensible registry for lazily constructing and
reusing agent instances. Agents are created once (unless explicitly
refreshed) to avoid repeated prompt file I/O and object graph assembly.

Usage:
    from src.utils.agents.factory import get_agent, warm_agents

    agent = await get_agent("meta")

To add a new agent module, register a builder:
    @register_agent("my_agent")
    async def build_my_agent(): ... return Agent(...)

You can optionally warm all registered agents at startup by calling
`await warm_agents()` (e.g., in a FastAPI startup event or CLI init).
"""

from __future__ import annotations

import asyncio
from typing import Awaitable, Callable, Dict, Optional, Set

from agents import Agent

AgentBuilder = Callable[[], Awaitable[Agent]]

_registry: Dict[str, AgentBuilder] = {}
_cache: Dict[str, Agent] = {}
_inflight_locks: Dict[str, asyncio.Lock] = {}


def register_agent(name: str) -> Callable[[AgentBuilder], AgentBuilder]:
    """Decorator to register an async agent builder under a name.

    If a name is re-registered, the previous builder is overwritten but any
    cached instance remains until `refresh_agent` is called.
    """

    def decorator(fn: AgentBuilder) -> AgentBuilder:
        _registry[name] = fn
        _inflight_locks.setdefault(name, asyncio.Lock())
        return fn

    return decorator


async def get_agent(name: str, *, refresh: bool = False) -> Agent:
    """Return a cached agent instance, constructing it if needed.

    Args:
        name: Registry key.
        refresh: If True, rebuild even if cached.
    Raises:
        KeyError: If no builder is registered for the name.
    """
    if name not in _registry:
        raise KeyError(f"Agent '{name}' is not registered")

    if not refresh and name in _cache:
        return _cache[name]

    lock = _inflight_locks.setdefault(name, asyncio.Lock())
    async with lock:
        # Double-check after acquiring lock.
        if not refresh and name in _cache:
            return _cache[name]
        builder = _registry[name]
        agent = await builder()
        _cache[name] = agent
        return agent


async def warm_agents(names: Optional[Set[str]] = None) -> None:
    """Eagerly build agents for the given names (or all).

    Builds concurrently for faster warmup.
    """
    target = names or set(_registry.keys())
    await asyncio.gather(*(get_agent(n) for n in target))


def list_agents() -> Set[str]:
    return set(_registry.keys())


def clear_cache(*, names: Optional[Set[str]] = None) -> None:
    target = names or set(_cache.keys())
    for n in target:
        _cache.pop(n, None)


async def refresh_agent(name: str) -> Agent:
    return await get_agent(name, refresh=True)
