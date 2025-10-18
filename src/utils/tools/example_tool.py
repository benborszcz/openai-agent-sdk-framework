from agents import function_tool


@function_tool
async def example_tool(param: str) -> str:
    """
    An example tool that processes the input parameter and repeats it.

    Args:
        param: A string parameter to be processed.

    Returns:
        A processed string result.
    """
    # Simulate some processing
    processed_result = f"{param}"
    return processed_result
