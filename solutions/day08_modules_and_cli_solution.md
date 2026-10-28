# Day 08 - Modules, packages, argparse CLI and logging: suggested solution

> Try the exercise yourself first. Stuck? Read only the part you need, close the file, and carry on from memory. There are many valid solutions - yours does not have to match.

## `work/termtools/__init__.py`

```python
"""Small tools for working with term lists."""
```

## `work/termtools/models.py`

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Iterator


class DuplicateTermError(ValueError):
    """Raised when a term id is added twice."""


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
        return (self.label, *self.synonyms)


class Ontology:
    def __init__(self, terms: Iterable[Term] = ()) -> None:
        self._terms: dict[str, Term] = {}
        for term in terms:
            self.add(term)

    def add(self, term: Term) -> None:
        if term.id in self._terms:
            raise DuplicateTermError(term.id)
        self._terms[term.id] = term

    def find_by_name(self, text: str) -> list[Term]:
        wanted = text.strip().casefold()
        matches = [t for t in self._terms.values() if any(n.casefold() == wanted for n in t.names())]
        return sorted(matches, key=lambda t: t.id)

    def roots(self) -> list[Term]:
        return sorted((t for t in self._terms.values() if t.is_root), key=lambda t: t.id)

    def __len__(self) -> int:
        return len(self._terms)

    def __iter__(self) -> Iterator[Term]:
        return iter(self._terms.values())
```

## `work/termtools/loader.py`

```python
from __future__ import annotations

import csv
import logging
from pathlib import Path

from .models import Ontology, Term

logger = logging.getLogger(__name__)


def _split(cell: str) -> tuple[str, ...]:
    return tuple(part for part in cell.split("|") if part)


def load_ontology(path: str | Path) -> Ontology:
    terms = []
    with open(path, newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            terms.append(
                Term(
                    id=row["id"],
                    label=row["label"],
                    synonyms=_split(row["synonyms"]),
                    parents=_split(row["parent_ids"]),
                )
            )
    logger.debug("loaded %d terms from %s", len(terms), path)
    return Ontology(terms)
```

## `work/termtools/cli.py`

```python
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from .loader import load_ontology


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="termtools", description="Look things up in a term list.")
    parser.add_argument("csv_path", type=Path, help="CSV file with id,label,synonyms,parent_ids")
    parser.add_argument("--find", metavar="NAME", help="print terms whose label or synonym matches NAME")
    parser.add_argument("--stats", action="store_true", help="print term and root counts")
    parser.add_argument("-v", "--verbose", action="store_true", help="show debug logging")
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        format="%(levelname)s %(name)s: %(message)s",
    )

    try:
        ontology = load_ontology(args.csv_path)
    except FileNotFoundError:
        print(f"error: {args.csv_path} not found", file=sys.stderr)
        return 2

    exit_code = 0
    if args.find:
        matches = ontology.find_by_name(args.find)
        for term in matches:
            print(f"{term.id}\t{term.label}")
        if not matches:
            exit_code = 1
    if args.stats:
        print(f"terms: {len(ontology)}")
        print(f"roots: {len(ontology.roots())}")
    if not args.find and not args.stats:
        parser.print_help()
    return exit_code
```

## `work/termtools/__main__.py`

```python
from .cli import main

raise SystemExit(main())
```

## Why this works
- **Package layout**: `models` (data), `loader` (I/O), `cli` (user interface) - each file has one reason to change. Relative imports (`from .models import ...`) keep the package relocatable.
- **`python -m termtools`** runs `termtools/__main__.py`. Putting `raise SystemExit(main())` there turns the integer returned by `main()` into the process exit code.
- **`main(argv=None)`** takes the argument list as a parameter, which makes it trivially testable: `main(["data/terms.csv", "--stats"])`.
- **Logging**: `logging.getLogger(__name__)` in library modules, `basicConfig` only in the entry point. Logs go to stderr by default, so stdout stays clean for results that other programs might pipe.
- **Exit codes** are the contract with shell scripts and workflow engines (Step Functions, Nextflow, CI): 0 success, non-zero failure; distinct codes tell callers *what* failed.

## Answers to the "think about it" questions
- Returning a code keeps `main()` testable and lets cleanup code run; a `sys.exit` buried in a helper is surprising and hard to test.
- Pipelines pipe stdout between programs; if log messages were mixed in, they would corrupt the data stream.
- `__name__` is `"__main__"` only when the file is run directly. It stops the script's code running when the file is merely imported.

## Stretch solution (capsys test)
```python
# work/test_cli.py  (run from the work/ folder: pytest -q)
from termtools.cli import main

def test_stats(capsys):
    assert main(["../data/terms.csv", "--stats"]) == 0
    assert capsys.readouterr().out == "terms: 16\nroots: 1\n"
```

## What an interviewer is watching
Separation of concerns, an importable `main`, sensible exit codes and logging used properly (not `print` for diagnostics).
