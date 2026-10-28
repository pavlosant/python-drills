# Day 5 - Classes I

**Time:** 30 min | **File to create:** `work/day05.py`

Build a tiny in-memory ontology from scratch using plain classes. Dunder methods, equality and hashing are the favourite probes in an interview.

## Warm-up (5 min)
Redo `dedupe_preserve_order` and `invert_synonyms` (Day 1) from memory.

## Tasks (20 min)
Write two classes.

**`Term`**
- `__init__(self, term_id, label, synonyms=None)` - store `id`, `label`, and `synonyms` (a list; if `None` use an empty list - **never** use a mutable default argument).
- `__repr__` -> `Term(id='DIS:0003', label='asthma')`
- `__eq__` - two terms are equal if their `id` is equal. Return `NotImplemented` if `other` is not a `Term`.
- `__hash__` - consistent with `__eq__` (so terms work in sets and as dict keys).
- `matches(text)` - true if `text` (ignoring case and surrounding whitespace) equals the label or any synonym.

**`Ontology`**
- `__init__(self)` - starts empty.
- `add_term(term)` - raises `ValueError` if the id already exists.
- `get(term_id)` - returns the term, or `None` if unknown.
- `find_by_name(text)` - list of terms whose `matches(text)` is true.
- `__len__`, `__contains__(term_id)` and `__iter__` (iterate over terms in insertion order).

## Self-check
```python
asthma = Term("DIS:0003", "asthma", ["bronchial asthma"])
assert repr(asthma) == "Term(id='DIS:0003', label='asthma')"
assert asthma == Term("DIS:0003", "a different label")
assert asthma != Term("DIS:0004", "asthma")
assert asthma != "DIS:0003"
assert len({asthma, Term("DIS:0003", "x")}) == 1
assert asthma.matches("  Bronchial ASTHMA ")
assert asthma.matches("asthma")
assert not asthma.matches("asth")
assert Term("DIS:0001", "disease").synonyms == []
onto = Ontology()
onto.add_term(asthma)
onto.add_term(Term("DIS:0006", "diabetes mellitus", ["diabetes", "DM"]))
assert len(onto) == 2
assert "DIS:0006" in onto and "DIS:9999" not in onto
assert onto.get("nope") is None
assert [t.id for t in onto.find_by_name("dm")] == ["DIS:0006"]
assert onto.find_by_name("nothing") == []
try:
    onto.add_term(Term("DIS:0003", "dup"))
    raise AssertionError("expected ValueError")
except ValueError:
    pass
assert [t.id for t in onto] == ["DIS:0003", "DIS:0006"]
```

## Think about it
- Why must you define `__hash__` when you define `__eq__`?
- Why is `def __init__(self, synonyms=[])` a bug?
- What is the difference between `__repr__` and `__str__`?

## Stretch
Add `__lt__` so terms can be sorted by id, and a `from_csv` classmethod that reads `data/terms.csv`.
