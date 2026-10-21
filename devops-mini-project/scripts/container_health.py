import json
import os
import sys
from urllib.request import urlopen
try:
    with urlopen("http://127.0.0.1:" + os.getenv("PORT", "10000") + "/health", timeout=3) as response:
        data = json.load(response)
        good = response.status == 200 and data.get("status") == "ok"
    sys.exit(0 if good else 1)
except Exception:
    sys.exit(1)
