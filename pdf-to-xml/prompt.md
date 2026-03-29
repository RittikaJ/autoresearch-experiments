You are extracting text from a page of an Idaho legislative bill PDF into structured XML.

Output ONLY the raw XML below, with no explanation, no markdown code fences, and no other text. Use this structure:

```xml
<Page num="PAGE_NUMBER">
  <Line num="1">text here</Line>
  <Line num="2">more text</Line>
</Page>
```

## Critical Rules

### Line numbering
- The bill has printed line numbers in the left margin (1, 2, 3, ..., up to 54 or so per page).
- Use THOSE printed line numbers as the `num` attribute on each `<Line>` element.
- IMPORTANT: The line numbers are CONTINUOUS from 1 through the last line on the page. The header lines at the top (like "LEGISLATURE OF THE STATE OF IDAHO", "Sixty-eighth Legislature...", "IN THE HOUSE OF REPRESENTATIVES", "HOUSE BILL NO. 2", etc.) are included in the line numbering. Do NOT restart numbering after the header.
- Lines that are blank in the original should be empty: `<Line num="X"></Line>`
- Do NOT skip any line numbers. Every line from 1 through the last must appear.
- The page should have all lines up to the last printed line number (typically around 54 for a full page, or fewer for the last page).
- There are often blank lines between sections (e.g. before "SECTION 3."). Make sure to include these as empty `<Line>` elements.

### Text extraction
- Extract the text EXACTLY as printed — preserve punctuation, capitalization, and hyphens.
- Words hyphenated at line breaks: look very carefully at exactly which letters appear before the hyphen. Copy them character by character. For example, if the line ends with "PE-" do NOT write "PETI-" — only write what is visually on that line.
- Do NOT merge lines together. Each printed line is its own `<Line>` element.
- For header lines, collapse multiple spaces into a single space.

### Underline and Strikethrough detection — THIS IS CRITICAL
This is a legislative bill showing amendments. It uses two visual styles to mark changes:

1. **Underlined text** = NEW language being added to the law. This text has a solid line drawn beneath it. Wrap it in `<underline>` tags.

2. **Strikethrough text** = OLD language being deleted from the law. This text has a horizontal line drawn through the middle of the characters. Wrap it in `<strikethrough>` tags.

Rules for markup tags:
- Place `<underline>` and `<strikethrough>` tags INSIDE the `<Line>` element, wrapping ONLY the affected text.
- Be very precise about which exact words are underlined or struck through. Do not include adjacent regular words in the tags.
- A single line may contain regular text, underlined text, and strikethrough text mixed together.
- Underlined or strikethrough text may span across multiple consecutive lines. Each line gets its own tags.
- Example: `<Line num="24">PROVED. The manner of voting <strikethrough>upon</strikethrough> <underline>on</underline> measures submitted to the people shall</Line>`

Look carefully at the visual appearance of each word. Strikethrough text has a line running through the middle of the letters. Underlined text has a line running below the letters. Regular text has no lines.
