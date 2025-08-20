import aiofiles
import os
# Async function to get prompt from file in src/utils/agents/prompts/
async def get_prompt_from_file(filename: str, values: dict = None) -> str:
	"""
	Reads the prompt from src/utils/agents/prompts/{filename}.txt asynchronously and replaces {{key}} with values from the dictionary.
	Args:
		filename (str): The name of the prompt file (without .txt extension)
		values (dict, optional): Dictionary of replacements for {{key}} in the prompt
	Returns:
		str: The contents of the prompt file with replacements
	"""
	base_dir = os.path.join(os.path.dirname(__file__), 'agents', 'prompts')
	file_path = os.path.join(base_dir, f"{filename}.txt")
	async with aiofiles.open(file_path, mode='r', encoding='utf-8') as f:
		prompt = await f.read()
	if values:
		for k, v in values.items():
			prompt = prompt.replace(f"{{{{{k}}}}}", str(v))
	return prompt
