"""Request documented HTTP endpoints with bounded response sizes."""
import json
import urllib.error
import urllib.request
from urllib.parse import urlsplit


def request(url, payload=None, headers=None, *, raw=False, timeout=60, max_bytes=30_000_000):
    address = urlsplit(url)
    if address.scheme not in {"https", "http"} or not address.hostname or address.username or address.password:
        raise ValueError("Use an HTTP(S) URL without embedded credentials")
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    request_headers = {"User-Agent": "ResearchMind-Agent-Skills/1.0"}
    if data is not None:
        request_headers["Content-Type"] = "application/json"
    request_headers.update(headers or {})
    req = urllib.request.Request(url, data=data, headers=request_headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            body = response.read(max_bytes + 1)
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"{address.hostname} returned HTTP {exc.code}") from None
    except (urllib.error.URLError, TimeoutError, OSError):
        raise RuntimeError(f"Request to {address.hostname} failed") from None
    if len(body) > max_bytes:
        raise ValueError(f"Response from {address.hostname} exceeds {max_bytes} bytes")
    return body if raw else json.loads(body)
