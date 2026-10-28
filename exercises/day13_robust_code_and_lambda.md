# Day 13 - Robust code and cloud shape

**Time:** 30 min | **File to create:** `work/day13.py`

The role mentions AWS Batch, Step Functions and Lambda. You do not need to know AWS deeply for a Python screen, but you should write code that is shaped for it: small handlers, dependencies passed in, errors handled deliberately.

Start with:
```python
import csv
import functools
import io
import json
import logging
import time
from contextlib import contextmanager
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
logger = logging.getLogger(__name__)
```

## Warm-up (5 min)
Redo `ancestors` (Day 10) from memory - or the Day 8 CLI skeleton if you prefer.

## Tasks (20 min)
1. `retry(times, delay, exceptions, sleep=time.sleep)` - a **decorator factory**. The wrapped function is attempted up to `times` times; if it raises one of `exceptions` it waits `delay` seconds (via the injected `sleep`) and tries again; after the last failure the exception propagates. Other exceptions propagate immediately. Use `functools.wraps`. Log a warning on each retry.
2. `timer()` - a context manager (`@contextmanager`) that yields a dict and, on exit (even if the body raised), stores `elapsed` seconds in it: `with timer() as t: ...; print(t["elapsed"])`. Exceptions must still propagate.
3. `lambda_handler(event, context, s3_client=None)`:
   - `event` has `bucket` and `key`. If either is missing -> return `{"statusCode": 400, "body": json.dumps({"error": "missing <name>"})}`.
   - Fetch the object with `s3_client.get_object(Bucket=..., Key=...)["Body"].read()`, decode as UTF-8, parse it as the terms CSV, and return `{"statusCode": 200, "body": json.dumps({"terms": N, "roots": N})}` where *roots* are rows with no `parent_ids`.
   - If `s3_client` is `None`, create one **lazily** with `boto3.client("s3")` *inside the function* (so importing your module and testing it does not need boto3 or AWS credentials).
   - Do **not** catch S3 errors - let them raise so the platform can retry. Log the bucket/key at INFO level.

## Self-check
```python
from unittest.mock import MagicMock

attempts = {"n": 0}


@retry(times=3, delay=0, exceptions=(ValueError,), sleep=lambda seconds: None)
def flaky():
    attempts["n"] += 1
    if attempts["n"] < 3:
        raise ValueError("boom")
    return "ok"


assert flaky() == "ok" and attempts["n"] == 3
assert flaky.__name__ == "flaky"  # functools.wraps


@retry(times=2, delay=0, exceptions=(ValueError,), sleep=lambda seconds: None)
def always_fails():
    raise ValueError("nope")


try:
    always_fails()
    raise AssertionError("expected ValueError")
except ValueError:
    pass


@retry(times=3, delay=0, exceptions=(ValueError,), sleep=lambda seconds: None)
def wrong_exception():
    raise KeyError("not retried")


try:
    wrong_exception()
    raise AssertionError("expected KeyError")
except KeyError:
    pass

with timer() as t:
    pass
assert t["elapsed"] >= 0
try:
    with timer() as t2:
        raise KeyError("x")
    raise AssertionError("expected KeyError")
except KeyError:
    assert "elapsed" in t2

csv_bytes = (DATA / "terms.csv").read_bytes()
s3 = MagicMock()
s3.get_object.return_value = {"Body": io.BytesIO(csv_bytes)}
response = lambda_handler({"bucket": "my-bucket", "key": "terms.csv"}, None, s3_client=s3)
assert response["statusCode"] == 200
assert json.loads(response["body"]) == {"terms": 16, "roots": 1}
s3.get_object.assert_called_once_with(Bucket="my-bucket", Key="terms.csv")
bad = lambda_handler({"bucket": "my-bucket"}, None, s3_client=s3)
assert bad["statusCode"] == 400 and "key" in json.loads(bad["body"])["error"]
```

## Think about it
- Why inject `sleep` and `s3_client` as parameters? What does that do for testing?
- Why should a retry decorator only catch the exceptions you name, not bare `Exception`?
- Which AWS-side failures should be retried automatically (Step Functions `Retry`, Batch retry strategy) rather than inside your code?

## Stretch
Add exponential back-off to `retry` (`delay * 2 ** attempt`) and a `jitter` option.
