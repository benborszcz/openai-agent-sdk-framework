from src.services.openai_service import get_embeddings
from src.services.chromadb_service import add_docs
from src.utils.retrieval.convert import convert_pdf_to_text
from src.utils.retrieval.chunk import semantic_chunk_text


async def load_document_to_chromadb(
    doc_path, collection_name="all-my-documents", chunk_size=300, overlap=50
):
    # Check if the document is a PDF
    text = ""
    if doc_path.lower().endswith(".pdf"):
        text = convert_pdf_to_text(doc_path)
    elif doc_path.lower().endswith(".txt"):
        with open(doc_path, "r", encoding="utf-8") as f:
            text = f.read()
    else:
        raise ValueError("Unsupported document format. Only PDF and TXT are supported.")

    # Chunk the text
    chunks = semantic_chunk_text(text, chunk_size=chunk_size, overlap=overlap)

    # Prepare data for ChromaDB
    ids = [f"{doc_path}_chunk_{i}" for i in range(len(chunks))]
    documents = [chunk["text"] for chunk in chunks]
    metadatas = [
        {
            "source": doc_path,
            "start_word": chunk["start_word"],
            "end_word": chunk["end_word"],
        }
        for chunk in chunks
    ]

    # Get embeddings for the documents
    embeddings = await get_embeddings(documents)

    # Add documents to ChromaDB
    add_docs(collection_name, ids, documents, metadatas, embeddings)
