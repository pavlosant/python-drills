# Day 04 - Strings, regex and file I/O (csv, json): suggested solution

> Try the exercise yourself first. Stuck? Read only the part you need, close the file, and carry on from memory. There are many valid solutions - yours does not have to match.

## `work/day04.py`

```python
import csv
import json
import re
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"

ID_IN_TEXT = re.compile(r"\b[A-Z]+:\d+\b")
VALID_ID = re.compile(r"[A-Z]{2,10}:\d{4,7}")


def normalise_label(text):
    collapsed = " ".join(text.split())
    return collapsed.strip(" .,;:").casefold()


def extract_ids(text):
    return ID_IN_TEXT.findall(text)


def is_valid_id(value):
    return VALID_ID.fullmatch(value) is not None


def _split_cell(cell):
    return [part for part in cell.split("|") if part]


def read_terms_csv(path):
    terms = []
    with open(path, newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            terms.append(
                {
                    "id": row["id"],
                    "label": row["label"],
                    "synonyms": _split_cell(row["synonyms"]),
                    "parents": _split_cell(row["parent_ids"]),
                    "category": row["category"],
                }
            )
    return terms


def write_json(data, path):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)


def read_json(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


if __name__ == "__main__":
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
    print("All checks passed")
```

## Why this works
- **normalise_label**: `" ".join(text.split())` is the idiomatic whitespace-collapse - `split()` with no argument splits on any whitespace run and drops empties. Strip the punctuation *after* collapsing so `"Asthma ;"` is also handled.
- **extract_ids**: `\b[A-Z]+:\d+\b` - the word boundaries stop it matching inside longer tokens, and the capital-letters prefix excludes `dis:3`. Always write regexes as raw strings (`r"..."`).
- **is_valid_id**: `fullmatch` anchors both ends. With `re.match` you would need `^...$` yourself, and `re.search` would happily accept `xDIS:0003`.
- **read_terms_csv**: `"".split("|")` returns `[""]`, so filter out empty strings. `newline=""` lets the csv module handle line endings itself (important for quoted fields containing newlines).
- **json**: `ensure_ascii=False` keeps non-ASCII characters readable; always set `encoding="utf-8"` explicitly because the default is platform-dependent (cp1252 on many Windows setups).

## Answers to the "think about it" questions
- `re.compile` parses the pattern once; the `re` module caches recent patterns anyway, but a compiled module-level constant is clearer and names the intent.
- Without `newline=""`, the csv module can mis-handle embedded newlines and you may get extra blank lines on Windows.
- Python's default encoding depends on the OS/locale. Being explicit makes the code behave the same on a laptop, a Lambda and a Batch container.

## What an interviewer is watching
Do you validate with `fullmatch`, handle empty cells, close files with `with`, and think about encoding?
