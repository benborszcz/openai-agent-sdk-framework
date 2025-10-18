import chromadb

from typing import Any, Dict

client = chromadb.PersistentClient(path="chroma")


def get_collection(name: str = "all-my-documents") -> chromadb.api.models.Collection:
    return client.get_or_create_collection(name)


def add_docs(collection_name, ids, documents, metadatas, embeddings) -> None:
    if len(ids) != len(documents):
        raise ValueError("ids and documents must have the same length")
    collection = get_collection(collection_name)
    collection.upsert(
        ids=list(ids),
        documents=list(documents),
        metadatas=list(metadatas) if metadatas else None,
        embeddings=list(embeddings) if embeddings else None,
    )


def query(collection_name, query_embedding, n_results, **kwargs) -> Dict[str, Any]:
    if not query_embedding:
        raise ValueError("query_embedding is required")
    collection = get_collection(collection_name)
    return collection.query(query_embedding, n_results=n_results, **kwargs)


def reset_db() -> None:
    client.reset()
