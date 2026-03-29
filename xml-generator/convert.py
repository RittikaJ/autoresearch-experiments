"""
Bill-to-XML converter.
THIS IS THE FILE THE AGENT EDITS.

Takes a bill dict and returns an XML string.
"""

import xml.etree.ElementTree as ET


def convert_bill_to_xml(bill: dict) -> str:
    """Convert a bill dictionary to XML string."""
    root = ET.Element("bill", id=bill["bill_id"])
    meta = ET.SubElement(root, "metadata")
    for f in ("title", "sponsor", "status", "session"):
        ET.SubElement(meta, f).text = bill[f]
    secs = ET.SubElement(root, "sections")
    for s in bill.get("sections", []):
        ET.SubElement(secs, "section", number=s["number"], action=s["action"])
    ET.indent(root, space="  ")
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding="unicode")
