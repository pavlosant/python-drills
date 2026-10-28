# Day 05 - Classes I: Term and Ontology: suggested solution

> Try the exercise yourself first. Stuck? Read only the part you need, close the file, and carry on from memory. There are many valid solutions - yours does not have to match.

## `work/day05.py`

```python
class Term:
    def __init__(self, term_id, label, synonyms=None):
        self.id = term_id
        self.label = label
        self.synonyms = list(synonyms) if synonyms else []

    def __repr__(self):
        return f"Term(id={self.id!r}, label={self.label!r})"

    def __eq__(self, other):
        if not isinstance(other, Term):
            return NotImplemented
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def matches(self, text):
        wanted = text.strip().casefold()
        return any(name.casefold() == wanted for name in [self.label, *self.synonyms])


class Ontology:
    def __init__(self):
        self._terms = {}

    def add_term(self, term):
        if term.id in self._terms:
            raise ValueError(f"duplicate term id: {term.id}")
        self._terms[term.id] = term

    def get(self, term_id):
        return self._terms.get(term_id)

    def find_by_name(self, text):
        return [term for term in self._terms.values() if term.matches(text)]

    def __len__(self):
        return len(self._terms)

    def __contains__(self, term_id):
        return term_id in self._terms

    def __iter__(self):
        return iter(self._terms.values())


if __name__ == "__main__":
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
    print("All checks passed")
```

## Why this works
- **Mutable default**: `synonyms=None` then `list(synonyms) if synonyms else []` gives each term its own list and also copies the caller's list, so later changes by the caller do not leak in.
- **`__eq__` + `__hash__`**: equal objects must have equal hashes. Python sets `__hash__` to `None` when you define `__eq__` without it, which makes the class unhashable. Returning `NotImplemented` (not `False`) lets Python try the other operand's `__eq__`.
- **Ontology storage**: a dict keyed by id gives O(1) `get`/`in`, and dicts preserve insertion order, so `__iter__` is stable.
- **`__contains__`** takes an *id* here (design choice) - say so out loud, interviewers like explicit API decisions.

## Answers to the "think about it" questions
- Dict/set lookups use the hash first, then equality. If two "equal" objects had different hashes, a set could hold duplicates.
- Default arguments are evaluated once, at function definition. Every call without an argument would share the *same* list.
- `__repr__` is for developers (unambiguous, ideally valid Python); `__str__` is for readable output. `print` uses `__str__`, falling back to `__repr__`.

## What an interviewer is watching
Clean `__init__`, correct equality/hash pairing, no mutable defaults, sensible error behaviour (`ValueError` on duplicates).
