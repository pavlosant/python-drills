# Day 10 - Walking a hierarchy

**Time:** 30 min | **File to create:** `work/day10.py`

An ontology is a graph: terms have parents (and some have two!). Graph walks - BFS, DFS, cycle detection - are the classic "algorithm" question a data engineer may meet.

## Setup
Copy `starters/ontology_model.py` into `work/` if you have not already. Start with:
```python
from collections import deque
from pathlib import Path

from ontology_model import Ontology

DATA = Path(__file__).resolve().parent.parent / "data"
```
The `Ontology` has `get(id)`, `children_of(id)` and terms have `.parents` and `.is_root`. Sketch the hierarchy of `data/terms.csv` on paper first (5 min): root `DIS:0001` has four children; `DIS:0010` (lung cancer) has **two parents**.

## Warm-up (3 min)
Redo `batches` (Day 3) from memory.

## Tasks (20 min)
1. `ancestors(onto, term_id)` -> a **set** of all ancestor ids (parents, grandparents, ...). Must handle multiple parents without visiting a node twice. Use a stack or recursion plus a `seen` set.
2. `descendants(onto, term_id)` -> a set of all descendant ids, using `onto.children_of` and a `deque` (BFS).
3. `depth(onto, term_id)` -> the **shortest** number of steps up to any root (a root has depth 0). Use BFS; guard against cycles with a `seen` set and raise `ValueError` if no root is reachable.
4. `path_to_root(onto, term_id)` -> list of ids from the term up to a root, always following the **first** parent. `path_to_root(onto, "DIS:0010")` -> `["DIS:0010", "DIS:0002", "DIS:0001"]`.
5. `has_cycle(parents)` -> `True`/`False` for a plain dict `{id: [parent ids]}`. Ids that appear only as parents (not as keys) are leaves. Use depth-first search with "visiting"/"done" states.

## Self-check
```python
onto = Ontology.from_csv(DATA / "terms.csv")
assert ancestors(onto, "DIS:0007") == {"DIS:0006", "DIS:0005", "DIS:0001"}
assert ancestors(onto, "DIS:0010") == {"DIS:0002", "DIS:0009", "DIS:0001"}
assert ancestors(onto, "DIS:0001") == set()
assert descendants(onto, "DIS:0005") == {"DIS:0006", "DIS:0007", "DIS:0008", "DIS:0012"}
assert descendants(onto, "DIS:0002") == {"DIS:0003", "DIS:0004", "DIS:0010"}
assert descendants(onto, "DIS:0003") == set()
assert depth(onto, "DIS:0001") == 0
assert depth(onto, "DIS:0010") == 2
assert depth(onto, "DIS:0007") == 3
assert path_to_root(onto, "DIS:0010") == ["DIS:0010", "DIS:0002", "DIS:0001"]
assert path_to_root(onto, "DIS:0001") == ["DIS:0001"]
assert has_cycle({"A": ["B"], "B": ["C"], "C": ["A"]}) is True
assert has_cycle({"A": ["B"], "B": []}) is False
assert has_cycle({"A": ["B", "C"], "B": ["D"], "C": ["D"]}) is False  # diamond, not a cycle
assert has_cycle({"A": ["A"]}) is True
```

## Think about it
- BFS or DFS for `descendants`? Does it matter for the answer? For memory?
- Why is plain recursion risky for very deep hierarchies in Python?
- If ontology import data had a cycle, which of your functions would loop forever, and how did you protect it?

## Stretch
`lowest_common_ancestor(onto, a, b)` - among ancestors shared by both terms (include the terms themselves), return the one with the greatest depth.
