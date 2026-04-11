#!/usr/bin/env python3
"""Smoke test: email → n8n → ai-service → reply (INT-01).

This script triggers the n8n webhook that mirrors the real Gmail-poll
workflow. It does NOT send a real email — that path requires Gmail
OAuth in Production and is covered by the manual runbook in
.planning/phases/05-n8n-email-bot/05-02-PLAN.md.

Usage:
    N8N_WEBHOOK_URL=https://n8n.example.com/webhook/email-test \
    python scripts/smoke/smoke_email.py
"""

import json
import os
import sys
import urllib.error
import urllib.request


def main() -> int:
    url = os.getenv("N8N_WEBHOOK_URL")
    if not url:
        print("RUN-DEFERRED: set N8N_WEBHOOK_URL to run this smoke test")
        print("Note: this test requires n8n VM + Gmail OAuth production setup")
        print("See .planning/phases/05-n8n-email-bot/05-02-PLAN.md")
        return 2

    payload = json.dumps({
        "from": "smoke-test@example.com",
        "subject": "Tell me about the candidate",
        "body": "What certifications does the candidate have?",
    }).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            status = response.status
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        print(f"FAIL: HTTP {exc.code} from {url}: {exc.read().decode('utf-8', errors='replace')}")
        return 1
    except Exception as exc:
        print(f"FAIL: {type(exc).__name__} contacting {url}: {exc}")
        return 1

    if status not in (200, 202):
        print(f"FAIL: expected 200/202, got {status}")
        return 1

    print(f"PASS: n8n webhook accepted trigger (status={status})")
    print(f"      preview: {body[:200]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
