import fitz  # PyMuPDF

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extracts raw text from a PDF memory bytes object."""
    text = ""
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        for page in doc:
            text += page.get_text()
    except Exception as e:
        print(f"Error parsing PDF: {e}")
    return text

def parse_resume(file_bytes: bytes) -> dict:
    """
    Parses OCR / Text from resume and segments it.
    In production, this strings the raw text through a structured LLM prompt (e.g. GPT-4o-mini) to isolate exactly what to modify.
    """
    raw_text = extract_text_from_pdf(file_bytes)
    
    return {
        "raw_text": raw_text,
        "skills": ["Python", "SQL", "React"], # Stubbed derived
        "experience": [], 
        "projects": []
    }
