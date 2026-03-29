# xml-optimizer

An autoresearch-style experiment loop to optimize a bill-to-XML converter.

## Setup

1. Read all files for context:
   - `test_data.py` — ground truth input/output pairs. DO NOT MODIFY.
   - `evaluate.py` — scoring script. DO NOT MODIFY.
   - `convert.py` — the file you modify.
2. Run the baseline: `python evaluate.py`
3. Create `results.tsv` with the header row.
4. Log the baseline result.

## Rules

**What you CAN do:**
- Modify `convert.py` — this is the only file you edit. Change the conversion logic however you want.

**What you CANNOT do:**
- Modify `evaluate.py` or `test_data.py`. They are read-only.
- Install new packages. Only use Python standard library.
- Look at `test_data.py` expected XML and hardcode the answers. You must write a general-purpose converter.

**The goal: get the highest score (closest to 1.0).**

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

1. Look at the current score and what's wrong (read evaluate.py output carefully).
2. Edit `convert.py` with an improvement idea.
3. `git commit` the change.
4. Run: `python evaluate.py > run.log 2>&1`
5. Read the score: `grep "^score:" run.log`
6. If empty, it crashed. Run `tail -n 20 run.log` to debug.
7. Log results to `results.tsv`.
8. If score improved → keep the commit.
9. If score is equal or worse → `git reset --hard HEAD~1` to discard.
10. Repeat.

**NEVER STOP.** Keep iterating until manually interrupted. If you hit 1.0, try simplifying the code while maintaining 1.0.

**Hints:** Look at the evaluate.py scoring to understand what matters — tag names, attributes, text content, nesting, XML declaration. Study the structure carefully and fix one thing at a time.
