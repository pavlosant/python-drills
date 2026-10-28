# Day 13 - Robust code: decorators, context managers, logging, a Lambda-style handler: suggested solution

> Try the exercise yourself first. Stuck? Read only the part you need, close the file, and carry on from memory. There are many valid solutions - yours does not have to match.

## `work/day13.py`

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


def retry(times, delay, exceptions, sleep=time.sleep):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as error:
                    if attempt == times:
                        raise
                    logger.warning("%s failed (attempt %d/%d): %s", func.__name__, attempt, times, error)
                    sleep(delay)

        return wrapper

    return decorator


@contextmanager
def timer():
    result = {}
    start = time.perf_counter()
    try:
        yield result
    finally:
        result["elapsed"] = time.perf_counter() - start


def lambda_handler(event, context, s3_client=None):
    for name in ("bucket", "key"):
        if not event.get(name):
            return {"statusCode": 400, "body": json.dumps({"error": f"missing {name}"})}

    if s3_client is None:
        import boto3  # imported lazily so tests and local runs do not need AWS

        s3_client = boto3.client("s3")

    logger.info("reading s3://%s/%s", event["bucket"], event["key"])
    body = s3_client.get_object(Bucket=event["bucket"], Key=event["key"])["Body"].read()
    rows = list(csv.DictReader(io.StringIO(body.decode("utf-8"))))
    roots = [row for row in rows if not row["parent_ids"]]
    return {"statusCode": 200, "body": json.dumps({"terms": len(rows), "roots": len(roots)})}


if __name__ == "__main__":
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
    print("All checks passed")
```

## Why this works
- **Decorator factory**: three nested functions - `retry(...)` returns `decorator(func)` which returns `wrapper(...)`. `functools.wraps` copies the name/docstring so tracebacks and tests still show `flaky`. The `attempt == times` check re-raises the *original* exception with its traceback (`raise` with no argument).
- **Dependency injection**: passing `sleep` means tests run instantly; passing `s3_client` means tests need no AWS account. This is the single most useful testing trick for cloud code. A default of `None` plus a lazy `import boto3` keeps production convenience.
- **`@contextmanager` + `try/finally`**: code after `yield` would be skipped on an exception without `finally`; with it, `elapsed` is always recorded, and the exception still propagates (we do not catch it).
- **Handler shape**: parse and validate the event first, do the work, return a simple dict. Lambda passes `(event, context)`; keeping logic in plain functions you can call from tests is the key design point.
- **Not catching S3 errors** is deliberate: if the object is missing or throttled, a raised exception lets Lambda/Step Functions apply their retry and dead-letter policies. Swallowing it would turn a failure into a silent success.
- On a real Lambda you would configure logging once at module level (`logging.getLogger().setLevel(logging.INFO)`) - the runtime attaches the handler for you.

## Answers to the "think about it" questions
- Injection replaces slow/unavailable collaborators with fakes, so tests are fast, deterministic and offline.
- Catching bare `Exception` hides bugs (typos, `KeyError`, `TypeError`) behind retries and delays real failures.
- Throttling, transient network/5xx errors and spot-instance interruptions are best retried by the platform (`Retry` blocks in Step Functions, `retryStrategy` in AWS Batch) with back-off; in-code retries suit small, local, idempotent operations.

## Stretch solution
```python
sleep(delay * 2 ** (attempt - 1))   # 1x, 2x, 4x ...
# with jitter:  sleep(delay * 2 ** (attempt - 1) * random.uniform(0.5, 1.5))
```

## What an interviewer is watching
Idempotency awareness, testability through injection, deliberate error handling and logging rather than prints.
