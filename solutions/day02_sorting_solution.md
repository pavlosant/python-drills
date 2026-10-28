# Day 02 - Sorting: key functions, multi-key sorts, stability: suggested solution

> Try the exercise yourself first. Stuck? Read only the part you need, close the file, and carry on from memory. There are many valid solutions - yours does not have to match.

## `work/day02.py`

```python
import heapq
from operator import itemgetter


def sort_terms(terms):
    return sorted(terms, key=lambda t: (-len(t["synonyms"]), t["label"]))


def sort_by_second(pairs):
    return sorted(pairs, key=itemgetter(1))


def sort_ids_numerically(ids):
    def key(term_id):
        prefix, _, number = term_id.partition(":")
        return prefix, int(number)

    return sorted(ids, key=key)


def case_insensitive_sort(labels):
    return sorted(labels, key=str.casefold)


def sort_two_pass(records):
    by_label = sorted(records, key=lambda r: r["label"])
    return sorted(by_label, key=lambda r: r["group"])


def longest_labels(terms, k):
    biggest = heapq.nlargest(k, terms, key=lambda t: len(t["label"]))
    return [t["id"] for t in biggest]


if __name__ == "__main__":
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
    print("All checks passed")
```

## Why this works
- **sort_terms**: key functions can return a tuple; Python compares tuples element by element. Negating the count (`-len(...)`) gives "descending" for that part only. `sorted()` returns a new list, so the input is untouched.
- **sort_by_second**: `itemgetter(1)` is the tidy alternative to `lambda p: p[1]`.
- **sort_ids_numerically**: convert the numeric part to `int` inside the key. Sorting the raw strings would give `DIS:10` before `DIS:2`.
- **case_insensitive_sort**: `str.casefold` is the right tool (better than `lower` for non-ASCII). Because the sort is stable, `"Apple"` stays before `"apple"`.
- **sort_two_pass**: sort by the *least* significant key first, then by the more significant key. Stability means ties in `group` keep the label order from the first pass.
- **longest_labels**: `heapq.nlargest(k, iterable, key=...)` is O(n log k), better than sorting everything when `k` is small.

## Answers to the "think about it" questions
- If the sort were not stable, equal groups could be shuffled and the label ordering from pass one would be lost.
- `sorted()` returns a new list; `list.sort()` sorts in place and returns `None`.
- `reverse=True` **preserves** stability: equal elements keep their original order (Python does not simply reverse the result).

## What an interviewer is watching
Can you express "by X desc, then Y asc" in a single `key`? Do you avoid mutating inputs and mention complexity?
