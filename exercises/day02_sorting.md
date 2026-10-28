# Day 2 - Sorting

**Time:** 30 min | **File to create:** `work/day02.py`

Sorting questions are rarely about the algorithm - they are about `sorted(..., key=...)`, tuples as keys, and knowing Python's sort is stable.

## Warm-up (5 min)
Redo one function from Day 1 from memory (pick the one you found hardest).

## Tasks (20 min)
1. `sort_terms(terms)` - `terms` is a list of dicts with keys `id`, `label`, `synonyms` (a list). Return a **new** list sorted by number of synonyms (most first), then by label (A-Z). Do not mutate the input.
2. `sort_by_second(pairs)` - sort a list of tuples by their second element, ascending.
   `[("a", 3), ("b", 1), ("c", 2)]` -> `[("b", 1), ("c", 2), ("a", 3)]`
3. `sort_ids_numerically(ids)` - ids look like `"DIS:10"`. Sort by prefix, then by the **number** (so `DIS:2` comes before `DIS:10`).
4. `case_insensitive_sort(labels)` - sort ignoring case. Equal-ignoring-case items must keep their original relative order.
5. `sort_two_pass(records)` - records have `group` and `label`. Do **not** use a tuple key: sort by `label` first, then sort that result by `group`. It must give the same answer as sorting by `(group, label)`. This proves you understand stability.
6. `longest_labels(terms, k)` - return the ids of the `k` terms with the longest labels, longest first. Use `heapq.nlargest`.

## Self-check
```python
terms = [
    {"id": "DIS:0003", "label": "asthma", "synonyms": ["bronchial asthma"]},
    {"id": "DIS:0007", "label": "type 2 diabetes", "synonyms": ["T2D", "NIDDM", "adult-onset diabetes"]},
    {"id": "DIS:0004", "label": "copd", "synonyms": ["COPD", "chronic bronchitis"]},
    {"id": "DIS:0001", "label": "disease", "synonyms": []},
    {"id": "DIS:0002", "label": "abc", "synonyms": ["x", "y"]},
]
snapshot = [t["id"] for t in terms]
assert [t["id"] for t in sort_terms(terms)] == ["DIS:0007", "DIS:0002", "DIS:0004", "DIS:0003", "DIS:0001"]
assert [t["id"] for t in terms] == snapshot  # input not mutated
assert sort_by_second([("a", 3), ("b", 1), ("c", 2)]) == [("b", 1), ("c", 2), ("a", 3)]
assert sort_ids_numerically(["DIS:10", "DIS:2", "CHEBI:15", "DIS:9"]) == ["CHEBI:15", "DIS:2", "DIS:9", "DIS:10"]
assert case_insensitive_sort(["banana", "Apple", "cherry", "apple"]) == ["Apple", "apple", "banana", "cherry"]
records = [
    {"group": "b", "label": "x"},
    {"group": "a", "label": "z"},
    {"group": "a", "label": "y"},
    {"group": "b", "label": "w"},
]
assert sort_two_pass(records) == sorted(records, key=lambda r: (r["group"], r["label"]))
assert longest_labels(terms, 2) == ["DIS:0007", "DIS:0001"]
```

## Think about it
- Why does the two-pass sort in task 5 work? What would break if Python's sort were not stable?
- `list.sort()` vs `sorted()` - which returns a new list, and which mutates?
- What does `reverse=True` do to stability?

## Stretch
Sort the rows of a CSV file (`data/terms.csv`, read with the `csv` module) by `category`, then by number of parents, descending.
