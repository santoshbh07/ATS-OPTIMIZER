import pdfplumber
from docx import Document
import os

def pdf_text_extractor(file_path: str) -> str:
    text = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            # x_tolerance: horizontal gap to treat as a space
            # y_tolerance: vertical gap to treat as a newline
            page_text = page.extract_text(x_tolerance=2, y_tolerance=3)
            if page_text:
                text.append(page_text)
    return "\n".join(text)

def docx_text_extractor(file_path: str) -> str:
    document = Document(file_path)
    full_text = []
    for para in document.paragraphs:
        if para.text.strip():
            full_text.append(para.text)
    return '\n'.join(full_text)

def extract_text(file_path: str) -> str:
    if file_path.endswith('.pdf'):
        return pdf_text_extractor(file_path)
    elif file_path.endswith('.docx'):
        return docx_text_extractor(file_path)
    else:
        raise ValueError("Unsupported file format!")
        