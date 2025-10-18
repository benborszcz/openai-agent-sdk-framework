from src.utils.retrieval.load import load_document_to_chromadb
from src.services.chromadb_service import query
from src.services.openai_service import get_embedding
import asyncio

if __name__ == "__main__":
    asyncio.run(
        load_document_to_chromadb("src/data/ohio_state_recent_news_10-17-2025.txt")
    )
    embedding = asyncio.run(get_embedding("What is Julian Sayins QB rating?"))
    result = query("all-my-documents", embedding, n_results=3)
    print(result)
