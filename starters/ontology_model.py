"""Reference Term / Ontology classes used by the drills from Day 7 onwards.

Copy this file into your work/ folder as work/ontology_model.py so that
`from ontology_model import Ontology, Term` works in your own files.
(You can use your own Day 6 version instead if you prefer.)
"""
from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from typing import Iterable, Iterator

ID_PATTERN = re.compile(r"[A-Z]{2,10}:\d{4,7}")


class DuplicateTermError(ValueError):
    """Raised when a term id is added twice."""


class UnknownTermError(KeyError):
    """Raised when a term id is not in the ontology."""


@dataclass(frozen=True)
class Term:
    id: str
    label: str
    synonyms: tuple[str, ...] = ()
    parents: tuple[str, ...] = ()

    @property
    def is_root(self) -> bool:
        return not self.parents

    def names(self) -> tuple[str, ...]:
        """Label first, then synonyms."""
        return (self.label, *self.synonyms)

    @staticmethod
    def is_valid_id(value: str) -> bool:
        return ID_PATTERN.fullmatch(value) is not None

    @classmethod
    def from_dict(cls, data: dict) -> "Term":
        return cls(
            id=data["id"],
            label=data["label"],
            synonyms=tuple(data.get("synonyms", ())),
            parents=tuple(data.get("parents", ())),
        )

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Term):
            return NotImplemented
        return self.id < other.id


class Ontology:
    def __init__(self, terms: Iterable[Term] = ()) -> None:
        self._terms: dict[str, Term] = {}
        for term in terms:
            self.add(term)

    def add(self, term: Term) -> None:
        if term.id in self._terms:
            raise DuplicateTermError(term.id)
        self._terms[term.id] = term

    def get(self, term_id: str) -> Term:
        try:
            return self._terms[term_id]
        except KeyError:
            raise UnknownTermError(term_id) from None

    def find_by_name(self, text: str) -> list[Term]:
        wanted = text.strip().casefold()
        matches = [t for t in self._terms.values() if any(n.casefold() == wanted for n in t.names())]
        return sorted(matches, key=lambda t: t.id)

    def roots(self) -> list[Term]:
        return sorted((t for t in self._terms.values() if t.is_root), key=lambda t: t.id)

    def children_of(self, term_id: str) -> list[Term]:
        self.get(term_id)  # raises UnknownTermError for unknown ids
        return sorted((t for t in self._terms.values() if term_id in t.parents), key=lambda t: t.id)

    def __len__(self) -> int:
        return len(self._terms)

    def __contains__(self, term_id: object) -> bool:
        return term_id in self._terms

    def __iter__(self) -> Iterator[Term]:
        return iter(self._terms.values())

    @classmethod
    def from_csv(cls, path) -> "Ontology":
        """Load data/terms.csv style files (synonyms and parent_ids are |-separated)."""
        terms = []
        with open(path, newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                terms.append(
                    Term(
                        id=row["id"],
                        label=row["label"],
                        synonyms=tuple(s for s in row["synonyms"].split("|") if s),
                        parents=tuple(p for p in row["parent_ids"].split("|") if p),
                    )
                )
        return cls(terms)
