# Day 9 - Parsing XML and OBO

**Time:** 30 min | **File to create:** `work/day09.py`

"Maintain ontology import pipelines" means turning vendor files (XML, OBO, OWL, CSV) into one internal model. Today you write two importers for the same ontology and prove they agree.

## Setup (2 min)
Copy `starters/ontology_model.py` into `work/` (skip if you did this on Day 7). Look at the two input files first:
- `data/terms.xml` - `<term id="..."><label/><synonym/><parent ref="..."/></term>`
- `data/terms.obo` - text stanzas: `[Term]` blocks with `id:`, `name:`, `synonym: "text" EXACT []`, `is_a: ID ! comment`. The file also has an **obsolete** term and a `[Typedef]` stanza you must ignore.

Start your file with:
```python
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from ontology_model import Ontology, Term

DATA = Path(__file__).resolve().parent.parent / "data"
```

## Warm-up (3 min)
Redo `extract_ids` and `is_valid_id` (Day 4) from memory.

## Tasks (20 min)
1. `parse_xml(path)` -> `list[Term]` using `xml.etree.ElementTree` (`findall`, `findtext`, `.get`).
2. `parse_obo(path)` -> `list[Term]`:
   - only `[Term]` stanzas count (skip `[Typedef]` and anything else),
   - skip stanzas with `is_obsolete: true`,
   - `synonym:` lines look like `synonym: "bronchial asthma" EXACT []` - extract the text between the quotes (a regex works well),
   - `is_a:` lines look like `is_a: DIS:0002 ! respiratory disease` - keep only the id,
   - ignore every other tag (`def:`, ...).

Both functions must return terms in file order with `synonyms` and `parents` as **tuples**.

## Self-check
```python
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
```

## Think about it
- Why is `ET.parse(...).getroot().findall("term")` fine here, but `iterparse` better for a 2 GB OWL file?
- Your OBO parser silently ignores unknown tags. Is that what you want in production? What would you log or raise?
- `partition(":")` vs `split(":")` for `"id: DIS:0003"` - which is safer and why?

## Stretch
Add `parse_any(path)` that picks the parser from the file suffix (`.xml`, `.obo`, `.csv`) and raises a clear error for anything else.
