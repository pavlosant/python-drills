# Day 12 - pandas II: data cleaning and version diffing

**Time:** 30 min | **File to create:** `work/day12.py`

Two very realistic DataOps jobs: (1) take a messy vendor file and produce a clean table plus a problem report; (2) compare two releases and say exactly what changed.

Start with:
```python
import re
from pathlib import Path

import pandas as pd

DATA = Path(__file__).resolve().parent.parent / "data"
ID_PATTERN = re.compile(r"[A-Z]+:\d{4}")
```
Open `data/messy_terms.csv` and spot the problems yourself before reading the rules.

## Warm-up (3 min)
Redo `synonyms_long` (Day 11) from memory.

## Part A - `clean_terms(raw)` (15 min)
`raw` is a DataFrame read with `pd.read_csv(path, dtype=str, keep_default_na=False)`. Return `(clean, problems)`:

Rules, applied in this order to each row:
1. Strip whitespace from `id`, `label`, `synonyms`, `parent_ids`; upper-case ids and parent ids.
2. Empty label -> problem `"missing label"`, row dropped.
3. Id not matching `[A-Z]+:\d{4}` (whole string) -> problem `"malformed id"`, row dropped.
4. Id already seen in an earlier kept row -> problem `"duplicate id"`, row dropped (keep the first).
5. Clean `synonyms`: split on `|`, strip, **casefold**, drop empties, drop any synonym equal to the label (ignoring case), remove duplicates keeping order, join with `|`.
6. After all rows are processed: any parent id that is not an id in the clean table -> problem `"unknown parent: <id>"`; the row is **kept**.

`clean` has the same four columns, rows in file order, index reset. `problems` is a DataFrame with columns `id, problem`, sorted by both columns, index reset.

## Part B - `diff_versions(old, new)` (10 min)
Both are DataFrames read from `data/terms_v1.csv` / `data/terms_v2.csv`. Return a dict:
```python
{"added": [ids only in new, sorted],
 "removed": [ids only in old, sorted],
 "changed": {id: {column: (old_value, new_value), ...}}}   # compare label, synonyms, parent_ids, category
```
Only ids present in both versions can be "changed"; only list columns that differ.

## Self-check
```python
raw = pd.read_csv(DATA / "messy_terms.csv", dtype=str, keep_default_na=False)
clean, problems = clean_terms(raw)
assert list(clean.columns) == ["id", "label", "synonyms", "parent_ids"]
assert list(clean["id"]) == ["DIS:0001", "DIS:0002", "DIS:0003", "DIS:0006", "DIS:0007"]
by_id = clean.set_index("id")
assert by_id.loc["DIS:0002", "synonyms"] == "lung disease|pulmonary disease"
assert by_id.loc["DIS:0003", "synonyms"] == "bronchial asthma"
assert by_id.loc["DIS:0006", "synonyms"] == "diabetes|dm"
assert by_id.loc["DIS:0007", "label"] == "type 2 diabetes"
assert by_id.loc["DIS:0007", "synonyms"] == "t2d|niddm"
assert by_id.loc["DIS:0002", "label"] == "Respiratory Disease"
assert list(problems.columns) == ["id", "problem"]
assert set(map(tuple, problems.to_numpy())) == {
    ("DIS:0005", "missing label"),
    ("DIS-0004", "malformed id"),
    ("DIS:12", "malformed id"),
    ("DIS:0003", "duplicate id"),
    ("DIS:0006", "unknown parent: DIS:0099"),
}
assert list(problems.index) == list(range(len(problems)))

old = pd.read_csv(DATA / "terms_v1.csv", dtype=str, keep_default_na=False)
new = pd.read_csv(DATA / "terms_v2.csv", dtype=str, keep_default_na=False)
diff = diff_versions(old, new)
assert diff["added"] == ["DIS:0017"]
assert diff["removed"] == ["DIS:0012"]
assert diff["changed"] == {
    "DIS:0007": {"synonyms": ("T2D|NIDDM|adult-onset diabetes", "T2D|NIDDM|adult-onset diabetes|type ii diabetes")},
    "DIS:0014": {"label": ("hypertension", "arterial hypertension")},
}
assert diff_versions(old, old) == {"added": [], "removed": [], "changed": {}}
```

## Think about it
- Part A uses a row loop. When is that acceptable, and what would the vectorised version look like for steps 1 and 3?
- Why return a *problem report* instead of raising on the first bad row or silently dropping rows?
- For `diff_versions`, what changes if a release can legitimately reorder rows?

## Stretch
Write a `render_diff(diff)` function that turns the dict into a human-readable text report (what you would paste into a Slack message or release note).
