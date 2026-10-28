# Day 7 - pytest, unittest and mocking

**Time:** 30 min | **Files to create:** `work/test_ontology_model.py`, `work/test_release.py`

The job ad asks for pytest/unittest and code-review experience. Today you write tests for code someone else wrote.

## Setup (2 min)
Copy these two files from `starters/` into `work/`:
- `ontology_model.py` (a finished `Term` / `Ontology` - read it first, 3 min)
- `release.py` (two tiny functions that talk to a web service)

Run tests with `pytest -q work` from the project folder (or use the VS Code Testing panel).

## Warm-up (3 min)
Skim `ontology_model.py`. Which behaviours would you test? Write 4 bullet points on paper before coding.

## Tasks (20 min)
**A. `work/test_ontology_model.py`**
1. A **fixture** `small_ontology` returning an `Ontology` with three terms: `DIS:0001 disease` (root), `DIS:0002 respiratory disease` (synonym `lung disease`, parent `DIS:0001`), `DIS:0003 asthma` (synonym `bronchial asthma`, parent `DIS:0002`).
2. Tests that use the fixture: `len`, `in`, `roots()`, `children_of("DIS:0002")`.
3. `pytest.raises` tests: `get("DIS:9999")` -> `UnknownTermError`; adding a duplicate -> `DuplicateTermError`.
4. A **parametrized** test for `find_by_name` with cases: `"asthma"`, `"BRONCHIAL ASTHMA"`, `"lung disease"`, and `"nothing"` (no match).
5. A test using **`tmp_path`**: write a small CSV (same columns as `data/terms.csv`) into it, load with `Ontology.from_csv`, assert the result.
6. A test that loads the real `data/terms.csv` and asserts 16 terms (build the path from `Path(__file__)`).

**B. `unittest` style (5 min)** - in the same file add a `unittest.TestCase` class with two tests (duplicate raises, `find_by_name` works). Use `self.assertRaises` and `setUp`.

**C. `work/test_release.py`** - mocking
1. `latest_release` happy path: use a `MagicMock` session whose `get()` returns a response with `status_code = 200` and `json()` returning `{"version": "2026-10"}`. Assert the result *and* that `session.get` was called once with `(url, timeout=10)`.
2. Failure path: status 503 -> `RuntimeError`.
3. `needs_update` using `unittest.mock.patch("release.latest_release", return_value="2026-10")` - one test where it returns `False` and one where it returns `True`.

## Think about it
- What does a fixture give you that a helper function does not?
- Why mock the HTTP session instead of calling the real server?
- Name one thing you should *not* mock.

## Stretch
Add `@pytest.fixture(scope="module")` for the real-data ontology and a test that every non-root term has at least one parent that exists in the ontology.
