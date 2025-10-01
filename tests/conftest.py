import os
import sys
import types
import pytest
from unittest.mock import AsyncMock, patch

# Ensure project root (containing src/) is on path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Lightweight stand-in for RunResult expected interface
class _StubRunResult:
    def __init__(self, final_output: str):
        self.final_output = final_output
        self.messages = []
    def to_input_list(self):
        return []

@pytest.fixture(autouse=True)
def patch_runner_run():
    """Automatically patch Runner.run to avoid real OpenAI calls."""
    with patch('agents.Runner.run', new=AsyncMock(return_value=_StubRunResult("stub"))):
        yield


@pytest.fixture(scope="session", autouse=True)
def register_agents_session():
    """Import agent modules so their @register_agent decorators execute.

    Ensures factory has entries like 'meta', 'planning', etc., before tests
    that request them. Session scoped to do once.
    """
    # Imports trigger decorator side-effects.
    import src.utils.agents.chat_agent  # noqa: F401
    import src.utils.agents.planning_agent  # noqa: F401
    import src.utils.agents.weather_agent  # noqa: F401
    import src.utils.agents.meta_agent  # noqa: F401
    import src.utils.agents.router_agent  # noqa: F401
    yield
