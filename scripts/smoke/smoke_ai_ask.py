#!/usr/bin/env python3
"""Smoke test: POST /ai/ask returns a grounded answer (INT-02 + INT-03).

Usage:
    AI_SERVICE_URL=https://ai-service-xyz.run.app python scripts/smoke/smoke_ai_ask.py

Exit codes:
    0 — PASS: endpoint responded 200 with expected shape
    1 — FAIL: unexpected status, shape, or connection error
    2 — RUN-DEFERRED: AI_SERVICE_URL not set
"""

import json
import os
import sys
import urllib.error
import urllib.request


def main() -> int:
    url = os.getenv("AI_SERVICE_URL")
    if not url:
        print("RUN-DEFERRED: set AI_SERVICE_URL to run this smoke test")
        return 2

    endpoint = f"{url.rstrip('/')}/ai/ask"
    payload = json.dumps({"question": "What certifications does the candidate have?"}).encode("utf-8")
    req = urllib.request.Request(
        endpoint,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            status = response.status
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        print(f"FAIL: HTTP {exc.code} from {endpoint}: {exc.read().decode('utf-8', errors='replace')}")
        return 1
    except Exception as exc:
        print(f"FAIL: {type(exc).__name__} contacting {endpoint}: {exc}")
        return 1

    if status != 200:
        print(f"FAIL: expected 200, got {status}")
        return 1

    required_keys = {"answer", "sources", "model_used"}
    missing = required_keys - set(body.keys())
    if missing:
        print(f"FAIL: response missing keys: {missing}")
        return 1

    if not body["answer"] or not isinstance(body["sources"], list):
        print(f"FAIL: empty answer or malformed sources: {body}")
        return 1

    print(f"PASS: /ai/ask returned {len(body['sources'])} sources, model={body['model_used']}")
    print(f"      answer preview: {body['answer'][:120]}...")
    return 0


if __name__ == "__main__":
    sys.exit(main())
