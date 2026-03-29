"""
Ground truth: 5 bill dicts and their gold-standard XML outputs.
DO NOT MODIFY THIS FILE.
"""

TEST_CASES = [
    # --- Case 1: Simple bill ---
    {
        "input": {
            "bill_id": "HB0042",
            "title": "Income Tax Amendment",
            "sponsor": "Smith",
            "status": "introduced",
            "session": "2025-regular",
            "sections": [
                {"number": "63-3024", "action": "amend"},
                {"number": "63-3025", "action": "repeal"},
            ],
        },
        "expected_xml": '<?xml version="1.0" encoding="UTF-8"?>\n<bill id="HB0042">\n  <metadata>\n    <title>Income Tax Amendment</title>\n    <sponsor>Smith</sponsor>\n    <status>introduced</status>\n    <session>2025-regular</session>\n  </metadata>\n  <sections>\n    <section number="63-3024" action="amend" />\n    <section number="63-3025" action="repeal" />\n  </sections>\n</bill>',
    },
    # --- Case 2: Bill with no sections ---
    {
        "input": {
            "bill_id": "SB0101",
            "title": "Highway Safety Act",
            "sponsor": "Jones",
            "status": "passed",
            "session": "2025-regular",
            "sections": [],
        },
        "expected_xml": '<?xml version="1.0" encoding="UTF-8"?>\n<bill id="SB0101">\n  <metadata>\n    <title>Highway Safety Act</title>\n    <sponsor>Jones</sponsor>\n    <status>passed</status>\n    <session>2025-regular</session>\n  </metadata>\n  <sections />\n</bill>',
    },
    # --- Case 3: Multiple sections ---
    {
        "input": {
            "bill_id": "HB0200",
            "title": "Education Reform Act",
            "sponsor": "Garcia",
            "status": "in_committee",
            "session": "2024-special",
            "sections": [
                {"number": "33-101", "action": "amend"},
                {"number": "33-102", "action": "amend"},
                {"number": "33-103", "action": "add"},
                {"number": "33-104", "action": "repeal"},
            ],
        },
        "expected_xml": '<?xml version="1.0" encoding="UTF-8"?>\n<bill id="HB0200">\n  <metadata>\n    <title>Education Reform Act</title>\n    <sponsor>Garcia</sponsor>\n    <status>in_committee</status>\n    <session>2024-special</session>\n  </metadata>\n  <sections>\n    <section number="33-101" action="amend" />\n    <section number="33-102" action="amend" />\n    <section number="33-103" action="add" />\n    <section number="33-104" action="repeal" />\n  </sections>\n</bill>',
    },
    # --- Case 4: Special characters in title ---
    {
        "input": {
            "bill_id": "SB0055",
            "title": "Water & Land Use - Phase II",
            "sponsor": "O'Brien",
            "status": "amended",
            "session": "2025-regular",
            "sections": [
                {"number": "42-1701", "action": "amend"},
            ],
        },
        "expected_xml": '<?xml version="1.0" encoding="UTF-8"?>\n<bill id="SB0055">\n  <metadata>\n    <title>Water &amp; Land Use - Phase II</title>\n    <sponsor>O\'Brien</sponsor>\n    <status>amended</status>\n    <session>2025-regular</session>\n  </metadata>\n  <sections>\n    <section number="42-1701" action="amend" />\n  </sections>\n</bill>',
    },
    # --- Case 5: Long bill ---
    {
        "input": {
            "bill_id": "HB0999",
            "title": "Omnibus Budget Reconciliation",
            "sponsor": "Williams",
            "status": "enrolled",
            "session": "2025-regular",
            "sections": [
                {"number": "67-3501", "action": "amend"},
                {"number": "67-3502", "action": "amend"},
                {"number": "67-3503", "action": "add"},
            ],
        },
        "expected_xml": '<?xml version="1.0" encoding="UTF-8"?>\n<bill id="HB0999">\n  <metadata>\n    <title>Omnibus Budget Reconciliation</title>\n    <sponsor>Williams</sponsor>\n    <status>enrolled</status>\n    <session>2025-regular</session>\n  </metadata>\n  <sections>\n    <section number="67-3501" action="amend" />\n    <section number="67-3502" action="amend" />\n    <section number="67-3503" action="add" />\n  </sections>\n</bill>',
    },
]
