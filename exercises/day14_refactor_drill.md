# Day 14 - Refactoring drill

**Time:** 30 min, strictly timed | **Files:** `starters/messy_report.py` and `starters/test_messy_report.py`

Live "pair programming" rounds often hand you a messy class or function with a few tests and ask you to make it better *while narrating your decisions*. This is that round. The goal is not perfection - it is a calm, visible process.

## Setup (1 min)
Copy **both** starter files into `work/`, then run `pytest -q work`. They should all pass. They describe the behaviour you must keep.

## The process to practise (say each step out loud)
1. **0-3 min: read and summarise.** "This function counts records by category, validates each record, and formats a text report." Look at the tests - they are the spec.
2. **3-6 min: list smells before touching code.** Repeated `x = x + 1` patterns, three copy-pasted `if/elif` branches, manual counting loop (`n = n + 1`), string concatenation in a loop, one function doing three jobs, magic strings, no types or docstrings.
3. **6-22 min: small safe steps, running the tests after each one:**
   - replace manual counting with `len(...)` / `Counter`,
   - extract `validate_record(record) -> list[str]`,
   - extract `count_categories(records)`,
   - build the report with a list of lines and `"\n".join(...)` / f-strings,
   - replace `x == None or x == ""` style checks with truthiness (`not x`).
4. **22-27 min: polish.** Type hints, docstrings, constants for the magic strings.
5. **27-30 min: say what you would do next**, e.g. "add tests for the extracted helpers, decide what should happen for an unknown category, and consider returning a dataclass instead of one big string."

## Rules
- Tests must stay green after every step.
- No behaviour changes (the exact output format is the contract).
- If you are running out of time, stop refactoring and *say* what is left - that is exactly what the interviewer wants to hear.

## After the timer
- Compare with `solutions/day14_refactor_drill_solution.md`.
- Add one new test for `validate_record` and one for `count_categories` in `work/test_messy_report.py`.

## Think about it
- Which refactoring step gave the biggest readability win per minute?
- The tests only cover the final string. What risk does that create while refactoring, and what would you add first if you had more time?
- When is it better *not* to refactor?

## Stretch
Do the drill a second time on a different day with a stopwatch, and try to reach the extracted-helpers step in under 12 minutes.
