# Day 03 - Comprehensions, generators and itertools: suggested solution

> Try the exercise yourself first. Stuck? Read only the part you need, close the file, and carry on from memory. There are many valid solutions - yours does not have to match.

## `work/day03.py`

```python
import itertools
from pathlib import Path


def flatten(list_of_lists):
    return [item for sub in list_of_lists for item in sub]


def batches(items, size):
    if size < 1:
        raise ValueError("size must be at least 1")
    iterator = iter(items)
    while True:
        batch = list(itertools.islice(iterator, size))
        if not batch:
            return
        yield batch


def read_lines(path):
    with open(path, encoding="utf-8") as handle:
        for raw in handle:
            line = raw.strip()
            if line and not line.startswith("#"):
                yield line


def group_by_first_letter(labels):
    result = {}
    for letter, group in itertools.groupby(sorted(labels), key=lambda s: s[0]):
        result[letter] = list(group)
    return result


def running_total(values):
    return list(itertools.accumulate(values))


def pairwise_diffs(values):
    return [b - a for a, b in zip(values, values[1:])]


def label_lengths(labels):
    return {label: len(label) for label in labels}


if __name__ == "__main__":
    import tempfile

    assert flatten([[1, 2], [3], [], [4, 5]]) == [1, 2, 3, 4, 5]
    assert list(batches(range(7), 3)) == [[0, 1, 2], [3, 4, 5], [6]]
    assert list(batches([], 3)) == []
    try:
        list(batches([1], 0))
        raise AssertionError("expected ValueError")
    except ValueError:
        pass
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "lines.txt"
        path.write_text("a\n\n# comment\n  b  \n")
        lines = read_lines(path)
        assert iter(lines) is lines  # a generator, not a list
        assert list(lines) == ["a", "b"]
    assert group_by_first_letter(["asthma", "apnoea", "bronchitis", "cancer", "carcinoma"]) == {
        "a": ["apnoea", "asthma"],
        "b": ["bronchitis"],
        "c": ["cancer", "carcinoma"],
    }
    assert running_total([1, 2, 3, 4]) == [1, 3, 6, 10]
    assert pairwise_diffs([1, 4, 9, 16]) == [3, 5, 7]
    assert label_lengths(["asthma", "cancer", "stroke!"]) == {"asthma": 6, "cancer": 6, "stroke!": 7}
    print("All checks passed")
```

## Why this works
- **flatten**: read the comprehension as nested loops written in the same order: `for sub in list_of_lists`, then `for item in sub`.
- **batches**: a generator keeps only one batch in memory. The `ValueError` is raised when the generator is first iterated (not when it is created) - a classic gotcha; the check still passes because `list(...)` iterates it. The `islice` version shown here also works on any iterable, which covers the stretch goal.
- **read_lines**: the `with` block lives inside the generator, so the file closes when the generator is exhausted or garbage-collected. Iterating the file object reads one line at a time.
- **group_by_first_letter**: `groupby` only groups *consecutive* equal keys, hence the `sorted(...)` first.
- **pairwise_diffs**: `zip(values, values[1:])` pairs each element with its successor and stops at the shorter one. (On Python 3.10+ `itertools.pairwise(values)` does the same.)

## Answers to the "think about it" questions
- A list comprehension builds the whole list immediately; a generator expression is lazy and produces items on demand.
- Without sorting, `groupby` creates a new group every time the key changes, so `["a","b","a"]` gives three groups.
- A generator is exhausted after one pass. A second loop over it yields nothing - a common source of silent bugs.

## What an interviewer is watching
Do you think about memory for large inputs, and can you explain laziness in one sentence?
