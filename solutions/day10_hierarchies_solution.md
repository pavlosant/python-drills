# Day 10 - Hierarchies: ancestors, descendants, depth, cycles: suggested solution

> Try the exercise yourself first. Stuck? Read only the part you need, close the file, and carry on from memory. There are many valid solutions - yours does not have to match.

## `work/day10.py`

```python
from collections import deque
from pathlib import Path

from ontology_model import Ontology

DATA = Path(__file__).resolve().parent.parent / "data"


def ancestors(onto, term_id):
    seen = set()
    stack = list(onto.get(term_id).parents)
    while stack:
        parent_id = stack.pop()
        if parent_id in seen:
            continue
        seen.add(parent_id)
        stack.extend(onto.get(parent_id).parents)
    return seen


def descendants(onto, term_id):
    seen = set()
    queue = deque(t.id for t in onto.children_of(term_id))
    while queue:
        child_id = queue.popleft()
        if child_id in seen:
            continue
        seen.add(child_id)
        queue.extend(t.id for t in onto.children_of(child_id))
    return seen


def depth(onto, term_id):
    seen = {term_id}
    queue = deque([(term_id, 0)])
    while queue:
        current, steps = queue.popleft()
        term = onto.get(current)
        if term.is_root:
            return steps
        for parent_id in term.parents:
            if parent_id not in seen:
                seen.add(parent_id)
                queue.append((parent_id, steps + 1))
    raise ValueError(f"no root reachable from {term_id}")


def path_to_root(onto, term_id):
    path = [term_id]
    seen = {term_id}
    term = onto.get(term_id)
    while not term.is_root:
        parent_id = term.parents[0]
        if parent_id in seen:
            raise ValueError(f"cycle detected at {parent_id}")
        seen.add(parent_id)
        path.append(parent_id)
        term = onto.get(parent_id)
    return path


def has_cycle(parents):
    visiting, done = set(), set()

    def visit(node):
        if node in done:
            return False
        if node in visiting:
            return True
        visiting.add(node)
        for parent in parents.get(node, []):
            if visit(parent):
                return True
        visiting.discard(node)
        done.add(node)
        return False

    return any(visit(node) for node in list(parents))


if __name__ == "__main__":
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
    print("All checks passed")
```

## Why this works
- **ancestors**: a stack gives depth-first traversal; the `seen` set both prevents repeated work (a term reachable by two paths, like `DIS:0001` from `DIS:0010`) and makes cycles harmless.
- **descendants**: BFS with `collections.deque` - `popleft()` is O(1), whereas `list.pop(0)` is O(n). Using `seen` means a term with two parents is only expanded once.
- **depth**: BFS visits nodes in order of distance, so the *first* root it reaches is at the shortest distance. DFS would not guarantee that.
- **path_to_root**: a simple loop following `parents[0]`; the `seen` check turns a would-be infinite loop into a clear error.
- **has_cycle**: three-colour DFS - `visiting` = on the current path, `done` = fully explored. Meeting a `visiting` node means a back edge = cycle. The diamond case (`A->B->D`, `A->C->D`) reaches `D` twice but `D` is already `done`, so it is correctly *not* a cycle. Recursion depth is fine for ontology-sized hierarchies; for huge graphs convert to an explicit stack.

## Answers to the "think about it" questions
- The *set* of descendants is identical for BFS and DFS. BFS uses memory proportional to the widest level, DFS to the deepest path. BFS is required when order/distance matters (as in `depth`).
- Python's default recursion limit is about 1000 frames; a pathological chain of 5000 parents would raise `RecursionError`. Iterative versions avoid that.
- Without the `seen` sets, `ancestors`, `descendants` and `depth` would all loop forever on a cycle. Every traversal needs a visited set when data comes from outside.

## Stretch solution
```python
def lowest_common_ancestor(onto, a, b):
    shared = (ancestors(onto, a) | {a}) & (ancestors(onto, b) | {b})
    return max(shared, key=lambda t: depth(onto, t)) if shared else None
```

## What an interviewer is watching
Choosing BFS vs DFS deliberately, handling multi-parent (diamond) structures, and guarding against cycles in untrusted data.
