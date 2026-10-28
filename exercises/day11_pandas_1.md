# Day 11 - pandas I

**Time:** 30 min | **File to create:** `work/day11.py`

pandas questions in interviews are about *fluency*: load, filter, derive a column, group, reshape, merge. Do this one without autocomplete help if you can.

Start with:
```python
from pathlib import Path

import pandas as pd

DATA = Path(__file__).resolve().parent.parent / "data"
```
Have a look at `data/terms.csv`: columns `id, label, synonyms, parent_ids, category`; `synonyms` and `parent_ids` are `|`-separated; the root term has empty cells.

## Warm-up (5 min)
Redo `read_terms_csv` (Day 4) from memory - then notice how much shorter pandas makes it.

## Tasks (20 min)
1. `load_terms(path)` -> DataFrame. Read the CSV so that empty cells are empty **strings** (not `NaN`) - hint: `dtype=str, keep_default_na=False`. Add an integer column `n_synonyms`.
2. `terms_with_min_synonyms(df, n)` -> **sorted list** of ids with at least `n` synonyms.
3. `category_summary(df)` -> DataFrame indexed by `category` with columns `n_terms` and `mean_synonyms`, sorted by `n_terms` descending then category name ascending. (`groupby(...).agg(...)` with named aggregation.)
4. `synonyms_long(df)` -> a "tidy" DataFrame with columns `id` and `synonym`, one row per synonym (use `str.split` + `explode`; drop the empty ones; `reset_index(drop=True)`).
5. `parent_labels(df)` -> DataFrame with columns `id, label, parent_id, parent_label`, one row per (term, parent) pair - the term with two parents appears twice, the root does not appear. (`explode` + `merge` against a renamed copy of `id`/`label`.)
6. Also try (no check): `df["category"].value_counts()`, `df.query("n_synonyms > 2")`, `df.sort_values(...)`.

## Self-check
```python
df = load_terms(DATA / "terms.csv")
assert df.shape == (16, 6)
assert list(df.columns) == ["id", "label", "synonyms", "parent_ids", "category", "n_synonyms"]
assert int(df["n_synonyms"].sum()) == 30
assert int(df.loc[df["id"] == "DIS:0001", "n_synonyms"].iloc[0]) == 0
assert int(df.loc[df["id"] == "DIS:0007", "n_synonyms"].iloc[0]) == 3
ids2 = terms_with_min_synonyms(df, 2)
assert len(ids2) == 12 and ids2 == sorted(ids2)
assert "DIS:0003" not in ids2 and "DIS:0007" in ids2
summary = category_summary(df)
assert list(summary.index) == ["metabolic", "cardiovascular", "cancer", "respiratory", "root"]
assert list(summary["n_terms"]) == [5, 4, 3, 3, 1]
assert [round(x, 2) for x in summary["mean_synonyms"]] == [2.0, 2.0, 2.33, 1.67, 0.0]
long = synonyms_long(df)
assert list(long.columns) == ["id", "synonym"]
assert len(long) == 30 and (long["synonym"] != "").all()
assert long.iloc[0]["id"] == "DIS:0002" and long.iloc[0]["synonym"] == "lung disease"
pairs = parent_labels(df)
assert list(pairs.columns) == ["id", "label", "parent_id", "parent_label"]
assert len(pairs) == 16 and "DIS:0001" not in set(pairs["id"])
assert set(pairs.loc[pairs["id"] == "DIS:0010", "parent_label"]) == {"respiratory disease", "cancer"}
assert (pairs["parent_label"] != "").all() and pairs["parent_label"].notna().all()
```

## Think about it
- `df[df["x"] > 1]["y"] = 5` can silently fail. Why? What do you write instead (`.loc`)?
- `merge` `how="left"` vs `"inner"` - what changes in task 5?
- Why `keep_default_na=False`? What goes wrong if a label were literally the string `"NA"`?

## Stretch
Write `synonyms_long(df)` the pure-Python way with a list comprehension, build the DataFrame from it, and check both give the same result.
