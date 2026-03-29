"""
Evaluation script — compares convert.py output against gold-standard XMLs.
DO NOT MODIFY THIS FILE.

HOW SCORING WORKS:
=================
We compare the agent's XML output against the gold-standard XML, node by node.
At each XML node, we check 4 things and award points:

  1. TAG NAME    — does <bill> match <bill>? (1 point if yes)
  2. ATTRIBUTES  — does id="HB0042" match? (1 point per matching attribute)
  3. TEXT CONTENT — does "Income Tax" match? (1 point if yes)
  4. CHILDREN    — recurse into child elements (sum of all child scores)

The final score = total points earned / total points possible.
This gives partial credit: if you get the root tag right but children wrong,
you still earn some points.

Example: comparing <bill id="HB0042"> vs <bill id="HB0042">
  - Tag "bill" matches "bill"  → +1 point earned, +1 possible
  - Attr id="HB0042" matches   → +1 point earned, +1 possible
  - Then we recurse into children (metadata, sections, etc.)

Prints a single score from 0.0 to 1.0 at the end.
"""

import xml.etree.ElementTree as ET
from test_data import TEST_CASES
from convert import convert_bill_to_xml


def normalize_xml(xml_string: str) -> ET.Element:
    """
    Parse an XML string into an Element tree.

    Why: xml.etree.ElementTree ignores the <?xml ...?> declaration and
    whitespace differences, so we can compare structure not formatting.
    Returns None if the XML is broken (can't be parsed).
    """
    try:
        return ET.fromstring(xml_string.strip())
    except ET.ParseError:
        return None


def _compare_raw(expected, actual):
    """
    Recursively compare two XML elements node-by-node.
    Returns (score, total) — raw points, not a ratio.

    The caller divides score/total to get a 0.0–1.0 ratio.

    Walk-through example:
    =====================
    Expected: <bill id="HB0042">           Actual: <document>
                <metadata>...</metadata>              <id>HB0042</id>
                <sections>...</sections>            </document>
              </bill>

    At the root node:
      CHECK 1 — Tag name: "bill" vs "document" → no match → 0/1
      CHECK 2 — Attributes: expected has id="HB0042", actual has none
                → 0/1 (one attribute checked, zero matched)
      CHECK 3 — Text content: neither has direct text → skip (0/0)
      CHECK 4 — Children: expected has 2 (metadata, sections),
                actual has 1 (id) → compare first pair, penalize missing second
    """
    # Base case: if either node is missing, no points earned
    if expected is None or actual is None:
        return 0.0, 1.0

    score = 0.0  # points the agent earned
    total = 0.0  # points possible (what a perfect answer would get)

    # ─── CHECK 1: TAG NAME ───────────────────────────────────────────
    # Does the element name match?
    # e.g., expected <bill> vs actual <bill> → match! +1
    # e.g., expected <bill> vs actual <document> → no match, +0
    total += 1.0
    if expected.tag == actual.tag:
        score += 1.0

    # ─── CHECK 2: ATTRIBUTES ────────────────────────────────────────
    # Compare every attribute from BOTH sides.
    # e.g., expected: <bill id="HB0042">  actual: <bill id="HB0042">
    #   → attribute "id": both have "HB0042" → +1
    # e.g., expected: <section number="63-3024" action="amend"/>
    #        actual:  <section number="63-3024">
    #   → "number" matches (+1), "action" missing in actual (+0)
    #   → total possible = 2, earned = 1
    expected_attrs = expected.attrib
    actual_attrs = actual.attrib
    # Union of all attribute names from both sides
    all_keys = set(list(expected_attrs.keys()) + list(actual_attrs.keys()))
    if all_keys:
        for key in all_keys:
            total += 1.0  # each attribute is worth 1 point
            if expected_attrs.get(key) == actual_attrs.get(key):
                score += 1.0  # only if BOTH have the key AND values match

    # ─── CHECK 3: TEXT CONTENT ───────────────────────────────────────
    # The text directly inside the element (not in children).
    # e.g., <title>Income Tax Amendment</title>
    #   → expected text: "Income Tax Amendment"
    #   → actual text must match exactly for the point
    # Note: only checked if at least one side has text (skip empty-vs-empty)
    expected_text = (expected.text or "").strip()
    actual_text = (actual.text or "").strip()
    if expected_text or actual_text:
        total += 1.0
        if expected_text == actual_text:
            score += 1.0

    # ─── CHECK 4: CHILDREN (recursive) ──────────────────────────────
    # Compare child elements in order, position by position.
    # e.g., expected has [<metadata>, <sections>]
    #        actual has   [<metadata>]
    #   → position 0: compare <metadata> vs <metadata> (recurse!)
    #   → position 1: expected has <sections>, actual has nothing → penalty
    #
    # Three cases for each position:
    #   a) Both have a child → recurse and add their scores
    #   b) Expected has child, actual doesn't → penalty (missed content)
    #   c) Actual has extra child → small penalty (1 point)
    expected_children = list(expected)
    actual_children = list(actual)
    max_children = max(len(expected_children), len(actual_children))

    for i in range(max_children):
        if i < len(expected_children) and i < len(actual_children):
            # Case (a): both sides have a child at this position
            # Recurse! This is where the tree-walk happens.
            child_score, child_total = _compare_raw(expected_children[i], actual_children[i])
            score += child_score
            total += child_total
        else:
            if i < len(expected_children):
                # Case (b): expected has a child here, but actual is missing it
                # Penalty = whatever that expected child is worth (all its points become "possible but not earned")
                # We compare the expected child against itself to measure its weight
                _, child_total = _compare_raw(expected_children[i], expected_children[i])
                total += child_total  # adds to "possible" but NOT to "earned" → score drops
            else:
                # Case (c): actual has an EXTRA child that expected doesn't have
                # Small penalty: 1 point added to "possible" but not "earned"
                total += 1.0

    return score, total


def evaluate():
    """
    Main evaluation function. Runs convert_bill_to_xml() on each test case,
    compares against gold-standard XML, and prints per-case + average scores.

    Output format:
      Case 1: 0.2778
      Case 2: 0.4167
      ...
      ---
      score: 0.228175    ← this is THE metric the agent optimizes
    """
    scores = []
    for i, case in enumerate(TEST_CASES):
        bill = case["input"]
        expected_xml = case["expected_xml"]

        # Step 1: Run the agent's converter. If it crashes, score = 0.
        try:
            actual_xml = convert_bill_to_xml(bill)
        except Exception as e:
            print(f"Case {i+1}: CRASH — {e}")
            scores.append(0.0)
            continue

        # Step 2: Parse both XMLs into element trees.
        expected_tree = normalize_xml(expected_xml)
        actual_tree = normalize_xml(actual_xml)

        # If the agent's output isn't even valid XML, score = 0.
        # (This happens e.g. when & isn't escaped as &amp;)
        if actual_tree is None:
            print(f"Case {i+1}: INVALID XML — could not parse output")
            scores.append(0.0)
            continue

        # Step 3: Recursively compare the two XML trees.
        # Returns (points_earned, points_possible).
        raw_score, raw_total = _compare_raw(expected_tree, actual_tree)

        # Step 4: Convert to a 0.0–1.0 ratio.
        case_score = raw_score / raw_total if raw_total > 0 else 0.0
        scores.append(case_score)
        print(f"Case {i+1}: {case_score:.4f}")

    # Final score = average across all 5 test cases.
    avg = sum(scores) / len(scores) if scores else 0.0
    print(f"---")
    print(f"score: {avg:.6f}")
    return avg


if __name__ == "__main__":
    evaluate()
