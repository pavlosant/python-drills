# Python interview drills (15 days x 30 minutes)

Daily practice to get your Python fluent again before a live coding round. The exercises use an
**ontology / vocabulary** theme (terms, synonyms, parent-child hierarchies)  but the skills (data structures, classes, tests,
pandas, parsing, refactoring) are the general ones every Python screen tests.

## How to use this folder
1. Open the `python-drills` folder in VS Code (File > Open Folder).
2. Make sure you have Python 3.10+ and install the packages once:
   ```
   python -m venv .venv
   # Mac/Linux:  source .venv/bin/activate      Windows:  .venv\Scripts\activate
   pip install -r requirements.txt
   ```
   (In VS Code pick the `.venv` interpreter: Ctrl/Cmd+Shift+P > "Python: Select Interpreter".)
3. Each day: open `exercises/dayNN_*.md`, set a 30-minute timer and write your code in **`work/`**.
4. Stuck? The matching file in `solutions/` has a suggested answer plus an explanation. Peek at one
   function at a time, then close it and re-type from memory.
5. Run a file with `python work/day01.py`. Run tests with `pytest -q work` (or the VS Code Testing panel).

The sample data lives in `data/` (CSV, XML, OBO, messy file, two versions of a release).
`starters/` has a few finished helper files that some days ask you to copy into `work/`.
Every solution in this folder was run and passes its own self-checks.

## Folder map
```
exercises/   the 15 daily exercise sheets (open these)
solutions/   suggested answers + explanations (open when stuck)
data/        sample input files
starters/    helper code you copy into work/ on certain days
work/        YOUR code goes here
```

## The 30-minute routine
| Minutes | What |
|---|---|
| 0-5 | Warm-up: redo yesterday's trickiest function from memory |
| 5-25 | Today's tasks - timed, no autocomplete, talk aloud |
| 25-30 | Run the self-check, tidy, write one test or one improvement |

Do the warm-ups - repetition from memory is what builds the speed that disappears under interview nerves.

## Schedule
| Day | Topic | Exercise |
|---|---|---|
| 1 | Core data structures: lists, tuples, sets, dicts | `exercises/day01_core_structures.md` |
| 2 | Sorting: key functions, multi-key sorts, stability | `exercises/day02_sorting.md` |
| 3 | Comprehensions, generators and itertools | `exercises/day03_comprehensions_generators.md` |
| 4 | Strings, regex and file I/O (csv, json) | `exercises/day04_strings_regex_files.md` |
| 5 | Classes I: Term and Ontology | `exercises/day05_classes_1.md` |
| 6 | Classes II: dataclasses, custom exceptions, inheritance | `exercises/day06_classes_2.md` |
| 7 | pytest: fixtures, parametrize, raises, tmp_path, mocking | `exercises/day07_pytest.md` |
| 8 | Modules, packages, argparse CLI and logging | `exercises/day08_modules_and_cli.md` |
| 9 | Parsing XML and OBO files into Term objects | `exercises/day09_xml_and_obo_parsing.md` |
| 10 | Hierarchies: ancestors, descendants, depth, cycles | `exercises/day10_hierarchies.md` |
| 11 | pandas I: filter, groupby, explode, merge | `exercises/day11_pandas_1.md` |
| 12 | pandas II: clean a messy file, diff two ontology versions | `exercises/day12_pandas_2_cleaning_and_diff.md` |
| 13 | Robust code: decorators, context managers, logging, a Lambda-style handler | `exercises/day13_robust_code_and_lambda.md` |
| 14 | Timed refactoring drill (the Isomorphic-style round) | `exercises/day14_refactor_drill.md` |
| 15 | Mock interview: build a term index from scratch | `exercises/day15_mock_interview.md` |

## Live-interview habits to build (practise these every day)
- **Restate the problem** and ask a clarifying question or two before typing.
- **Narrate your thinking** ("I'll use a set here because I need O(1) lookups").
- **Get the simplest working version first**, run it, then improve. A working 70% beats a perfect 0%.
- **Run your code often** - small steps mean small bugs.
- **Name things well**, keep functions short, handle the empty/duplicate/unknown cases out loud.
- **When you freeze**: stop typing, say what you *do* know, write the input and expected output as a comment, then code the smallest piece.
- **Tests**: even one or two tests written at the end show good habits.
- **Finish with trade-offs**: complexity, edge cases you skipped, what you would do next.

## If you want to extend this after day 15
- Re-do days 5-6, 9-10 and 14 with a stopwatch (the classes, parsing/graph and refactoring rounds are the likeliest).
- Learn the very basics of AWS Batch, Step Functions and Lambda (what each is for) so you can talk about them - the job lists them even though a Python screen rarely tests them directly.
- Try a new mock: "parse an OBO file and find every term whose label appears in a paragraph of text".
