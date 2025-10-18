import pymupdf


_LINE_BREAK_TRANSLATION_TABLE = {
    ord("\u2028"): "\n",  # Unicode line separator
    ord("\u2029"): "\n",  # Unicode paragraph separator
    ord("\u0085"): "\n",  # Next line (NEL)
}


def _normalize_line_endings(text: str) -> str:
    """Replace unusual line terminators with standard newlines."""

    if not text:
        return ""

    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return normalized.translate(_LINE_BREAK_TRANSLATION_TABLE)


def convert_pdf_to_text(pdf_path):
    """
    Converts a PDF file to text format using Pdf4LLM.

    Args:
        pdf_path (str): Path to the PDF file.

    Returns:
        str: The extracted Markdown text.
    """
    with pymupdf.open(pdf_path) as doc:
        pages = []
        for page in doc:  # iterate the document pages
            page_text = _normalize_line_endings(page.get_text())
            pages.append(page_text)

    return "\n".join(pages)
