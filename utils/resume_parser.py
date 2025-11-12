import io

try:
    import fitz
    HAVE_PYMUPDF = True
except:
    HAVE_PYMUPDF = False

try:
    import pdfplumber
    HAVE_PDFPLUMBER = True
except:
    HAVE_PDFPLUMBER = False

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    if HAVE_PYMUPDF:
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text.strip()
        except:
            pass
    
    if HAVE_PDFPLUMBER:
        try:
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text.strip()
        except:
            pass
    return ""

def extract_text_from_file(file_bytes: bytes, filename: str) -> str:
    filename_lower = filename.lower()
    if filename_lower.endswith('.pdf'):
        return extract_text_from_pdf(file_bytes)
    elif filename_lower.endswith(('.txt', '.text')):
        try:
            return file_bytes.decode('utf-8')
        except:
            try:
                return file_bytes.decode('latin-1')
            except:
                return ""
    return ""

def clean_resume_text(text: str) -> str:
    if not text:
        return ""
    lines = [line.strip() for line in text.split('\n')]
    lines = [line for line in lines if line]
    return '\n'.join(lines)
