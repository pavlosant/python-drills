# Day 01 - Core data structures: lists, tuples, sets, dicts: suggested solution

> Try the exercise yourself first. Stuck? Read only the part you need, close the file, and carry on from memory. There are many valid solutions - yours does not have to match.

## `work/day01.py`

```python
from collections import Counter, defaultdict


def dedupe_preserve_order(items):
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def invert_synonyms(term_synonyms):
    return {
        synonym.lower(): term
        for term, synonyms in term_synonyms.items()
        for synonym in synonyms
    }


def ids_only_in_a(a, b):
    return sorted(set(a) - set(b))


def top_n(items, n):
    return Counter(items).most_common(n)


def split_id(term_id):
    prefix, _, number = term_id.partition(":")
    return prefix, number


def min_max(values):
    return min(values), max(values)


def group_by_prefix(ids):
    groups = defaultdict(list)
    for term_id in ids:
        prefix, _ = split_id(term_id)
        groups[prefix].append(term_id)
    return dict(groups)


if __name__ == "__main__":
    assert dedupe_preserve_order([3, 1, 3, 2, 1]) == [3, 1, 2]
    assert invert_synonyms(
        {"asthma": ["bronchial asthma"], "diabetes mellitus": ["diabetes", "DM"]}
    ) == {"bronchial asthma": "asthma", "diabetes": "diabetes mellitus", "dm": "diabetes mellitus"}
    assert ids_only_in_a(["C", "A", "B"], ["B", "D"]) == ["A", "C"]
    assert top_n(["x", "y", "x", "z", "x", "y"], 2) == [("x", 3), ("y", 2)]
    assert split_id("DIS:0003") == ("DIS", "0003")
    assert min_max([3, 9, 1]) == (1, 9)
    assert group_by_prefix(["DIS:1", "CHEBI:5", "DIS:2"]) == {"DIS": ["DIS:1", "DIS:2"], "CHEBI": ["CHEBI:5"]}
    print("All checks passed")
```

## Why this works
- **Dedupe**: a `set` gives O(1) membership checks while the list keeps order. Stretch version: `list(dict.fromkeys(items))` - dicts preserve insertion order and keys are unique.
- **invert_synonyms**: a dict comprehension with two `for` clauses reads left to right like nested loops (outer loop first).
- **ids_only_in_a**: set difference is O(len(a)+len(b)); `a_item in b_list` inside a loop would be O(len(a) x len(b)).
- **top_n**: `Counter.most_common(n)` already returns `(item, count)` tuples. Ties come out in first-seen order.
- **split_id**: `str.partition` always returns a 3-tuple, so there is no index error on odd input (unlike `split(":")[1]`).
- **group_by_prefix**: `defaultdict(list)` removes the "if key not in dict" boilerplate.

## Answers to the "think about it" questions
- Dict keys must be **hashable**, and hashing requires the object not to change. A tuple of hashable items is immutable, so its hash is stable. A list can be mutated, so Python refuses to hash it.
- `x in list` scans the list: O(n). `x in set` hashes: O(1) on average. Inside a loop that is the difference between O(n) and O(n^2).

## What an interviewer is watching
Do you reach for the right structure without hesitating, and do you say *why* ("I'll use a set for O(1) lookups")?
