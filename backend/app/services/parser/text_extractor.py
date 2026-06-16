import pdfplumber
from docx import Document
import os

def pdf_text_extractor(file_path: str) -> str:
    pages = []
    
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
        if page_text:
            pages.append(page_text)
        
    return "\n".join(pages)

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
        
