"""
Agent: splits a PDF into single pages and sends each page to Claude
for XML conversion using the prompt from prompt.md.
DO NOT MODIFY THIS FILE.
"""

import os
import sys
import base64
import re

# Load .env file if it exists
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip())


def split_pdf_to_pages(pdf_path: str) -> list[bytes]:
    """Split a PDF into individual single-page PDFs. Returns list of PDF bytes."""
    try:
        import fitz  # PyMuPDF
    except ImportError:
        print("ERROR: PyMuPDF not installed. Run: pip install PyMuPDF")
        sys.exit(1)

    doc = fitz.open(pdf_path)
    pages = []
    for page_num in range(len(doc)):
        single_page_doc = fitz.open()  # new empty PDF
        single_page_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
        pages.append(single_page_doc.tobytes())
        single_page_doc.close()
    doc.close()
    return pages


def call_claude(page_pdf_bytes: bytes, prompt: str, page_num: int) -> str:
    """Send a single-page PDF to Claude and get XML back."""
    try:
        import anthropic
    except ImportError:
        print("ERROR: anthropic not installed. Run: pip install anthropic")
        sys.exit(1)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: Set ANTHROPIC_API_KEY environment variable.")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    # Inject the page number into the prompt
    full_prompt = prompt.replace("PAGE_NUMBER", str(page_num))

    pdf_b64 = base64.standard_b64encode(page_pdf_bytes).decode("utf-8")

    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=8000,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "application/pdf",
                            "data": pdf_b64,
                        },
                    },
                    {
                        "type": "text",
                        "text": full_prompt,
                    },
                ],
            }
        ],
    )

    return response.content[0].text


def extract_xml_from_response(response: str, page_num: int) -> str:
    """Extract the <Page>...</Page> XML from Claude's response."""
    # Strip code block fences if present
    code_block = re.search(r"```(?:xml)?\s*\n?(.*?)```", response, re.DOTALL)
    if code_block:
        response = code_block.group(1).strip()
    # Find the specific page
    page_match = re.search(
        rf'<Page\s+num="{page_num}".*?</Page>', response, re.DOTALL
    )
    if page_match:
        return page_match.group(0).strip()
    # Fallback: grab the first <Page> block
    page_match = re.search(r"<Page.*?</Page>", response, re.DOTALL)
    if page_match:
        return page_match.group(0).strip()
    return response.strip()


def convert_pdf_page(pdf_path: str, page_num: int, prompt: str) -> str:
    """
    Main entry point: split PDF, send the specific page to Claude,
    return extracted XML string.

    Args:
        pdf_path: path to the full PDF
        page_num: 1-indexed page number
        prompt: the prompt text from prompt.md
    Returns:
        XML string for that page
    """
    pages = split_pdf_to_pages(pdf_path)
    if page_num < 1 or page_num > len(pages):
        raise ValueError(f"Page {page_num} out of range (PDF has {len(pages)} pages)")

    page_bytes = pages[page_num - 1]  # convert to 0-indexed
    response = call_claude(page_bytes, prompt, page_num)
    xml = extract_xml_from_response(response, page_num)
    return xml
