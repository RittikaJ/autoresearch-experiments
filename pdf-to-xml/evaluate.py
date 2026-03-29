"""
Evaluation script — uses agent.py to convert PDF pages to XML,
compares output against gold-standard XMLs.
DO NOT MODIFY THIS FILE.

Prints a single score from 0.0 to 1.0.
"""

import os
import re
import sys
import xml.etree.ElementTree as ET
from agent import convert_pdf_page

# ---------------------------------------------------------------------------
# Config — which PDFs and gold files to evaluate
# ---------------------------------------------------------------------------
TEST_CASES = [
    {
        "pdf": "pdfs/H0002.pdf",
        "gold": "gold/H0002_page1.xml",
        "page_num": 1,
    },
    {
        "pdf": "pdfs/H0002.pdf",
        "gold": "gold/H0002_page2.xml",
        "page_num": 2,
    },
]

PROMPT_FILE = "prompt.md"


# ---------------------------------------------------------------------------
# XML comparison
# ---------------------------------------------------------------------------

def _compare_raw(expected, actual):
    """
    Recursively compare two XML elements node-by-node.
    Returns (score, total).
    Checks: tag name, attributes, text content, tail text, children.
    """
    if expected is None or actual is None:
        return 0.0, 1.0

    score = 0.0
    total = 0.0

    # CHECK 1: Tag name
    total += 1.0
    if expected.tag == actual.tag:
        score += 1.0

    # CHECK 2: Attributes
    expected_attrs = expected.attrib
    actual_attrs = actual.attrib
    all_keys = set(list(expected_attrs.keys()) + list(actual_attrs.keys()))
    if all_keys:
        for key in all_keys:
            total += 1.0
            if expected_attrs.get(key) == actual_attrs.get(key):
                score += 1.0

    # CHECK 3: Text content (text inside the element, before children)
    expected_text = (expected.text or "").strip()
    actual_text = (actual.text or "").strip()
    if expected_text or actual_text:
        total += 1.0
        if expected_text == actual_text:
            score += 1.0
        else:
            # Partial credit for similar text (normalized comparison)
            e_norm = re.sub(r'\s+', ' ', expected_text.lower())
            a_norm = re.sub(r'\s+', ' ', actual_text.lower())
            if e_norm == a_norm:
                score += 0.8

    # CHECK 4: Tail text (text after the element's closing tag)
    expected_tail = (expected.tail or "").strip()
    actual_tail = (actual.tail or "").strip()
    if expected_tail or actual_tail:
        total += 1.0
        if expected_tail == actual_tail:
            score += 1.0
        else:
            e_norm = re.sub(r'\s+', ' ', expected_tail.lower())
            a_norm = re.sub(r'\s+', ' ', actual_tail.lower())
            if e_norm == a_norm:
                score += 0.8

    # CHECK 5: Children (recursive)
    expected_children = list(expected)
    actual_children = list(actual)
    max_children = max(len(expected_children), len(actual_children))

    for i in range(max_children):
        if i < len(expected_children) and i < len(actual_children):
            child_score, child_total = _compare_raw(expected_children[i], actual_children[i])
            score += child_score
            total += child_total
        else:
            if i < len(expected_children):
                _, child_total = _compare_raw(expected_children[i], expected_children[i])
                total += child_total
            else:
                total += 1.0

    return score, total


# ---------------------------------------------------------------------------
# Main evaluation
# ---------------------------------------------------------------------------

def evaluate():
    # Read the prompt
    if not os.path.exists(PROMPT_FILE):
        print(f"ERROR: {PROMPT_FILE} not found.")
        sys.exit(1)
    with open(PROMPT_FILE, "r") as f:
        prompt = f.read()

    scores = []
    for i, case in enumerate(TEST_CASES):
        pdf_path = case["pdf"]
        gold_path = case["gold"]
        page_num = case["page_num"]

        print(f"Case {i+1}: {pdf_path} page {page_num}...", end=" ", flush=True)

        # Load gold standard
        try:
            with open(gold_path, "r") as f:
                gold_xml = f.read().strip()
        except FileNotFoundError:
            print(f"MISSING GOLD FILE {gold_path}")
            scores.append(0.0)
            continue

        # Use agent.py to convert the PDF page
        try:
            actual_xml = convert_pdf_page(pdf_path, page_num, prompt)
        except Exception as e:
            print(f"ERROR — {e}")
            scores.append(0.0)
            continue

        # Save the output for debugging
        with open(f"output_page{page_num}.xml", "w") as f:
            f.write(actual_xml)

        # Parse and compare
        try:
            expected_tree = ET.fromstring(gold_xml)
        except ET.ParseError as e:
            print(f"GOLD XML PARSE ERROR — {e}")
            scores.append(0.0)
            continue

        try:
            actual_tree = ET.fromstring(actual_xml)
        except ET.ParseError as e:
            print(f"INVALID XML OUTPUT — {e}")
            scores.append(0.0)
            continue

        raw_score, raw_total = _compare_raw(expected_tree, actual_tree)
        case_score = raw_score / raw_total if raw_total > 0 else 0.0
        scores.append(case_score)
        print(f"{case_score:.4f}")

    avg = sum(scores) / len(scores) if scores else 0.0
    print(f"---")
    print(f"score: {avg:.6f}")
    return avg


if __name__ == "__main__":
    evaluate()
