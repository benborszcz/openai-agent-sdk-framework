import aiofiles
import os
from typing import Dict, Optional

def get_prompt_from_file(filename: str, values: Optional[dict] = None, *, refresh: bool = False) -> str:
	base_dir = os.path.join(os.path.dirname(__file__), 'agents', 'prompts')
	file_path = os.path.join(base_dir, f"{filename}.txt")
	with open(file_path, mode='r', encoding='utf-8') as f:
		prompt = f.read()
	
	if values:
		for k, v in values.items():
			prompt = prompt.replace(f"{{{{{k}}}}}", str(v))
	return prompt

