import aiofiles
import os
from typing import Dict, Optional

def get_prompt_from_file(filename: str, values: Optional[dict] = None) -> str:
	"""
	Loads a prompt from a file and optionally fills in placeholders with values from a dictionary.

	Args:
		filename: The name of the prompt file (without extension).
		values: A dictionary of values to replace placeholders in the prompt.

	Returns:
		The prompt string with placeholders replaced by corresponding values.
	"""
	base_dir = os.path.join(os.path.dirname(__file__), 'agents', 'prompts')
	file_path = os.path.join(base_dir, f"{filename}.txt")
	with open(file_path, mode='r', encoding='utf-8') as f:
		prompt = f.read()
	
	if values:
		for k, v in values.items():
			prompt = prompt.replace(f"{{{{{k}}}}}", str(v))
	return prompt

