"""
parse_contract.py
Extracts text from a PDF or DOCX contract and writes it to .tmp/<filename>.txt

Usage:
    python tools/parse_contract.py <path_to_contract>

Output:
    .tmp/<original_filename>.txt  — plain text extracted from the document
    Prints the output path to stdout on success.

Requirements:
    pip install pdfplumber python-docx
"""

import sys
import os
from pathlib import Path


def extract_pdf(path: Path) -> str:
    try:
        import pdfplumber
    except ImportError:
        sys.exit("Missing dependency: run `pip install pdfplumber`")

    text_parts = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n\n".join(text_parts)


def extract_docx(path: Path) -> str:
    try:
        from docx import Document
    except ImportError:
        sys.exit("Missing dependency: run `pip install python-docx`")

    doc = Document(path)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n\n".join(paragraphs)


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python tools/parse_contract.py <path_to_contract>")

    input_path = Path(sys.argv[1]).resolve()

    if not input_path.exists():
        sys.exit(f"File not found: {input_path}")

    suffix = input_path.suffix.lower()
    if suffix == ".pdf":
        text = extract_pdf(input_path)
    elif suffix == ".docx":
        text = extract_docx(input_path)
    else:
        sys.exit(f"Unsupported file type '{suffix}'. Supported: .pdf, .docx")

    # Write output to .tmp/
    project_root = Path(__file__).resolve().parent.parent
    tmp_dir = project_root / ".tmp"
    tmp_dir.mkdir(exist_ok=True)

    output_path = tmp_dir / (input_path.stem + ".txt")
    output_path.write_text(text, encoding="utf-8")

    print(output_path)


if __name__ == "__main__":
    main()
