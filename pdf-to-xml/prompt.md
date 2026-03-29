You are extracting text from a page of an Idaho legislative bill PDF into structured XML.

Output ONLY the raw XML below, with no explanation, no markdown code fences, and no other text.

## Line numbering — READ CAREFULLY

Look at the LEFT MARGIN of the page. There are printed line numbers (1, 2, 3, ...) running down the left side. These numbers apply to EVERY line on the page, INCLUDING the header lines at the very top.

For example, on page 1:
- Line 1 = "LEGISLATURE OF THE STATE OF IDAHO"
- Line 2 = "Sixty-eighth Legislature First Regular Session - 2025"
- Line 3 = (blank)
- Line 4 = "IN THE HOUSE OF REPRESENTATIVES"
- ...and so on, continuously numbered through the entire page.

The line numbers do NOT restart. They go from 1 through the last line (typically around 54 for a full page).

You MUST:
- Use the printed left-margin line numbers as the `num` attribute on each `<Line>`.
- Include EVERY line number from 1 through the last, with NO gaps.
- Represent blank lines as empty elements: `<Line num="X"></Line>`
- There are blank lines between sections (e.g., before and after "HOUSE BILL NO. 2", before "SECTION 1.", before "SECTION 2.", before "SECTION 3.", etc.). Include all of them as empty `<Line>` elements.
- Double-check: your last `<Line>` num attribute should match the last printed line number on the left margin.

## Text extraction

- Extract text EXACTLY as printed — preserve punctuation, capitalization, and hyphens.
- Hyphenated words at line breaks: copy ONLY the letters that appear on THAT line. If the line ends "PE-", write "PE-", NOT "PETI-".
- Do NOT merge lines. Each printed line = one `<Line>` element.
- For header lines, collapse multiple spaces into a single space.
- If there are unusual spaces within words (e.g., a word appears visually as "confl ict" with a space), reproduce the text EXACTLY as it appears, including the space.

## Underline and Strikethrough detection

This is a legislative bill showing amendments:

1. **Underlined text** = NEW language being added. Has a solid line drawn BENEATH the text. Wrap in `<underline>` tags.

2. **Strikethrough text** = OLD language being deleted. Has a line drawn THROUGH THE MIDDLE of the characters. Wrap in `<strikethrough>` tags.

Rules:
- Place tags INSIDE `<Line>`, wrapping ONLY the affected words.
- Be precise about boundaries — do not include adjacent unmarked words.
- A line may mix regular, underlined, and strikethrough text.
- When underlined/strikethrough spans multiple lines, each line gets its own tags.
- Include a space between adjacent `</strikethrough>` and `<underline>` tags when the original has a space there.
- A single punctuation mark (like a comma) can be struck through by itself.
- Example: `<Line num="24">PROVED. The manner of voting <strikethrough>upon</strikethrough> <underline>on</underline> measures submitted to the people shall</Line>`

## Output format

```xml
<Page num="PAGE_NUMBER">
  <Line num="1">text here</Line>
  <Line num="2">more text</Line>
  ...
</Page>
```
