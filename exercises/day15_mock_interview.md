# Day 15 - Mock interview

**Time:** 30 min, strictly timed | **Files:** `work/day15.py` and `work/test_day15.py`

Treat this like the real thing. Set a 30-minute timer, **speak out loud the whole time**, and do not open the solution until the timer ends.

## Setup
Copy `starters/ontology_model.py` into `work/` if it is not there already. (You are allowed to use it - in a real interview you would be told what libraries or existing code you can rely on. Say "can I assume a `Term`/`Ontology` model exists?" first!)

## The brief (read it aloud)
> We receive vocabulary files from curators. We need a **`TermIndex`** so that a search service can look up what a user typed and expand it to every name a concept is known by.
>
> 1. Build the index from an `Ontology`. Names are matched **case-insensitively** and ignoring extra whitespace.
> 2. `lookup(name)` returns the **sorted list of term ids** whose label or any synonym matches the name exactly. Unknown name -> empty list. A name shared by two terms returns both.
> 3. `descendants(term_id)` returns the set of ids below a term.
> 4. `expand(name)` returns the **set of all names** (labels and synonyms, normalised: case-folded, single-spaced) of every term that `lookup(name)` finds **plus all their descendants**. Unknown name -> empty set. Example: `expand("diabetes")` returns the 11 names of *diabetes mellitus*, *type 2 diabetes* and *type 1 diabetes*.
> 5. Add a `TermIndex.from_csv(path)` convenience constructor.
> 6. Write **at least three tests**, including one edge case.

## Suggested timeline
| Minutes | Do this |
|---|---|
| 0-3 | Restate the problem, ask clarifying questions (duplicates? normalisation? what if there is a cycle?) |
| 3-8 | Design aloud: dict from normalised name -> set of ids; reuse `Ontology.children_of` for descendants |
| 8-18 | Implement the simplest working version, run it on `data/terms.csv` |
| 18-26 | Tests, then edge cases |
| 26-30 | Summarise trade-offs and what you would do next (caching, case folding vs Unicode normalisation, huge ontologies, cycles) |

## Self-check
`expand("diabetes")` should contain `"t2d"`, `"niddm"`, `"juvenile diabetes"`, `"dm"` and have length 11. `lookup("COPD")` should return `["DIS:0004"]`. `lookup("lung disease")` should return `["DIS:0002"]`.

## Debrief questions (answer after the timer)
- Where did you lose time? What would you do differently?
- Did you get to a *working* version before polishing?
- Did you tell the interviewer what you were thinking at each step?

## Stretch
Make `TermIndex` rebuild itself cheaply when one term is added, or add `expand(name, max_depth=None)`.
