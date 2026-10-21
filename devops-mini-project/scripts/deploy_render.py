"""Request an exact Docker digest, then verify the public service. No secrets logged."""
import json
import os
from pathlib import Path
import re
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from scripts.verify_release import verify


def build_hook_url(hook, image):
    parts = urlsplit(hook)
    if (parts.scheme != "https" or parts.hostname != "api.render.com"
            or not parts.path.startswith("/deploy/") or parts.username or parts.password):
        raise ValueError("Use the complete HTTPS deploy hook copied from Render Settings.")
    if not re.fullmatch(r"docker\.io/[a-z0-9_-]+/[a-z0-9_.-]+@sha256:[0-9a-f]{64}", image):
        raise ValueError("IMAGE_REF must be a Docker Hub repository with a sha256 digest.")
    query = [(key, value) for key, value in parse_qsl(parts.query) if key != "imgURL"]
    if not any(key == "key" and value for key, value in query):
        raise ValueError("The Render deploy hook is missing its secret key.")
    query.append(("imgURL", image))
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), ""))


def main():
    values = {name: os.getenv(name, "").strip() for name in (
        "RENDER_DEPLOY_HOOK", "RENDER_SERVICE_URL", "IMAGE_REF", "EXPECTED_VERSION"
    )}
    missing = [name for name, value in values.items() if not value]
    if missing:
        raise SystemExit("Missing configuration: " + ", ".join(missing))
    try:
        target = build_hook_url(values["RENDER_DEPLOY_HOOK"], values["IMAGE_REF"])
        with urlopen(Request(target, data=b"", method="POST"), timeout=30) as response:
            if response.status not in (200, 202):
                raise RuntimeError("Unexpected deploy response")
        print("Render accepted the request. Waiting for the exact release...")
        health = verify(values["RENDER_SERVICE_URL"], values["EXPECTED_VERSION"], timeout=600, interval=5)
    except HTTPError as error:
        raise SystemExit(f"Render request failed (HTTP {error.code}). Check service configuration and hook.")
    except (URLError, TimeoutError, OSError):
        raise SystemExit("Network failure. A deploy may already be running; check Render before retrying.")
    except (ValueError, RuntimeError) as error:
        raise SystemExit(str(error))
    record = {"image": values["IMAGE_REF"], "version": health["version"],
              "service_url": values["RENDER_SERVICE_URL"], "verified": True,
              "verified_at_utc": health.get("time_utc")}
    Path("release.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print("Verified live release:", health["version"])


if __name__ == "__main__":
    main()
