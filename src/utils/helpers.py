import aiofiles
import os
from typing import Dict, Optional

# Simple in-memory base prompt cache (raw file contents before value substitution)
_PROMPT_CACHE: Dict[str, str] = {}


async def get_prompt_from_file(filename: str, values: Optional[dict] = None, *, refresh: bool = False) -> str:
	"""Load a prompt template from disk with optional string interpolation.

	Caching Strategy:
	- Raw file contents cached by filename.
	- Replacement is applied on each call (cheap) so dynamic values remain supported.
	- Set `refresh=True` to force re-read (useful during development reloads).

	Args:
		filename: Base name of the prompt file (without .txt).
		values: Optional mapping of placeholder -> replacement.
		refresh: Force reloading the file contents from disk.

	Returns:
		The final prompt string with replacements applied.
	"""
	base_dir = os.path.join(os.path.dirname(__file__), 'agents', 'prompts')
	file_path = os.path.join(base_dir, f"{filename}.txt")
	if refresh or filename not in _PROMPT_CACHE:
		async with aiofiles.open(file_path, mode='r', encoding='utf-8') as f:
			_PROMPT_CACHE[filename] = await f.read()
	prompt = _PROMPT_CACHE[filename]
	if values:
		for k, v in values.items():
			prompt = prompt.replace(f"{{{{{k}}}}}", str(v))
	return prompt

def clear_prompt_cache(filename: Optional[str] = None) -> None:
	"""Clear the prompt cache for one or all files."""
	if filename is None:
		_PROMPT_CACHE.clear()
	else:
		_PROMPT_CACHE.pop(filename, None)
