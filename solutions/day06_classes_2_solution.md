# Day 06 - Classes II: dataclasses, custom exceptions, inheritance: suggested solution

> Try the exercise yourself first. Stuck? Read only the part you need, close the file, and carry on from memory. There are many valid solutions - yours does not have to match.

## `work/day06.py`

```python
import re
from dataclasses import FrozenInstanceError, dataclass

ID_PATTERN = re.compile(r"[A-Z]{2,10}:\d{4,7}")


class DuplicateTermError(ValueError):
    """Raised when a term id is added twice."""


class UnknownTermError(KeyError):
    """Raised when a term id is not in the ontology."""


@dataclass(frozen=True)
class Term:
    id: str
    label: str
    synonyms: tuple = ()
    parents: tuple = ()

    @property
    def is_root(self):
        return not self.parents

    @staticmethod
    def is_valid_id(value):
        return ID_PATTERN.fullmatch(value) is not None

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data["id"],
            label=data["label"],
            synonyms=tuple(data.get("synonyms", ())),
            parents=tuple(data.get("parents", ())),
        )

    def __lt__(self, other):
        if not isinstance(other, Term):
            return NotImplemented
        return self.id < other.id


@dataclass(frozen=True)
class ObsoleteTerm(Term):
    replaced_by: str | None = None


class Ontology:
    def __init__(self):
        self._terms = {}

    def add(self, term):
        if term.id in self._terms:
            raise DuplicateTermError(term.id)
        self._terms[term.id] = term

    def get(self, term_id):
        try:
            return self._terms[term_id]
        except KeyError:
            raise UnknownTermError(term_id) from None

    def roots(self):
        return sorted(t for t in self._terms.values() if t.is_root)

    def children_of(self, term_id):
        self.get(term_id)
        return sorted(t for t in self._terms.values() if term_id in t.parents)

    def __len__(self):
        return len(self._terms)


if __name__ == "__main__":
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
    print("All checks passed")
```

## Why this works
- **Frozen dataclass**: immutability makes instances hashable and safe to share; it also forces you to use tuples (lists are mutable and unhashable, which would break the generated `__hash__`). The cost: to "change" a term you create a new one (`dataclasses.replace`).
- **`from_dict`** is a `classmethod` because it needs `cls` (so a subclass calling `ObsoleteTerm.from_dict` would build the right type). `is_valid_id` is a `staticmethod` because it needs neither the instance nor the class.
- **Custom exceptions** that subclass built-ins (`ValueError`, `KeyError`) let callers catch broadly *or* narrowly. `raise ... from None` hides the noisy internal `KeyError` traceback.
- **`__lt__`** returning `NotImplemented` for foreign types is the correct protocol; `sorted()` only needs `__lt__`.
- **`ObsoleteTerm`**: all fields have defaults after the parent's defaults, which is what dataclass inheritance requires.
- `str | None` needs Python 3.10+. On 3.9 write `Optional[str]` (or add `from __future__ import annotations`).

## Answers to the "think about it" questions
- Frozen = hashable, thread-safe, no accidental mutation. Tuples because the generated hash includes all fields and tuples are hashable when their contents are.
- Subclass: clear type checks (`isinstance`) but a rigid hierarchy. Flag field: simpler and easier to serialise, but every consumer must remember to check it. Either is defensible - say which you choose and why.
- Use `@classmethod` when you need the class (alternative constructors, subclass-friendly); `@staticmethod` is just a namespaced function.

## What an interviewer is watching
Alternative constructors, immutability trade-offs and a sensible exception hierarchy show "production" thinking.
