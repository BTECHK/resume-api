#!/usr/bin/env python3
"""Smoke test: POST /chat returns a contextual response (INT-02).

Sends a 2-message history and verifies the endpoint preserves the
message_count and returns a non-empty answer.
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

    endpoint = f"{url.rstrip('/')}/chat"
    payload = json.dumps({
        "messages": [
            {"role": "user", "content": "What is the candidate's experience level?"},
            {"role": "assistant", "content": "The candidate has 8+ years of consulting experience."},
            {"role": "user", "content": "What about technical skills?"},
        ],
    }).encode("utf-8")
    req = urllib.request.Request(
        endpoint,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as response:
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

    if body.get("message_count") != 3:
        print(f"FAIL: expected message_count=3, got {body.get('message_count')}")
        return 1

    if not body.get("answer"):
        print(f"FAIL: empty answer: {body}")
        return 1

    print(f"PASS: /chat returned {len(body['sources'])} sources, message_count={body['message_count']}")
    print(f"      answer preview: {body['answer'][:120]}...")
    return 0


if __name__ == "__main__":
    sys.exit(main())
