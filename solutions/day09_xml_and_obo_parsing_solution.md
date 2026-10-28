# Day 09 - Parsing XML and OBO files into Term objects: suggested solution

> Try the exercise yourself first. Stuck? Read only the part you need, close the file, and carry on from memory. There are many valid solutions - yours does not have to match.

## `work/day09.py`

```python
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from ontology_model import Ontology, Term

DATA = Path(__file__).resolve().parent.parent / "data"

QUOTED = re.compile(r'"(.*)"')


def parse_xml(path):
    root = ET.parse(path).getroot()
    terms = []
    for element in root.findall("term"):
        terms.append(
            Term(
                id=element.get("id"),
                label=element.findtext("label"),
                synonyms=tuple(s.text for s in element.findall("synonym")),
                parents=tuple(p.get("ref") for p in element.findall("parent")),
            )
        )
    return terms


def _read_obo_stanzas(path):
    """Yield (stanza_type, list_of_(tag, value)) for every [Stanza] in the file."""
    stanza_type = None
    pairs = []
    for raw in Path(path).read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line.startswith("[") and line.endswith("]"):
            if stanza_type is not None:
                yield stanza_type, pairs
            stanza_type, pairs = line[1:-1], []
        elif stanza_type is not None and line:
            tag, _, value = line.partition(":")
            pairs.append((tag.strip(), value.strip()))
    if stanza_type is not None:
        yield stanza_type, pairs


def parse_obo(path):
    terms = []
    for stanza_type, pairs in _read_obo_stanzas(path):
        if stanza_type != "Term":
            continue
        if ("is_obsolete", "true") in pairs:
            continue
        term_id = label = None
        synonyms, parents = [], []
        for tag, value in pairs:
            if tag == "id":
                term_id = value
            elif tag == "name":
                label = value
            elif tag == "synonym":
                match = QUOTED.search(value)
                if match:
                    synonyms.append(match.group(1))
            elif tag == "is_a":
                parents.append(value.split("!")[0].strip())
        terms.append(Term(id=term_id, label=label, synonyms=tuple(synonyms), parents=tuple(parents)))
    return terms


if __name__ == "__main__":
    csv_terms = sorted(Ontology.from_csv(DATA / "terms.csv"), key=lambda t: t.id)
    xml_terms = parse_xml(DATA / "terms.xml")
    obo_terms = parse_obo(DATA / "terms.obo")
    assert len(xml_terms) == 16
    assert len(obo_terms) == 16  # DIS:0099 is obsolete and [Typedef] is ignored
    assert all(isinstance(t.synonyms, tuple) and isinstance(t.parents, tuple) for t in xml_terms + obo_terms)
    assert sorted(xml_terms, key=lambda t: t.id) == csv_terms
    assert sorted(obo_terms, key=lambda t: t.id) == csv_terms
    assert "DIS:0099" not in {t.id for t in obo_terms}
    lung_cancer = next(t for t in obo_terms if t.id == "DIS:0010")
    assert lung_cancer.parents == ("DIS:0002", "DIS:0009")
    assert lung_cancer.synonyms == ("lung carcinoma", "pulmonary neoplasm")
    print("All checks passed")
```

## Why this works
- **XML**: `findall("term")` returns direct children named `term`; `findtext` returns `None` instead of raising when a child is missing; `.get("id")` reads an attribute.
- **OBO**: first split the file into stanzas (a small generator), then interpret each one. Separating "reading the format" from "building Terms" makes both halves easy to test. `line.partition(":")` splits on the **first** colon only, so `id: DIS:0003` gives `("id", ":", " DIS:0003")` - `split(":")` would shred the value.
- **Obsolete terms**: checking `("is_obsolete", "true") in pairs` keeps the logic readable.
- **`value.split("!")[0].strip()`** drops the trailing human-readable comment on `is_a` lines.
- Comparing `sorted(xml_terms) == csv_terms` works because `Term` is a dataclass: equality compares all fields (so tuple order must match).

## Answers to the "think about it" questions
- `parse` loads the whole tree into memory. `iterparse` streams elements and lets you clear them as you go - essential for huge files.
- In production, log (or count) unknown tags and **fail loudly** on structural problems (missing `id`, duplicate ids). Silent ignoring hides data loss.
- `partition` always returns three parts and splits once; `split(":")` splits on every colon, so a value containing colons gets broken up.

## Stretch solution
```python
def parse_any(path):
    parsers = {".xml": parse_xml, ".obo": parse_obo, ".csv": lambda p: list(Ontology.from_csv(p))}
    suffix = Path(path).suffix.lower()
    try:
        return parsers[suffix](path)
    except KeyError:
        raise ValueError(f"unsupported file type: {suffix!r}") from None
```

## What an interviewer is watching
Do you read the sample file before coding, separate parsing from modelling, and think about bad input and big files?
