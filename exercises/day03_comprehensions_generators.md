# Day 3 - Comprehensions, generators, itertools

**Time:** 30 min | **File to create:** `work/day03.py`

DataOps code constantly streams files, batches work for cloud jobs and reshapes collections. Generators keep memory flat; comprehensions keep code short.

Start your file with:
```python
import itertools
from pathlib import Path
```

## Warm-up (5 min)
Redo `top_n` and `group_by_prefix` from Day 1 from memory.

## Tasks (20 min)
1. `flatten(list_of_lists)` - `[[1, 2], [3], [], [4, 5]]` -> `[1, 2, 3, 4, 5]`. One list comprehension.
2. `batches(items, size)` - a **generator** yielding lists of at most `size` items. `list(batches(range(7), 3))` -> `[[0, 1, 2], [3, 4, 5], [6]]`. Raise `ValueError` if `size < 1`. (This is how you would split 10,000 files into AWS Batch jobs.)
3. `read_lines(path)` - a **generator** that yields each line of a text file stripped of whitespace, skipping blank lines and lines starting with `#`. It must not read the whole file into memory.
4. `group_by_first_letter(labels)` - use `itertools.groupby`. Result: `{"a": [...], "b": [...]}` with each list sorted.
5. `running_total(values)` - `[1, 2, 3, 4]` -> `[1, 3, 6, 10]` using `itertools.accumulate`.
6. `pairwise_diffs(values)` - differences between consecutive values using `zip(values, values[1:])`. `[1, 4, 9, 16]` -> `[3, 5, 7]`.
7. `label_lengths(labels)` - a dict comprehension `{label: len(label)}`.

## Self-check
```python
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
```

## Think about it
- What is the difference between `[x for x in ...]` and `(x for x in ...)`?
- Why must you sort before `itertools.groupby`?
- Can you iterate over the same generator twice? What happens?

## Stretch
Make `batches` work on any iterable (not just things you can slice) using `itertools.islice`.
