from agents import function_tool
from src.services.chromadb_service import query as chroma_query
from src.services.openai_service import get_embedding


@function_tool
async def query_ohio_state_football_tool(query: str) -> str:
    """
    A tool that queries the Ohio State Football document database. Use it for questions related to Ohio State Football.
    Args:
        query: A string containing the query to search in the Ohio State Football documents.
    Returns:
        The query results from the Ohio State Football documents.
    """
    embedding = await get_embedding(query)
    result = chroma_query("all-my-documents", embedding, n_results=3)
    return str(result)
