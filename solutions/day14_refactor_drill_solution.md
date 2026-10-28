# Day 14 - Timed refactoring drill (the Isomorphic-style round): suggested solution

> Try the exercise yourself first. Stuck? Read only the part you need, close the file, and carry on from memory. There are many valid solutions - yours does not have to match.

## Refactored module
Replace the contents of `work/messy_report.py` with:

```python
"""Refactored report builder - same behaviour, easier to read and extend."""
from collections import Counter

REPORTED_CATEGORIES = ("cancer", "metabolic", "respiratory")


def validate_record(record: dict) -> list[str]:
    """Return the list of problems found in one record (empty if it is fine)."""
    problems = []
    record_id = record["id"]
    if not record_id:
        problems.append("record with no id")
    elif ":" not in record_id:
        problems.append(f"bad id {record_id}")
    if not record["label"]:
        problems.append(f"no label for {record_id}")
    if not record["synonyms"]:
        problems.append(f"no synonyms for {record_id}")
    return problems


def count_categories(records: list[dict]) -> dict[str, int]:
    """Counts for the reported categories plus an 'other' bucket for everything else."""
    counts = Counter(record["category"] for record in records)
    reported = {category: counts[category] for category in REPORTED_CATEGORIES}
    reported["other"] = len(records) - sum(reported.values())
    return reported


def build_report(records: list[dict]) -> str:
    lines = [f"Total: {len(records)}"]
    lines += [f"{category.capitalize()}: {count}" for category, count in count_categories(records).items()]

    problems = [problem for record in records for problem in validate_record(record)]
    if problems:
        lines.append("Problems:")
        lines += [f"- {problem}" for problem in problems]
    else:
        lines.append("No problems")
    return "\n".join(lines) + "\n"
```

## Suggested refactored `work/messy_report.py`
(See the file listing above - this is the full module. It passes the same tests as the original.)

## Walkthrough of the changes
| Smell in the original | Fix |
|---|---|
| `total = total + 1` in a loop | `len(records)` |
| `cancer`, `metabolic`, `respiratory` counters with `if/elif` | one `Counter` and a `REPORTED_CATEGORIES` constant |
| `other` incremented in the `else` branch | `other = total - sum(reported)` |
| `r["id"] is None or r["id"] == ""` | `not record_id` |
| `n = 0; for s in ...: n += 1; if n == 0` | `if not record["synonyms"]` |
| `str(r["id"])` repeated | f-strings (`f"no label for {record_id}"`) |
| `out = out + ...` string concatenation | list of lines + `"\n".join(...)` |
| one 40-line function | `validate_record`, `count_categories`, `build_report` |
| no types/docs | type hints and short docstrings |

## Things to say out loud (this is the part that scores)
- "I'll keep the tests running after every small step so I always know I haven't changed behaviour."
- "The `Other` count is derived, so adding a new reported category is a one-line change to the constant."
- "Validation returns a list of problems rather than appending to a shared list - that makes it testable in isolation."
- "With more time I'd add tests for `validate_record` and `count_categories`, and think about whether `None` should be allowed for `synonyms`."

## Suggested extra tests
```python
from messy_report import count_categories, validate_record

def test_validate_record_ok():
    record = {"id": "DIS:0003", "label": "asthma", "synonyms": ["x"], "parents": [], "category": "respiratory"}
    assert validate_record(record) == []

def test_validate_record_reports_everything_wrong():
    record = {"id": "", "label": None, "synonyms": [], "parents": [], "category": "cancer"}
    assert validate_record(record) == ["record with no id", "no label for ", "no synonyms for "]

def test_count_categories_other_bucket():
    records = [{"category": "cancer"}, {"category": "stroke"}, {"category": "root"}]
    assert count_categories(records) == {"cancer": 1, "metabolic": 0, "respiratory": 0, "other": 2}
```
Note the second test documents an oddity of the original behaviour (`"no label for "` with an empty id). Spotting and noting such quirks - without silently "fixing" them - is exactly the judgement interviewers look for.

## Answers to the "think about it" questions
- Usually "extract a function" for the validation block: it cut the main function's size and made the rest obvious.
- The tests only check final text, so a bug in a helper could hide behind coincidentally correct output. Adding direct tests for the helpers first (characterisation tests) reduces that risk.
- When there are no tests and no time to write them, when the code is about to be deleted, or when the change is unrelated to the task at hand.
