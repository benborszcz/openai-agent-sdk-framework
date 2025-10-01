"""Agent package utilities.

Provides `load_all_agents()` to dynamically import all *_agent.py modules so
their @register_agent decorators execute and populate the factory registry.
This avoids having to list imports manually in entrypoints.
"""

from importlib import import_module
from pathlib import Path
from typing import Iterable

def load_all_agents(pattern: str = "*_agent.py") -> None:
	"""Import all agent definition modules in this package.

	Args:
		pattern: Glob pattern for agent module filenames.
	"""
	base = Path(__file__).parent
	for file in base.glob(pattern):
		if file.name == "setup.py":
			continue
		import_module(f"{__name__}.{file.stem}")

__all__ = ["load_all_agents"]
