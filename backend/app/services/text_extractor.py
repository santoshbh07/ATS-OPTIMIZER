from pathlib import Path

import pdfplumber
from docx import Document


def pdf_text_extractor(file_path: str | Path) -> str:
    text_parts: list[str] = []

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text(
                x_tolerance=2,
                y_tolerance=3,
            )

            if page_text:
                text_parts.append(page_text)

    return "\n".join(text_parts)


def docx_text_extractor(file_path: str | Path) -> str:
    document = Document(file_path)

    text_parts = [
        paragraph.text
        for paragraph in document.paragraphs
        if paragraph.text.strip()
    ]

    return "\n".join(text_parts)


def extract_text(file_path: str | Path) -> str:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"File does not exist: {path}"
        )

    extension = path.suffix.lower()

    if extension == ".pdf":
        return pdf_text_extractor(path)

    if extension == ".docx":
        return docx_text_extractor(path)

    raise ValueError(
        f"Unsupported file format: {extension or 'unknown'}"
    )