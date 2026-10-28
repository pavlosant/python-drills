# Day 6 - Classes II

**Time:** 30 min | **File to create:** `work/day06.py`

Upgrade Day 5 using the modern toolbox: frozen dataclasses, custom exceptions, class/static methods, properties and a small inheritance example.

## Warm-up (5 min)
Redo `Term` and `Ontology.add_term` from Day 5 from memory (no peeking).

## Tasks (20 min)
Start with:
```python
import re
from dataclasses import dataclass, FrozenInstanceError
```

1. Exceptions: `DuplicateTermError(ValueError)` and `UnknownTermError(KeyError)`.
2. `Term` as a **frozen dataclass** with fields `id`, `label`, `synonyms: tuple = ()`, `parents: tuple = ()`.
   - property `is_root` -> true if there are no parents.
   - `@staticmethod is_valid_id(value)` -> `re.fullmatch(r"[A-Z]{2,10}:\d{4,7}", value)` based.
   - `@classmethod from_dict(cls, data)` -> builds a term from a dict whose `synonyms`/`parents` are **lists** (convert to tuples; missing keys mean empty).
   - `__lt__` -> compare by `id` so `sorted(terms)` works.
3. `ObsoleteTerm(Term)` - another frozen dataclass adding `replaced_by: str | None = None`.
4. `Ontology`:
   - `add(term)` -> raises `DuplicateTermError`.
   - `get(term_id)` -> raises `UnknownTermError`.
   - `roots()` -> list of root terms sorted by id.
   - `children_of(term_id)` -> terms that list `term_id` as a parent, sorted by id.
   - `__len__`.

## Self-check
```python
t = Term.from_dict({"id": "DIS:0007", "label": "type 2 diabetes", "synonyms": ["T2D"], "parents": ["DIS:0006"]})
assert t.synonyms == ("T2D",) and t.parents == ("DIS:0006",)
assert not t.is_root and Term("DIS:0001", "disease").is_root
try:
    t.label = "changed"
    raise AssertionError("Term should be frozen")
except FrozenInstanceError:
    pass
assert Term.is_valid_id("DIS:0003") and not Term.is_valid_id("dis:3")
assert [x.id for x in sorted([Term("DIS:0009", "b"), Term("DIS:0002", "a")])] == ["DIS:0002", "DIS:0009"]
old = ObsoleteTerm("DIS:0099", "old term", replaced_by="DIS:0003")
assert isinstance(old, Term) and old.replaced_by == "DIS:0003" and old.is_root
onto = Ontology()
onto.add(Term("DIS:0001", "disease"))
onto.add(Term("DIS:0002", "respiratory disease", parents=("DIS:0001",)))
onto.add(Term("DIS:0003", "asthma", parents=("DIS:0002",)))
onto.add(Term("DIS:0004", "copd", parents=("DIS:0002",)))
assert len(onto) == 4
assert [x.id for x in onto.roots()] == ["DIS:0001"]
assert [x.id for x in onto.children_of("DIS:0002")] == ["DIS:0003", "DIS:0004"]
try:
    onto.add(Term("DIS:0003", "again"))
    raise AssertionError("expected DuplicateTermError")
except DuplicateTermError:
    pass
try:
    onto.get("DIS:9999")
    raise AssertionError("expected UnknownTermError")
except UnknownTermError:
    pass
assert issubclass(DuplicateTermError, ValueError) and issubclass(UnknownTermError, KeyError)
```

## Think about it
- What does `frozen=True` buy you, and what does it cost? Why tuples instead of lists for `synonyms`?
- Inheritance vs composition: would `ObsoleteTerm` be better as a field `obsolete: bool` on `Term`? Argue both sides.
- When do you prefer `@classmethod` over `@staticmethod`?

## Stretch
Add `Ontology.from_dicts(list_of_dicts)` as a classmethod.
