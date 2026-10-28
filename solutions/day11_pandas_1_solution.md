# Day 11 - pandas I: filter, groupby, explode, merge: suggested solution

> Try the exercise yourself first. Stuck? Read only the part you need, close the file, and carry on from memory. There are many valid solutions - yours does not have to match.

## `work/day11.py`

```python
from pathlib import Path

import pandas as pd

DATA = Path(__file__).resolve().parent.parent / "data"


def load_terms(path):
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    df["n_synonyms"] = df["synonyms"].map(lambda cell: len(cell.split("|")) if cell else 0)
    return df


def terms_with_min_synonyms(df, n):
    return sorted(df.loc[df["n_synonyms"] >= n, "id"])


def category_summary(df):
    summary = df.groupby("category").agg(
        n_terms=("id", "count"),
        mean_synonyms=("n_synonyms", "mean"),
    )
    return summary.sort_values(["n_terms", "category"], ascending=[False, True])


def synonyms_long(df):
    tidy = df.assign(synonym=df["synonyms"].str.split("|")).explode("synonym")
    tidy = tidy.loc[tidy["synonym"] != "", ["id", "synonym"]]
    return tidy.reset_index(drop=True)


def parent_labels(df):
    pairs = df.assign(parent_id=df["parent_ids"].str.split("|")).explode("parent_id")
    pairs = pairs.loc[pairs["parent_id"] != "", ["id", "label", "parent_id"]]
    parents = df[["id", "label"]].rename(columns={"id": "parent_id", "label": "parent_label"})
    return pairs.merge(parents, on="parent_id", how="left").reset_index(drop=True)


if __name__ == "__main__":
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
    print("All checks passed")
```

## Why this works
- **Loading**: `dtype=str, keep_default_na=False` keeps every cell as a string and empty cells as `""`. Otherwise pandas turns empties into `NaN` (a float), which makes `.str` methods and comparisons awkward - and a real label like `"NA"` could be silently converted to missing.
- **Derived column**: `.map(lambda ...)` over a column is fine for small data; mention that vectorised string methods are the idiom for big data. Here `"".split("|")` would give `[""]` (length 1), hence the explicit `if cell else 0`.
- **Boolean filtering** uses `.loc[mask, column]`; assigning through chained indexing (`df[mask]["y"] = 5`) works on a temporary copy and may not change `df` (in pandas 3 it never does, because of copy-on-write).
- **Named aggregation** `agg(n_terms=("id", "count"), ...)` gives clean column names. Sorting by two keys with a list of `ascending` flags is the pandas twin of Day 2's tuple key.
- **explode**: `str.split` creates lists; `explode` makes one row per list item and repeats the other columns. The root's `""` becomes one row with an empty value, which we filter out.
- **merge**: renaming the lookup copy's columns first (`id` -> `parent_id`, `label` -> `parent_label`) makes the join key explicit and avoids the `_x/_y` suffix mess. `how="left"` keeps every term-parent pair even if a parent were missing from the file (you would then see `NaN`, which is a useful signal).

## Answers to the "think about it" questions
- Chained indexing creates an intermediate object, so the assignment may land on a copy. Use `df.loc[mask, "y"] = 5`.
- With `how="inner"`, pairs whose parent is missing would silently disappear; `left` preserves them as `NaN` so you can detect broken references.
- Without `keep_default_na=False`, strings like `"NA"`, `"N/A"` or `"null"` become `NaN`; for identifiers and labels that corrupts data.

## Stretch solution
```python
rows = [(r.id, s) for r in df.itertuples() for s in r.synonyms.split("|") if s]
pure = pd.DataFrame(rows, columns=["id", "synonym"])
assert pure.equals(synonyms_long(df))
```

## What an interviewer is watching
Vectorised thinking (no `for` loop over rows), `.loc`, tidy-data reshaping, and an awareness of NaN/dtype pitfalls.
