from agents import function_tool, RunContextWrapper
from src.utils.context.local_context import LocalContext


@function_tool
async def set_context_value(
    run_context: RunContextWrapper[LocalContext], key: str, value: str
) -> str:
    """
    Sets a key-value pair in the agent's local context.

    Args:
        run_context: The current run context containing the local context.
        key: The key to set in the context.
        value: The value to associate with the key.
    Returns:
        A confirmation string indicating the key and value set.
    """
    if run_context.context.context is None:
        run_context.context.context = {}
    run_context.context.context[key] = value
    return f"Set context[{key}] = {value}"
