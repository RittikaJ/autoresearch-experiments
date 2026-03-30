"""
Evaluation script — compares convert.py output against gold-standard HTML.
DO NOT MODIFY THIS FILE.

HOW SCORING WORKS:
=================
We parse both HTML strings into a simple tree, then compare node by node,
awarding partial credit for:

  1. TAG NAME    — does the element name match? (1 point if yes)
  2. ATTRIBUTES  — do href, src, alt, etc. match? (1 point per matching attr)
  3. TEXT CONTENT — text before/after child elements (1 point if match)
  4. CHILDREN    — recurse into child elements (sum of child scores)

The final score = total points earned / total points possible.
This gives partial credit: if you get the outer tag right but children wrong,
you still earn some points.

Prints a single score from 0.0 to 1.0 at the end.
"""

from html.parser import HTMLParser
from test_data import TEST_CASES
from convert import convert_markdown


class Node:
    """Simple tree node for parsed HTML."""
    def __init__(self, tag, attrs=None):
        self.tag = tag
        self.attrs = dict(attrs) if attrs else {}
        self.children = []  # list of Node or str (text nodes)


class TreeBuilder(HTMLParser):
    """
    Builds a tree of Node objects from an HTML string.
    Text content becomes string children. Elements become Node children.
    """
    VOID_ELEMENTS = {"br", "hr", "img", "input", "meta", "link"}

    def __init__(self):
        super().__init__()
        self.root = Node("__root__")
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs)
        self.stack[-1].children.append(node)
        if tag not in self.VOID_ELEMENTS:
            self.stack.append(node)

    def handle_endtag(self, tag):
        if len(self.stack) > 1 and self.stack[-1].tag == tag:
            self.stack.pop()

    def handle_data(self, data):
        if data:
            self.stack[-1].children.append(data)


def parse_html(html_string):
    """Parse an HTML string into a tree. Returns the root Node."""
    builder = TreeBuilder()
    builder.feed(html_string.strip())
    return builder.root


def _compare_nodes(expected, actual):
    """
    Compare two nodes recursively. Returns (score, total).
    Handles both Node objects and text strings.

    Walk-through example:
    =====================
    Expected: <p>This is <strong>bold</strong> text.</p>
    Actual:   <p>This is **bold** text.</p>

    At the <p> node:
      CHECK 1 — Tag: "p" vs "p" → match → 1/1
      CHECK 2 — Attrs: none on either side → skip
      CHECK 3 — Children: expected has ["This is ", <strong>, " text."]
                actual has ["This is **bold** text."]
                → position 0: "This is " vs "This is **bold** text." → mismatch
                → positions 1,2: expected has them, actual doesn't → penalty
    """
    # Both are text strings
    if isinstance(expected, str) and isinstance(actual, str):
        e = expected.strip()
        a = actual.strip()
        if not e and not a:
            return 0.0, 0.0  # skip empty-vs-empty
        total = 1.0
        score = 1.0 if e == a else 0.0
        return score, total

    # Type mismatch: one is text, the other is an element
    if isinstance(expected, str) or isinstance(actual, str):
        # Don't penalize empty/whitespace-only text
        if isinstance(expected, str) and not expected.strip():
            return 0.0, 0.0
        if isinstance(actual, str) and not actual.strip():
            return 0.0, 0.0
        return 0.0, 1.0

    # Both are Node objects
    score = 0.0
    total = 0.0

    # ─── CHECK 1: TAG NAME ───────────────────────────────────────────
    total += 1.0
    if expected.tag == actual.tag:
        score += 1.0

    # ─── CHECK 2: ATTRIBUTES ─────────────────────────────────────────
    all_keys = set(list(expected.attrs.keys()) + list(actual.attrs.keys()))
    for key in all_keys:
        total += 1.0
        if expected.attrs.get(key) == actual.attrs.get(key):
            score += 1.0

    # ─── CHECK 3: CHILDREN (includes text nodes) ─────────────────────
    # Filter out whitespace-only text nodes to avoid spurious mismatches
    exp_children = [c for c in expected.children
                    if not (isinstance(c, str) and not c.strip())]
    act_children = [c for c in actual.children
                    if not (isinstance(c, str) and not c.strip())]

    max_children = max(len(exp_children), len(act_children), 0)
    for i in range(max_children):
        if i < len(exp_children) and i < len(act_children):
            # Both sides have a child at this position — recurse
            child_score, child_total = _compare_nodes(
                exp_children[i], act_children[i]
            )
            score += child_score
            total += child_total
        elif i < len(exp_children):
            # Expected has a child here but actual is missing it — penalty
            _, child_total = _compare_nodes(
                exp_children[i], exp_children[i]
            )
            total += child_total
        else:
            # Actual has an extra child — small penalty
            total += 1.0

    return score, total


def _compare_children(expected_parent, actual_parent):
    """
    Compare just the children of two parent nodes (skipping the parent tag).
    Used to avoid inflating scores from the synthetic __root__ wrapper.
    """
    exp_children = [c for c in expected_parent.children
                    if not (isinstance(c, str) and not c.strip())]
    act_children = [c for c in actual_parent.children
                    if not (isinstance(c, str) and not c.strip())]

    score = 0.0
    total = 0.0
    max_children = max(len(exp_children), len(act_children), 0)
    for i in range(max_children):
        if i < len(exp_children) and i < len(act_children):
            child_score, child_total = _compare_nodes(
                exp_children[i], act_children[i]
            )
            score += child_score
            total += child_total
        elif i < len(exp_children):
            _, child_total = _compare_nodes(
                exp_children[i], exp_children[i]
            )
            total += child_total
        else:
            total += 1.0
    return score, total


def evaluate():
    """
    Run convert_markdown() on each test case, compare against gold-standard
    HTML, and print per-case + average scores.

    Output format:
      Case 1: 0.8500
      Case 2: 0.3333
      ...
      ---
      score: 0.078000    <-- THE metric the agent optimizes
    """
    scores = []
    for i, case in enumerate(TEST_CASES):
        md = case["input"]
        expected_html = case["expected_html"]

        # Step 1: Run the agent's converter. If it crashes, score = 0.
        try:
            actual_html = convert_markdown(md)
        except Exception as e:
            print(f"Case {i+1}: CRASH — {e}")
            scores.append(0.0)
            continue

        # Step 2: Validate output type.
        if not isinstance(actual_html, str):
            print(f"Case {i+1}: INVALID — convert_markdown did not return a string")
            scores.append(0.0)
            continue

        # Step 3: Parse both into DOM trees.
        expected_tree = parse_html(expected_html)
        actual_tree = parse_html(actual_html)

        # Step 4: Compare children of the root wrappers directly.
        # (Skip the synthetic __root__ node so it doesn't inflate scores.)
        raw_score, raw_total = _compare_children(expected_tree, actual_tree)

        # Step 5: Convert to 0.0–1.0 ratio.
        case_score = raw_score / raw_total if raw_total > 0 else 0.0
        scores.append(case_score)
        print(f"Case {i+1}: {case_score:.4f}")

    # Final score = average across all test cases.
    avg = sum(scores) / len(scores) if scores else 0.0
    print("---")
    print(f"score: {avg:.6f}")
    return avg


if __name__ == "__main__":
    evaluate()
