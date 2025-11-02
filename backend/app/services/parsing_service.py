import io
import tempfile
from pdfminer.high_level import extract_text
import docx2txt

def extract_text_from_resume(file):
    """Extract plain text from uploaded resume (PDF or DOCX)."""
    filename = file.filename.lower()

    if filename.endswith(".pdf"):
        # Read PDF bytes into BytesIO for pdfminer
        file_bytes = file.file.read()
        with io.BytesIO(file_bytes) as pdf_buffer:
            text = extract_text(pdf_buffer)
    elif filename.endswith(".docx"):
        # Save to temp file so docx2txt can process it
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
            tmp.write(file.file.read())
            tmp.flush()
            text = docx2txt.process(tmp.name)
    else:
        raise ValueError("Unsupported file type. Upload PDF or DOCX.")

    return text.strip()
