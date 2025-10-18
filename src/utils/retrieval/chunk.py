import re
import uuid
from typing import Dict, Iterable, List, Optional, Tuple


__all__ = [
    "chunk_text",
    "chunk_documents",
    "semantic_chunk_text",
    "semantic_chunk_documents",
]


def _normalize_whitespace(text: str) -> str:
    """Collapse repeated whitespace and trim the text."""
    # replace any whitespace sequence (spaces, newlines, tabs) with a single space
    return re.sub(r"\s+", " ", text).strip()


def chunk_text(
    text: str,
    chunk_size: int = 200,
    overlap: int = 20,
    chunk_id_prefix: Optional[str] = None,
) -> List[Dict]:
    """Split a single text into overlapping word chunks.

    Args:
        text: Source text to chunk.
        chunk_size: Number of words per chunk. Must be > 0.
        overlap: Number of words to overlap between consecutive chunks. Must be >= 0 and < chunk_size.
        chunk_id_prefix: Optional prefix for generated chunk ids.

    Returns:
        A list of chunk dicts. Each dict contains: id, text, start_word, end_word.

    Raises:
        ValueError: for invalid chunk_size or overlap values.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")
    if overlap < 0:
        raise ValueError("overlap must be >= 0")
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    normalized = _normalize_whitespace(text)
    if not normalized:
        return []

    words = normalized.split(" ")
    total = len(words)
    step = chunk_size - overlap

    chunks: List[Dict] = []
    if step <= 0:
        # defensive: step should be positive due to earlier validation, but guard anyway
        step = 1

    i = 0
    while i < total:
        start = i
        end = min(i + chunk_size, total)
        chunk_words = words[start:end]
        chunk_text = " ".join(chunk_words)
        uid = uuid.uuid4().hex
        cid = f"{chunk_id_prefix + '-' if chunk_id_prefix else ''}{uid}"
        chunks.append(
            {
                "id": cid,
                "text": chunk_text,
                "start_word": start,
                "end_word": end,
            }
        )
        if end >= total:
            break
        i += step

    return chunks


def chunk_documents(
    docs: Iterable[Dict],
    chunk_size: int = 200,
    overlap: int = 20,
    text_key: str = "text",
    id_key: str = "id",
) -> List[Dict]:
    """Chunk a sequence of document-like dicts.

    Each input document should be a mapping containing the text at `text_key`.
    If the document contains `id_key`, it will be propagated to each produced chunk
    as `document_id`. Any other keys are copied into the chunk's `meta` dict.

    Args:
        docs: Iterable of dict-like documents.
        chunk_size: words per chunk.
        overlap: overlap in words.
        text_key: the key name where the text lives in each document.
        id_key: the key name for each document's id (optional).

    Returns:
        A flat list of chunk dicts with keys: id, document_id (if available), text, start_word, end_word, meta
    """
    out: List[Dict] = []
    for doc in docs:
        if not isinstance(doc, dict):
            # try to coerce simple tuples/lists like (id, text)
            raise TypeError("each document must be a dict-like mapping")

        text = doc.get(text_key, "")
        if text is None:
            text = ""

        base_chunks = chunk_text(
            text,
            chunk_size=chunk_size,
            overlap=overlap,
            chunk_id_prefix=str(doc.get(id_key, "doc")),
        )
        meta = {k: v for k, v in doc.items() if k not in (text_key, id_key)}
        for c in base_chunks:
            c_out = {
                "id": c["id"],
                "text": c["text"],
                "start_word": c["start_word"],
                "end_word": c["end_word"],
                "document_id": doc.get(id_key),
                "meta": meta,
            }
            out.append(c_out)

    return out


def _split_to_paragraphs(text: str) -> List[str]:
    """Split text into paragraphs by blank lines while normalizing whitespace."""
    # Normalize newline styles then split on two or more newlines
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    parts = [p.strip() for p in re.split(r"\n{2,}", normalized) if p.strip()]
    return parts


def _split_paragraph_to_sentences(paragraph: str) -> List[str]:
    """A lightweight sentence splitter using punctuation heuristics.

    This is NOT a full NLP sentence tokenizer but works well for English-like text.
    It keeps the sentence-ending punctuation attached to the sentence.
    """
    # Split on sentence enders followed by whitespace and a capital letter or digit.
    # Keep the delimiter by using a lookbehind-ish approach via capture groups.
    sentence_end_re = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"])")
    sentences = [s.strip() for s in sentence_end_re.split(paragraph) if s.strip()]
    return sentences or ([paragraph] if paragraph else [])


def _collect_sentences_with_indices(text: str) -> List[Tuple[List[str], int, int]]:
    """Return (sentence_words, start_word, end_word) tuples for the text."""
    paragraphs = _split_to_paragraphs(text) or [_normalize_whitespace(text)]
    sentences_with_indices: List[Tuple[List[str], int, int]] = []
    word_index = 0
    for para in paragraphs:
        normalized_para = _normalize_whitespace(para)
        if not normalized_para:
            continue
        sentences = _split_paragraph_to_sentences(normalized_para)
        for sentence in sentences:
            words = sentence.split()
            if not words:
                continue
            start = word_index
            end = start + len(words)
            sentences_with_indices.append((words, start, end))
            word_index = end
    return sentences_with_indices


def semantic_chunk_text(
    text: str,
    chunk_size: int = 200,
    overlap: int = 20,
    chunk_id_prefix: Optional[str] = None,
) -> List[Dict]:
    """Chunk text preferring semantic boundaries (paragraphs/sentences).

    This keeps chunks semantically coherent (no mid-sentence cuts) when possible,
    while still respecting the desired chunk size and overlap.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")
    if overlap < 0:
        raise ValueError("overlap must be >= 0")
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    sentences_with_indices = _collect_sentences_with_indices(text)
    if not sentences_with_indices:
        return chunk_text(
            text,
            chunk_size=chunk_size,
            overlap=overlap,
            chunk_id_prefix=chunk_id_prefix,
        )

    chunks: List[Dict] = []
    current_words: List[str] = []
    current_start: Optional[int] = None

    prev_overlap_words: List[str] = []
    prev_overlap_start: int = 0
    carry_overlap_words: List[str] = []
    carry_overlap_start: int = 0
    carry_overlap_pending = False
    chunk_seed_from_overlap = False

    def update_overlap_state(words: List[str], start: int, end: int) -> None:
        nonlocal prev_overlap_words, prev_overlap_start, carry_overlap_words, carry_overlap_start, carry_overlap_pending
        if overlap > 0 and words:
            tail_len = min(overlap, len(words))
            prev_overlap_words = words[-tail_len:]
            prev_overlap_start = end - tail_len
            carry_overlap_words = prev_overlap_words.copy()
            carry_overlap_start = prev_overlap_start
            carry_overlap_pending = True
        else:
            prev_overlap_words = []
            prev_overlap_start = end
            carry_overlap_words = []
            carry_overlap_start = end
            carry_overlap_pending = False

    def flush_current() -> None:
        nonlocal current_words, current_start, chunk_seed_from_overlap
        if not current_words:
            return
        start = current_start if current_start is not None else 0
        end = start + len(current_words)
        uid = uuid.uuid4().hex
        chunk_id = f"{chunk_id_prefix + '-' if chunk_id_prefix else ''}{uid}"
        chunk_text_value = " ".join(current_words)
        chunks.append(
            {
                "id": chunk_id,
                "text": chunk_text_value,
                "start_word": start,
                "end_word": end,
            }
        )
        update_overlap_state(current_words, start, end)
        current_words = []
        current_start = None

    chunk_seed_from_overlap = False

    for sentence_words, sentence_start, sentence_end in sentences_with_indices:
        sentence_len = len(sentence_words)
        if sentence_len == 0:
            continue

        # Ensure any pending overlap is attached before adding new content
        if current_start is None and carry_overlap_pending:
            current_words = carry_overlap_words.copy()
            current_start = carry_overlap_start
            carry_overlap_pending = False
            chunk_seed_from_overlap = True

        if sentence_len > chunk_size:
            if current_words:
                flush_current()

            long_sentence_text = " ".join(sentence_words)
            fallback_chunks = chunk_text(
                long_sentence_text,
                chunk_size=chunk_size,
                overlap=overlap,
                chunk_id_prefix=chunk_id_prefix,
            )
            for fb_chunk in fallback_chunks:
                fb_words = fb_chunk["text"].split()
                start_abs = sentence_start + fb_chunk["start_word"]
                end_abs = sentence_start + fb_chunk["end_word"]
                chunks.append(
                    {
                        "id": fb_chunk["id"],
                        "text": fb_chunk["text"],
                        "start_word": start_abs,
                        "end_word": end_abs,
                    }
                )
                update_overlap_state(fb_words, start_abs, end_abs)
            carry_overlap_pending = bool(prev_overlap_words)
            current_words = []
            current_start = None
            chunk_seed_from_overlap = False
            continue

        tentative_len = (len(current_words) if current_words else 0) + sentence_len
        if current_words and tentative_len > chunk_size:
            if not chunk_seed_from_overlap:
                flush_current()
                if carry_overlap_pending:
                    current_words = carry_overlap_words.copy()
                    current_start = carry_overlap_start
                    carry_overlap_pending = False
                    chunk_seed_from_overlap = True
            else:
                # Drop overlap for this chunk to avoid duplicate overlap-only chunks
                current_words = []
                current_start = None
                chunk_seed_from_overlap = False
                carry_overlap_pending = False

        if current_start is None:
            if carry_overlap_pending:
                current_words = carry_overlap_words.copy()
                current_start = carry_overlap_start
                carry_overlap_pending = False
                chunk_seed_from_overlap = True
            else:
                current_start = sentence_start

        current_words.extend(sentence_words)
        chunk_seed_from_overlap = False

    if current_words:
        flush_current()

    return chunks


def semantic_chunk_documents(
    docs: Iterable[Dict],
    chunk_size: int = 200,
    overlap: int = 20,
    text_key: str = "text",
    id_key: str = "id",
) -> List[Dict]:
    """Apply semantic_chunk_text to a sequence of documents, preserving metadata."""
    out: List[Dict] = []
    for doc in docs:
        if not isinstance(doc, dict):
            raise TypeError("each document must be a dict-like mapping")
        text = doc.get(text_key, "") or ""
        base_chunks = semantic_chunk_text(
            text,
            chunk_size=chunk_size,
            overlap=overlap,
            chunk_id_prefix=str(doc.get(id_key, "doc")),
        )
        meta = {k: v for k, v in doc.items() if k not in (text_key, id_key)}
        for c in base_chunks:
            c_out = {
                "id": c["id"],
                "text": c["text"],
                "start_word": c["start_word"],
                "end_word": c["end_word"],
                "document_id": doc.get(id_key),
                "meta": meta,
            }
            out.append(c_out)
    return out
