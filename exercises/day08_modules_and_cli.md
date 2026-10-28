# Day 8 - Modules, packages and a command-line tool

**Time:** 30 min | **Folder to create:** `work/termtools/`

Real pipelines are packages with a command-line entry point, not one long script. Today you split code into modules and add `argparse` and `logging`.

## Warm-up (5 min)
Redo the Day 6 `Term` dataclass and `Ontology.add/get` from memory.

## Target structure
```
work/
  termtools/
    __init__.py      # can be nearly empty (a docstring)
    models.py        # Term, Ontology, the two exceptions (from Day 6)
    loader.py        # load_ontology(path) -> Ontology  (reads the CSV)
    cli.py           # build_parser(), main(argv=None) -> int
    __main__.py      # lets you run:  python -m termtools ...
```
You can copy your Day 6 code (or `starters/ontology_model.py`) into `models.py` and cut it down.

## Tasks (20 min)
1. `loader.load_ontology(path)` - reads a CSV like `data/terms.csv` (pipe-separated `synonyms` and `parent_ids`) and returns an `Ontology`. Log one `DEBUG` message with the number of terms loaded, using `logging.getLogger(__name__)`.
2. `cli.build_parser()` with:
   - positional `csv_path`
   - `--find NAME` - print each match as `id<TAB>label`
   - `--stats` - print `terms: N` then `roots: N`
   - `-v/--verbose` - switch logging to DEBUG
3. `cli.main(argv=None)` returns an **exit code**:
   - `0` success (also when only `--stats` is given)
   - `1` when `--find` matched nothing
   - `2` when the file does not exist (message to **stderr**: `error: <path> not found`)
   - if neither `--find` nor `--stats` is given, print the help and return `0`
4. `__main__.py`: `from .cli import main` then `raise SystemExit(main())`.

## Self-check
Run these from inside `work/` (`cd work`):
```
python -m termtools ../data/terms.csv --find T2D        ->  DIS:0007<TAB>type 2 diabetes     (exit code 0)
python -m termtools ../data/terms.csv --find "no such"  ->  (no output)                       (exit code 1)
python -m termtools ../data/terms.csv --stats           ->  terms: 16 / roots: 1              (exit code 0)
python -m termtools ../data/missing.csv --stats         ->  error: ... not found on stderr    (exit code 2)
python -m termtools ../data/terms.csv --stats -v        ->  a DEBUG log line on stderr
```
(`echo $?` on Mac/Linux or `echo %errorlevel%` on Windows shows the exit code.)

## Think about it
- Why return an exit code from `main()` instead of calling `sys.exit` deep inside?
- Why should logs go to stderr and results to stdout?
- Why does `if __name__ == "__main__":` exist?

## Stretch
Make `main(["../data/terms.csv", "--stats"])` testable: write a pytest test using `capsys` to capture the output.
