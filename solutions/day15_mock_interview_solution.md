# Day 15 - Mock interview: build a term index from scratch: suggested solution

> Try the exercise yourself first. Stuck? Read only the part you need, close the file, and carry on from memory. There are many valid solutions - yours does not have to match.

## `work/day15.py`

```python
import re
from pathlib import Path

from ontology_model import Ontology

DATA = Path(__file__).resolve().parent.parent / "data"


def normalise(name: str) -> str:
    """Case-fold and collapse whitespace so 'Type  2 Diabetes' == 'type 2 diabetes'."""
    return re.sub(r"\s+", " ", name).strip().casefold()


class TermIndex:
    def __init__(self, ontology: Ontology) -> None:
        self._ontology = ontology
        self._ids_by_name: dict[str, set[str]] = {}
        for term in ontology:
            for name in term.names():
                self._ids_by_name.setdefault(normalise(name), set()).add(term.id)

    @classmethod
    def from_csv(cls, path) -> "TermIndex":
        return cls(Ontology.from_csv(path))

    def lookup(self, name: str) -> list[str]:
        return sorted(self._ids_by_name.get(normalise(name), ()))

    def descendants(self, term_id: str) -> set[str]:
        found: set[str] = set()
        stack = [term_id]
        while stack:
            current = stack.pop()
            for child in self._ontology.children_of(current):
                if child.id not in found:
                    found.add(child.id)
                    stack.append(child.id)
        return found

    def expand(self, name: str) -> set[str]:
        ids = set(self.lookup(name))
        for term_id in list(ids):
            ids |= self.descendants(term_id)
        return {normalise(n) for term_id in ids for n in self._ontology.get(term_id).names()}


if __name__ == "__main__":
    index = TermIndex.from_csv(DATA / "terms.csv")
    print(index.lookup("T2D"))
    print(sorted(index.expand("diabetes")))
```

## `work/test_day15.py`

```python
from pathlib import Path

import pytest

from day15 import TermIndex, normalise
from ontology_model import Ontology, Term

DATA = Path(__file__).resolve().parent.parent / "data"


@pytest.fixture(scope="module")
def index():
    return TermIndex.from_csv(DATA / "terms.csv")


@pytest.mark.parametrize(
    "name, expected",
    [
        ("COPD", ["DIS:0004"]),
        ("  lung   DISEASE ", ["DIS:0002"]),
        ("t2d", ["DIS:0007"]),
        ("not a disease", []),
    ],
)
def test_lookup_is_case_and_whitespace_insensitive(index, name, expected):
    assert index.lookup(name) == expected


def test_lookup_requires_a_full_name_match(index):
    assert index.lookup("diabet") == []
    assert index.lookup("diabetes") == ["DIS:0006"]


def test_descendants(index):
    assert index.descendants("DIS:0005") == {"DIS:0006", "DIS:0007", "DIS:0008", "DIS:0012"}
    assert index.descendants("DIS:0003") == set()


def test_expand_includes_descendant_names(index):
    names = index.expand("diabetes")
    assert len(names) == 11
    assert {"t2d", "niddm", "juvenile diabetes", "dm", "type 1 diabetes"} <= names


def test_expand_unknown_is_empty(index):
    assert index.expand("zzz") == set()


def test_shared_name_returns_every_matching_id():
    onto = Ontology([Term("X:0001", "common cold", ("cold",)), Term("X:0002", "cold sore", ("cold",))])
    assert TermIndex(onto).lookup("COLD") == ["X:0001", "X:0002"]


def test_normalise():
    assert normalise("  Type  2\tDiabetes ") == "type 2 diabetes"
```

## Why this works
- **Index design**: a single dict `normalised name -> set of ids` gives O(1) lookups, and using a *set* of ids means two concepts sharing a synonym are handled correctly (the edge case most candidates miss). Build it once in `__init__`; queries are then cheap.
- **`normalise`** is one small function used on both the way in (indexing) and the way out (lookup) - if they ever differed, lookups would silently fail.
- **`descendants`** reuses `Ontology.children_of` rather than re-implementing hierarchy logic; the `found` set protects against terms with two parents and against cycles.
- **`expand`** composes the smaller pieces: `lookup` -> `descendants` -> `names`. Small functions that compose are easy to test and easy to explain aloud.
- **Tests**: parametrize for the common cases, one edge case for the shared synonym, one for "full match only" (`"diabet"` must not match), one for the unknown name. A module-scoped fixture avoids re-reading the CSV for every test.

## What to say in the closing minutes (trade-offs)
- "Normalisation here is `casefold` plus whitespace collapsing; real vocabularies may also need Unicode normalisation (NFKC) and punctuation handling."
- "The index is built eagerly and is immutable - fine for a batch pipeline; for a long-running service I'd rebuild on new releases or add incremental updates."
- "`expand` returns normalised names; if the caller needs original spellings I'd return the terms instead and let them choose."
- "For very large hierarchies I'd precompute descendant sets or use a closure table, and put a limit or cycle check on `descendants`."

## Common mistakes
1. Using a dict of `name -> id` (loses the shared-synonym case).
2. Normalising only the query or only the index.
3. Writing tests last with no time left - get a *working* version first, then tests, then polish.
4. Going silent while thinking. Narrate: "I'm choosing a set here because..."

## After the mock
Note three things you would do differently, then repeat a *different* mock next week (for example: "parse an OBO file and find terms whose label appears in a block of free text").
