"""Tiny module used in the Day 7 mocking exercise."""


def latest_release(session, url):
    """Ask a release server for the newest version string."""
    response = session.get(url, timeout=10)
    if response.status_code != 200:
        raise RuntimeError(f"release lookup failed: {response.status_code}")
    return response.json()["version"]


def needs_update(session, url, current_version):
    return latest_release(session, url) != current_version
