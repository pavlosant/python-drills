# Day 4 - Strings, regex, file I/O

**Time:** 30 min | **File to create:** `work/day04.py`

Ontology work is mostly cleaning text and moving it between formats. Today: normalise labels, pull identifiers out of text with regex, read CSV, write/read JSON.

Start your file with this so data paths work no matter where you run it from:
```python
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
```

## Warm-up (5 min)
Redo `batches` and `read_lines` from Day 3 from memory.

## Tasks (20 min)
1. `normalise_label(text)` - casefold, collapse any run of whitespace to a single space, strip leading/trailing whitespace **and** leading/trailing `.,;:` characters.
   `"  Type 2   Diabetes. "` -> `"type 2 diabetes"`; `"Asthma;"` -> `"asthma"`.
2. `extract_ids(text)` - return all identifiers of the form `PREFIX:digits` (prefix = capital letters) in order of appearance.
   `"Mapped CHEBI:15377 and DIS:0007, not dis:3 or X-12"` -> `["CHEBI:15377", "DIS:0007"]`
3. `is_valid_id(value)` - true only for 2-10 capital letters, a colon, then 4-7 digits (the *whole* string). Use `re.fullmatch`.
4. `read_terms_csv(path)` - read `data/terms.csv` with `csv.DictReader` and return a list of dicts: `id`, `label`, `synonyms` (list), `parents` (list), `category`. Empty cells become empty lists.
5. `write_json(data, path)` and `read_json(path)` - pretty-printed (indent 2), UTF-8, and they must round-trip.

## Self-check
```python
import tempfile

assert normalise_label("  Type 2   Diabetes. ") == "type 2 diabetes"
assert normalise_label("Asthma;") == "asthma"
assert normalise_label("COPD") == "copd"
assert extract_ids("Mapped CHEBI:15377 and DIS:0007, not dis:3 or X-12") == ["CHEBI:15377", "DIS:0007"]
assert is_valid_id("DIS:0003")
assert not is_valid_id("dis:0003")
assert not is_valid_id("DIS:3")
assert not is_valid_id("DIS-0003")
assert not is_valid_id("xDIS:0003")
terms = read_terms_csv(DATA / "terms.csv")
assert len(terms) == 16
by_id = {t["id"]: t for t in terms}
assert by_id["DIS:0010"]["parents"] == ["DIS:0002", "DIS:0009"]
assert by_id["DIS:0001"]["synonyms"] == [] and by_id["DIS:0001"]["parents"] == []
assert by_id["DIS:0007"]["synonyms"] == ["T2D", "NIDDM", "adult-onset diabetes"]
with tempfile.TemporaryDirectory() as folder:
    out = Path(folder) / "terms.json"
    write_json(terms, out)
    assert read_json(out) == terms
    assert out.read_text(encoding="utf-8").startswith("[\n  {")
```

## Think about it
- Why use `re.compile` for a pattern used in a loop?
- What does `newline=""` do when opening a CSV file?
- When do you pass `encoding="utf-8"` explicitly - and what goes wrong on Windows if you do not?

## Stretch
Make `extract_ids` ignore ids that are not valid according to `is_valid_id` (so `DIS:3` is dropped even if written in capitals).
