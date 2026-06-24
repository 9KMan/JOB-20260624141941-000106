python
// src/core/pdf_extract.py
"""PDF text extraction.

Wraps ``pdfplumber`` so the rest of the pipeline depends on a stable
``extract_text`` function rather than a third-party API surface.
"""
from __future__ import annotations

from pathlib import Path

import pdfplumber


def extract_text(pdf_path: Path) -> str:
    """Extract plain text from a PDF file, page by page.

    Pages that yield no text (image-only pages) contribute an empty string
    so the page count of the source PDF is still discernible from the
    number of newline-separated segments.

    Args:
        pdf_path: Path to a readable PDF file.

    Returns:
        The concatenated text from all pages, separated by newlines.

    Raises:
        FileNotFoundError: If ``pdf_path`` does not exist.
        pdfplumber.exceptions.PDFSyntaxError: If the file is not a valid PDF.
    """
    if not pdf_path.is_file():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    text_parts: list[str] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text_parts.append(page.extract_text() or "")
    return "\n".join(text_parts)


