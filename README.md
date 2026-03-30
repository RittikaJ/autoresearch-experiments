# autoresearch-experiments

A collection of autoresearch-style experiments — autonomous AI loops that iterate on code or prompts to optimize a measurable metric. Inspired by [Karpathy's autoresearch](https://github.com/karpathy/autoresearch).

## The pattern

Every experiment follows the same loop:

```
Edit → Run → Score → Keep or Discard → Repeat
```

An AI agent modifies one file, runs an evaluation, checks if the score improved, and keeps or discards the change. It repeats forever until interrupted.

## Experiments

### xml-generator (v1)

A simple warmup: optimize a Python function that converts bill data (dicts) to XML.

- **Agent edits:** `convert.py`
- **Metric:** XML similarity score (0.0–1.0)
- **Result:** hit 1.0 in one iteration (too easy!)

### pdf-to-xml (v2)

Optimize a prompt for Claude Vision to extract structured XML from Idaho legislative bill PDFs — detecting underlined (new language) and strikethrough (deleted language) text.

- **Agent edits:** `prompt.md` + model selection in `agent.py`
- **Metric:** XML tree similarity against gold-standard annotations (0.0–1.0)
- **Best score:** 0.988 (Claude Sonnet 4.6, after 42 iterations)
- **Key findings:**
  - Sonnet 4.5 plateaued at ~0.92
  - Switching to Sonnet 4.6 jumped to ~0.97
  - Detailed line numbering examples in the prompt had the biggest impact
  - Underline/strikethrough boundary precision was the hardest to get right

## How to run

Each experiment has a `program.md` with full instructions. Open a Claude Code session in the experiment folder and say:

> "Read program.md and start the experiment loop."

Requirements:
- Python 3.11+
- `ANTHROPIC_API_KEY` in a `.env` file (for pdf-to-xml)
- `pip install PyMuPDF anthropic` (for pdf-to-xml)
