"""
Ground truth: 20 markdown-to-HTML test cases, ordered easy to hard.
DO NOT MODIFY THIS FILE.

Cases 1-5:   Basic features in isolation
Cases 6-10:  Block elements
Cases 11-20: Feature interactions and edge cases (the hard stuff)
"""

TEST_CASES = [
    # ──────────────────────────────────────────────────────────────────
    # TIER 1: Basics in isolation (5 cases)
    # ──────────────────────────────────────────────────────────────────

    # --- Case 1: Plain paragraph ---
    {
        "input": "Hello, world!",
        "expected_html": "<p>Hello, world!</p>",
    },
    # --- Case 2: Heading levels ---
    {
        "input": "# Title\n\n## Subtitle\n\n### Section",
        "expected_html": "<h1>Title</h1>\n<h2>Subtitle</h2>\n<h3>Section</h3>",
    },
    # --- Case 3: Bold, italic, and inline code ---
    {
        "input": "This is **bold**, *italic*, and `code`.",
        "expected_html": "<p>This is <strong>bold</strong>, <em>italic</em>, and <code>code</code>.</p>",
    },
    # --- Case 4: Link and image ---
    {
        "input": "A [link](https://example.com) and ![img](https://example.com/i.png).",
        "expected_html": '<p>A <a href="https://example.com">link</a> and <img src="https://example.com/i.png" alt="img" />.</p>',
    },
    # --- Case 5: Multiple paragraphs ---
    {
        "input": "First paragraph.\n\nSecond paragraph.",
        "expected_html": "<p>First paragraph.</p>\n<p>Second paragraph.</p>",
    },

    # ──────────────────────────────────────────────────────────────────
    # TIER 2: Block elements (5 cases)
    # ──────────────────────────────────────────────────────────────────

    # --- Case 6: Unordered list ---
    {
        "input": "- Apple\n- Banana\n- Cherry",
        "expected_html": "<ul>\n<li>Apple</li>\n<li>Banana</li>\n<li>Cherry</li>\n</ul>",
    },
    # --- Case 7: Ordered list ---
    {
        "input": "1. First\n2. Second\n3. Third",
        "expected_html": "<ol>\n<li>First</li>\n<li>Second</li>\n<li>Third</li>\n</ol>",
    },
    # --- Case 8: Fenced code block ---
    {
        "input": "```\nfor i in range(10):\n    print(i)\n```",
        "expected_html": "<pre><code>for i in range(10):\n    print(i)\n</code></pre>",
    },
    # --- Case 9: Blockquote ---
    {
        "input": "> This is a quote.",
        "expected_html": "<blockquote>\n<p>This is a quote.</p>\n</blockquote>",
    },
    # --- Case 10: Horizontal rule ---
    {
        "input": "Above\n\n---\n\nBelow",
        "expected_html": "<p>Above</p>\n<hr />\n<p>Below</p>",
    },

    # ──────────────────────────────────────────────────────────────────
    # TIER 3: Feature interactions and edge cases (10 cases)
    # ──────────────────────────────────────────────────────────────────

    # --- Case 11: Inline formatting inside list items ---
    {
        "input": "- **Bold item**\n- An *italic* item\n- Item with `code`\n- A [link](https://example.com)",
        "expected_html": '<ul>\n<li><strong>Bold item</strong></li>\n<li>An <em>italic</em> item</li>\n<li>Item with <code>code</code></li>\n<li>A <a href="https://example.com">link</a></li>\n</ul>',
    },
    # --- Case 12: Nested unordered list ---
    {
        "input": "- Item 1\n  - Sub A\n  - Sub B\n- Item 2",
        "expected_html": "<ul>\n<li>Item 1\n<ul>\n<li>Sub A</li>\n<li>Sub B</li>\n</ul>\n</li>\n<li>Item 2</li>\n</ul>",
    },
    # --- Case 13: Blockquote with inline formatting ---
    {
        "input": "> **Important:** pay *close* attention.",
        "expected_html": "<blockquote>\n<p><strong>Important:</strong> pay <em>close</em> attention.</p>\n</blockquote>",
    },
    # --- Case 14: Multi-paragraph blockquote ---
    {
        "input": "> First quoted paragraph.\n>\n> Second quoted paragraph.",
        "expected_html": "<blockquote>\n<p>First quoted paragraph.</p>\n<p>Second quoted paragraph.</p>\n</blockquote>",
    },
    # --- Case 15: Consecutive lines = single paragraph (soft wrap) ---
    {
        "input": "Line one\nline two\nline three",
        "expected_html": "<p>Line one\nline two\nline three</p>",
    },
    # --- Case 16: Code block with markdown syntax inside (must not parse) ---
    {
        "input": "```\n# not a heading\n**not bold**\n- not a list\n```",
        "expected_html": "<pre><code># not a heading\n**not bold**\n- not a list\n</code></pre>",
    },
    # --- Case 17: Nested emphasis (bold wrapping italic) ---
    {
        "input": "This is **bold and *nested italic* inside**.",
        "expected_html": "<p>This is <strong>bold and <em>nested italic</em> inside</strong>.</p>",
    },
    # --- Case 18: Blockquote containing a list ---
    {
        "input": "> Shopping list:\n>\n> - Eggs\n> - Milk\n> - Bread",
        "expected_html": "<blockquote>\n<p>Shopping list:</p>\n<ul>\n<li>Eggs</li>\n<li>Milk</li>\n<li>Bread</li>\n</ul>\n</blockquote>",
    },
    # --- Case 19: Ordered list with inline formatting ---
    {
        "input": "1. **Step one**: do *this*\n2. Then run `make build`\n3. Visit [the site](https://example.com)",
        "expected_html": '<ol>\n<li><strong>Step one</strong>: do <em>this</em></li>\n<li>Then run <code>make build</code></li>\n<li>Visit <a href="https://example.com">the site</a></li>\n</ol>',
    },
    # --- Case 20: Kitchen sink ---
    {
        "input": "# Report\n\nA paragraph with **bold**, *italic*, and `code`.\n\n- Item with [a link](https://example.com)\n- **Bold item**\n\n> A *formatted* quote.\n>\n> Second paragraph.\n\n```\nx = 1\n```\n\n---\n\n1. **First** step\n2. Second step\n\nFinal paragraph.",
        "expected_html": '<h1>Report</h1>\n<p>A paragraph with <strong>bold</strong>, <em>italic</em>, and <code>code</code>.</p>\n<ul>\n<li>Item with <a href="https://example.com">a link</a></li>\n<li><strong>Bold item</strong></li>\n</ul>\n<blockquote>\n<p>A <em>formatted</em> quote.</p>\n<p>Second paragraph.</p>\n</blockquote>\n<pre><code>x = 1\n</code></pre>\n<hr />\n<ol>\n<li><strong>First</strong> step</li>\n<li>Second step</li>\n</ol>\n<p>Final paragraph.</p>',
    },
]
