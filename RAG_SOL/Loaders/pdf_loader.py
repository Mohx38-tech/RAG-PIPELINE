from pathlib import Path
from pypdf import PdfReader


def load_pdf(file_path: Path) -> str:
    """Load and extract text from a PDF file."""
    file_path = Path(file_path)
    reader = PdfReader(file_path)

    pages_text = []
    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text()

        if text:
           pages_text.append(f"\n---Page{page_number}---\n{text}")

           return "\n".join(pages_text)