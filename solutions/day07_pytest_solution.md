# Day 07 - pytest: fixtures, parametrize, raises, tmp_path, mocking: suggested solution

> Try the exercise yourself first. Stuck? Read only the part you need, close the file, and carry on from memory. There are many valid solutions - yours does not have to match.

## `work/test_ontology_model.py`

```python
import unittest
from pathlib import Path

import pytest

from ontology_model import DuplicateTermError, Ontology, Term, UnknownTermError

DATA = Path(__file__).resolve().parent.parent / "data"


def build_small_ontology():
    return Ontology(
        [
            Term("DIS:0001", "disease"),
            Term("DIS:0002", "respiratory disease", ("lung disease",), ("DIS:0001",)),
            Term("DIS:0003", "asthma", ("bronchial asthma",), ("DIS:0002",)),
        ]
    )


@pytest.fixture
def small_ontology():
    return build_small_ontology()


def test_len_and_contains(small_ontology):
    assert len(small_ontology) == 3
    assert "DIS:0003" in small_ontology
    assert "DIS:9999" not in small_ontology


def test_roots(small_ontology):
    assert [t.id for t in small_ontology.roots()] == ["DIS:0001"]


def test_children_of(small_ontology):
    assert [t.id for t in small_ontology.children_of("DIS:0002")] == ["DIS:0003"]


def test_get_unknown_raises(small_ontology):
    with pytest.raises(UnknownTermError):
        small_ontology.get("DIS:9999")


def test_add_duplicate_raises(small_ontology):
    with pytest.raises(DuplicateTermError):
        small_ontology.add(Term("DIS:0003", "again"))


@pytest.mark.parametrize(
    "query, expected_ids",
    [
        ("asthma", ["DIS:0003"]),
        ("BRONCHIAL ASTHMA", ["DIS:0003"]),
        ("lung disease", ["DIS:0002"]),
        ("nothing", []),
    ],
)
def test_find_by_name(small_ontology, query, expected_ids):
    assert [t.id for t in small_ontology.find_by_name(query)] == expected_ids


def test_from_csv_tmp_path(tmp_path):
    csv_file = tmp_path / "mini.csv"
    csv_file.write_text(
        "id,label,synonyms,parent_ids,category\n"
        "DIS:0001,disease,,,root\n"
        "DIS:0002,respiratory disease,lung disease|pulmonary disease,DIS:0001,respiratory\n",
        encoding="utf-8",
    )
    onto = Ontology.from_csv(csv_file)
    assert len(onto) == 2
    child = onto.get("DIS:0002")
    assert child.synonyms == ("lung disease", "pulmonary disease")
    assert child.parents == ("DIS:0001",)
    assert onto.get("DIS:0001").is_root


def test_from_csv_real_data():
    onto = Ontology.from_csv(DATA / "terms.csv")
    assert len(onto) == 16
    assert [t.id for t in onto.roots()] == ["DIS:0001"]


class TestOntologyUnittest(unittest.TestCase):
    def setUp(self):
        self.onto = build_small_ontology()

    def test_duplicate_raises(self):
        with self.assertRaises(DuplicateTermError):
            self.onto.add(Term("DIS:0001", "again"))

    def test_find_by_name(self):
        self.assertEqual([t.id for t in self.onto.find_by_name("Asthma")], ["DIS:0003"])
```

## `work/test_release.py`

```python
from unittest.mock import MagicMock, patch

import pytest

import release

URL = "https://example.org/releases/latest"


def make_session(status_code, payload=None):
    session = MagicMock()
    session.get.return_value.status_code = status_code
    session.get.return_value.json.return_value = payload or {}
    return session


def test_latest_release_happy_path():
    session = make_session(200, {"version": "2026-10"})
    assert release.latest_release(session, URL) == "2026-10"
    session.get.assert_called_once_with(URL, timeout=10)


def test_latest_release_failure_raises():
    session = make_session(503)
    with pytest.raises(RuntimeError, match="503"):
        release.latest_release(session, URL)


@pytest.mark.parametrize("latest, current, expected", [("2026-10", "2026-09", True), ("2026-10", "2026-10", False)])
def test_needs_update_with_patch(latest, current, expected):
    with patch("release.latest_release", return_value=latest) as fake:
        assert release.needs_update(None, URL, current) is expected
        fake.assert_called_once()
```

## Why this works
- **Fixture** `small_ontology`: pytest builds a fresh object for each test that asks for it by name, so tests cannot leak state into each other. (`build_small_ontology()` is a plain helper so the `unittest` class can reuse the same data.)
- **`pytest.raises`** is a context manager - the test fails if the exception is *not* raised. `match="503"` also checks the message with a regex.
- **`parametrize`** turns four cases into four separately reported tests with one function body. Name your parameters so failure output is readable.
- **`tmp_path`** is a unique temporary directory per test (a `pathlib.Path`), cleaned up automatically - never write test files into the repo.
- **`MagicMock`** records calls and returns whatever you configure. `assert_called_once_with` checks the *interaction*, the assertion on the return value checks the *result*.
- **`patch("release.latest_release")`** replaces the name *where it is looked up* (module `release`). That "patch where it is used" rule is the number-one mocking gotcha.
- **unittest**: `setUp` runs before each test method, `assertRaises` is the context-manager equivalent of `pytest.raises`. pytest also runs `unittest.TestCase` classes, so you can mix styles.

## Answers to the "think about it" questions
- A fixture gets dependency-injected by name, can be shared via scope (`module`, `session`), can clean up with `yield`, and shows up in failure reports.
- Real servers are slow, flaky, may cost money and cannot easily produce a 503 on demand. Mocks make tests fast and deterministic.
- Do not mock the thing you are testing, and be wary of mocking simple pure functions or your own data classes - you end up testing the mock.

## What an interviewer is watching (and what makes a good code review)
Test names that describe behaviour, one clear assertion focus per test, edge cases (empty, duplicate, unknown), and no real network or filesystem side effects.
