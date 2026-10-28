# Day 1 - Core data structures

**Time:** 30 min | **File to create:** `work/day01.py`

Lists, tuples, sets and dicts are the bread and butter of every live coding round.
Today is about fluency: write each function without looking anything up.

## Warm-up (5 min)
Without running anything, write down what each line prints:
```python
a = [1, 2, 3]
b = a
b.append(4)
print(a)                 # ?
print(tuple(a) == (1, 2, 3, 4))   # ?
print({1, 2, 2, 3})      # ?
print({"x": 1}.get("y", 0))       # ?
```

## Tasks (20 min)
Create `work/day01.py` and implement:

1. `dedupe_preserve_order(items)` - return a list with duplicates removed, keeping the first occurrence of each item and the original order.
   `dedupe_preserve_order([3, 1, 3, 2, 1])` -> `[3, 1, 2]`
2. `invert_synonyms(term_synonyms)` - input is `{term: [synonyms]}`. Return `{synonym_lowercased: term}`.
   `{"asthma": ["bronchial asthma"], "diabetes mellitus": ["diabetes", "DM"]}` -> `{"bronchial asthma": "asthma", "diabetes": "diabetes mellitus", "dm": "diabetes mellitus"}`
3. `ids_only_in_a(a, b)` - ids that appear in `a` but not in `b`, as a **sorted list**. Use sets.
4. `top_n(items, n)` - the `n` most common items as `(item, count)` tuples, most common first. (`collections.Counter` is fair game.)
5. `split_id(term_id)` - `"DIS:0003"` -> `("DIS", "0003")`, and `min_max(values)` -> `(smallest, largest)`. Both return **tuples**.
6. `group_by_prefix(ids)` - `{"DIS": ["DIS:1", "DIS:2"], "CHEBI": ["CHEBI:5"]}`. Use `collections.defaultdict(list)` but return a plain `dict`.

## Self-check
Paste this at the bottom of your file, then run `python work/day01.py`:
```python
assert dedupe_preserve_order([3, 1, 3, 2, 1]) == [3, 1, 2]
assert invert_synonyms(
    {"asthma": ["bronchial asthma"], "diabetes mellitus": ["diabetes", "DM"]}
) == {"bronchial asthma": "asthma", "diabetes": "diabetes mellitus", "dm": "diabetes mellitus"}
assert ids_only_in_a(["C", "A", "B"], ["B", "D"]) == ["A", "C"]
assert top_n(["x", "y", "x", "z", "x", "y"], 2) == [("x", 3), ("y", 2)]
assert split_id("DIS:0003") == ("DIS", "0003")
assert min_max([3, 9, 1]) == (1, 9)
assert group_by_prefix(["DIS:1", "CHEBI:5", "DIS:2"]) == {"DIS": ["DIS:1", "DIS:2"], "CHEBI": ["CHEBI:5"]}
```

## Think about it (answer out loud - interviewers love this)
- Why can a tuple be a dictionary key but a list cannot?
- What is the time complexity of `x in some_list` versus `x in some_set`? Why does that matter in task 3?

## Stretch
Rewrite `dedupe_preserve_order` in one line using `dict.fromkeys`.
