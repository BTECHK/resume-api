import base64
import json
import os

import functions_framework
from googleapiclient import discovery

PROJECT_ID = os.environ["TARGET_PROJECT_ID"]
PROJECT_NAME = f"projects/{PROJECT_ID}"


@functions_framework.cloud_event
def stop_billing(cloud_event):
    raw = cloud_event.data["message"]["data"]
    payload = json.loads(base64.b64decode(raw).decode("utf-8"))

    cost = float(payload.get("costAmount", 0))
    budget = float(payload.get("budgetAmount", 0))
    name = payload.get("budgetDisplayName", "unknown")
    print(f"[{name}] cost=${cost:.2f} budget=${budget:.2f}")

    if cost < budget:
        print("Under budget — no action.")
        return

    billing = discovery.build("cloudbilling", "v1", cache_discovery=False)
    projects = billing.projects()

    info = projects.getBillingInfo(name=PROJECT_NAME).execute()
    if not info.get("billingEnabled", False):
        print(f"Billing already disabled on {PROJECT_NAME}.")
        return

    projects.updateBillingInfo(
        name=PROJECT_NAME,
        body={"billingAccountName": ""},
    ).execute()
    print(f"BILLING DISABLED on {PROJECT_NAME}")
