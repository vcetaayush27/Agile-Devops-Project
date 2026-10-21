"""Read-only smoke check; proves that the expected release serves the home page."""
import argparse
import json
from html.parser import HTMLParser
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


class PageText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)

    def normalized(self):
        return " ".join(" ".join(self.parts).split())


def verify(base_url, expected_version, timeout=120, interval=3):
    parts = urlsplit(base_url)
    if parts.scheme not in ("http", "https") or not parts.netloc or parts.query or parts.fragment:
        raise ValueError("Use an http(s) base URL with no query string or fragment.")
    if not expected_version or timeout <= 0 or interval <= 0:
        raise ValueError("Expected version and positive timeout/interval are required.")
    base_url = base_url.rstrip("/")
    deadline = time.monotonic() + timeout
    reason = "No response"
    while time.monotonic() < deadline:
        try:
            request = Request(base_url + "/health", headers={"Cache-Control": "no-cache"})
            with urlopen(request, timeout=min(10, max(.1, deadline - time.monotonic()))) as response:
                health = json.load(response)
                if response.status != 200 or not isinstance(health, dict) or health.get("status") != "ok":
                    raise ValueError("Health endpoint did not report ok")
                if health.get("version") != expected_version:
                    raise ValueError("The expected release is not live yet")
            with urlopen(base_url + "/", timeout=min(10, max(.1, deadline - time.monotonic()))) as response:
                parser = PageText()
                parser.feed(response.read().decode("utf-8"))
                body = parser.normalized()
                if response.status != 200 or not all(message in body for message in (
                    "Hello from DevOps!", "CI/CD Pipeline Working Successfully!"
                )):
                    raise ValueError("The home page is missing its expected messages")
            return health
        except HTTPError as error:
            reason = "HTTP " + str(error.code)
        except (URLError, TimeoutError, OSError, ValueError):
            reason = "Service not ready or release/content mismatch"
        remaining = deadline - time.monotonic()
        if remaining > 0:
            time.sleep(min(interval, remaining))
    raise RuntimeError(f"Release verification timed out: {reason}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--expected", required=True)
    parser.add_argument("--timeout", type=float, default=120)
    parser.add_argument("--interval", type=float, default=3)
    args = parser.parse_args()
    try:
        result = verify(args.url, args.expected, args.timeout, args.interval)
    except (RuntimeError, ValueError) as error:
        raise SystemExit(str(error))
    print("Verified expected release:", result["version"])


if __name__ == "__main__":
    main()
