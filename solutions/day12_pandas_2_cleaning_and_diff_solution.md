# Day 12 - pandas II: clean a messy file, diff two ontology versions: suggested solution

> Try the exercise yourself first. Stuck? Read only the part you need, close the file, and carry on from memory. There are many valid solutions - yours does not have to match.

## `work/day12.py`

```python
import re
from pathlib import Path

import pandas as pd

DATA = Path(__file__).resolve().parent.parent / "data"
ID_PATTERN = re.compile(r"[A-Z]+:\d{4}")
TEXT_COLUMNS = ["id", "label", "synonyms", "parent_ids"]
COMPARE_COLUMNS = ["label", "synonyms", "parent_ids", "category"]


def clean_synonyms(text, label):
    label_key = label.casefold()
    kept = []
    for synonym in text.split("|"):
        synonym = synonym.strip().casefold()
        if synonym and synonym != label_key and synonym not in kept:
            kept.append(synonym)
    return "|".join(kept)


def clean_terms(raw):
    df = raw.copy()
    for column in TEXT_COLUMNS:
        df[column] = df[column].fillna("").astype(str).str.strip()
    df["id"] = df["id"].str.upper()
    df["parent_ids"] = df["parent_ids"].str.upper()

    problems = []
    kept_rows = []
    seen_ids = set()
    for row in df[TEXT_COLUMNS].to_dict("records"):
        if not row["label"]:
            problems.append((row["id"], "missing label"))
        elif not ID_PATTERN.fullmatch(row["id"]):
            problems.append((row["id"], "malformed id"))
        elif row["id"] in seen_ids:
            problems.append((row["id"], "duplicate id"))
        else:
            seen_ids.add(row["id"])
            row["synonyms"] = clean_synonyms(row["synonyms"], row["label"])
            kept_rows.append(row)

    for row in kept_rows:
        for parent_id in filter(None, row["parent_ids"].split("|")):
            if parent_id not in seen_ids:
                problems.append((row["id"], f"unknown parent: {parent_id}"))

    clean = pd.DataFrame(kept_rows, columns=TEXT_COLUMNS)
    report = pd.DataFrame(problems, columns=["id", "problem"])
    report = report.sort_values(["id", "problem"]).reset_index(drop=True)
    return clean, report


def diff_versions(old, new):
    old_by_id = old.fillna("").set_index("id")
    new_by_id = new.fillna("").set_index("id")
    added = sorted(new_by_id.index.difference(old_by_id.index))
    removed = sorted(old_by_id.index.difference(new_by_id.index))

    changed = {}
    for term_id in sorted(old_by_id.index.intersection(new_by_id.index)):
        differences = {}
        for column in COMPARE_COLUMNS:
            before = old_by_id.at[term_id, column]
            after = new_by_id.at[term_id, column]
            if before != after:
                differences[column] = (before, after)
        if differences:
            changed[term_id] = differences
    return {"added": added, "removed": removed, "changed": changed}


if __name__ == "__main__":
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
    print("All checks passed")
```

## Why this works
- **Order of the rules matters.** A row with an empty label is reported as "missing label" even if its id is also bad - decide the order, document it, and keep it deterministic. The "kept" ids are only collected from rows that passed every earlier rule, which is exactly what rule 4 and 6 need.
- **A row loop is fine** for a few thousand rows and reads like the spec. The vectorised version for steps 1 and 3 would be `df["id"].str.strip().str.upper()` and `df["id"].str.fullmatch(r"[A-Z]+:\d{4}")` - mention it, then say you would only optimise if profiling showed a need.
- **`clean_synonyms`** is a small pure function: easy to unit-test on its own (a good habit to show). Casefold before comparing with the label so `Asthma` equals `asthma`.
- **Problem report**: returning data *about* the data lets the caller decide whether to fail the pipeline, alert someone or just log. It also gives curators an actionable list.
- **`diff_versions`**: indexing by `id` turns the comparison into set operations (`difference`, `intersection`) - order independent, so reordered rows are not reported as changes. `.at[row, col]` is the fast scalar accessor. Comparing two strings per cell is trivial here; for big tables you would compare whole columns with vectorised `!=` and `merge(..., indicator=True)`.

## Answers to the "think about it" questions
- A loop is acceptable when clarity beats speed and the data is modest; vectorise when it becomes a measured bottleneck.
- Silent drops hide data loss, and raising on the first error makes a 10,000-row file a 10,000-attempt chore. A report lets one run surface *all* issues.
- Using the id as the index (set operations) makes the diff independent of row order.

## Stretch solution
```python
def render_diff(diff):
    lines = [f"Added ({len(diff['added'])}): " + ", ".join(diff["added"]),
             f"Removed ({len(diff['removed'])}): " + ", ".join(diff["removed"]),
             f"Changed ({len(diff['changed'])}):"]
    for term_id, columns in diff["changed"].items():
        for column, (before, after) in columns.items():
            lines.append(f"  {term_id}.{column}: {before!r} -> {after!r}")
    return "\n".join(lines)
```

## What an interviewer is watching
Do you turn a vague cleaning request into explicit, ordered rules, return a report rather than hide problems, and make the logic testable?
