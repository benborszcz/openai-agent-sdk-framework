from agents import function_tool

@function_tool
async def example_tool(param: str) -> str:
    """An example tool that processes the input parameter and repeats it."""
    # Simulate some processing
    processed_result = f"{param}"
    return processed_result