# autoresearch: pdf-to-xml

An autoresearch-style experiment loop to optimize a prompt for PDF-to-XML conversion.
The goal: get Claude Vision to extract structured XML (with underline/strikethrough markup)
from Idaho legislative bill PDFs.

## Setup

1. Read all files for context:
   - `evaluate.py` — scoring script. DO NOT MODIFY.
   - `gold/` — gold-standard XML files. DO NOT MODIFY.
   - `pdfs/` — source PDF files. DO NOT MODIFY.
   - `prompt.md` — **the file you modify.** This is the prompt sent to Claude Vision.
2. Run the baseline: `python evaluate.py`
3. Create `results.tsv` with the header row.
4. Log the baseline result.

## Rules

**What you CAN do:**
- Modify `prompt.md` — change the instructions sent to the vision model however you want.
- Modify the `model` parameter in `agent.py` — you can try different Anthropic models to see which performs best. Only change the model ID string, nothing else in the file.

**Available models to try (from https://platform.claude.com/docs/en/about-claude/models/overview):**
- `claude-sonnet-4-6` — latest Sonnet (fast + smart)
- `claude-sonnet-4-5-20250929` — previous Sonnet (current default)
- `claude-opus-4-6` — most intelligent, slower, more expensive
- `claude-haiku-4-5-20251001` — fastest, cheapest, less accurate

**What you CANNOT do:**
- Modify `evaluate.py`, gold XMLs, or PDFs. They are read-only.
- Modify anything in `agent.py` other than the model ID string.

**The goal: get the highest score (closest to 1.0).**

The score measures how well Claude Vision's XML output matches the gold-standard XML.
Key things the prompt needs to get right:
- Correct `<Page>` and `<Line>` structure with num attributes
- Detect **underlined text** (new legislative language) → wrap in `<underline>` tags
- Detect **strikethrough text** (deleted language) → wrap in `<strikethrough>` tags
- Accurate text extraction (exact words, punctuation, hyphens)
- Correct line numbering

## Logging results

Log each experiment to `results.tsv` (tab-separated):

```
commit	score	status	description
```

- commit: git short hash (7 chars)
- score: the score from evaluate.py (e.g. 0.456789)
- status: `keep`, `discard`, or `crash`
- description: what you tried

## The experiment loop

LOOP FOREVER:

1. Look at the current score and what's wrong (read the output XMLs to compare against gold).
2. Edit `prompt.md` with an improvement idea.
3. `git commit` the change.
4. Run: `python evaluate.py > run.log 2>&1`
5. Read the score: `grep "^score:" run.log`
6. If empty, it crashed. Run `tail -n 20 run.log` to debug.
7. Log results to `results.tsv`.
8. If score improved → keep the commit.
9. If score is equal or worse → `git reset --hard HEAD~1` to discard.
10. Repeat.

**NEVER STOP.** Keep iterating until manually interrupted.

**Cost awareness:** Each iteration calls Claude Vision API (~$0.01-0.05 per page, 2 pages per run). Budget roughly ~$0.10 per iteration.

**Hints:**
- Compare your output XMLs (`output_page1.xml`, `output_page2.xml`) against the gold files to see exactly what's wrong.
- Focus on one problem at a time: first get the structure right, then fix text accuracy, then fix underline/strikethrough detection.
- Be very specific in the prompt about what underlined and strikethrough text looks like visually.
- Legislative bills have line numbers on the left margin — make sure the prompt handles these correctly.
