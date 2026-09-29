"""Register a separate tenant for Lucio or Ember, using the admin key."""
import os
import sys
import httpx

project_id = sys.argv[1] if len(sys.argv) > 1 else "lucio-dev"
url = os.getenv("NEXUS_URL", "http://localhost:8000")
admin = os.environ["NEXUS_ADMIN_TOKEN"]
with httpx.Client(base_url=url, timeout=15) as client:
    r = client.post("/v1/projects", headers={"Authorization": f"Bearer {admin}"}, json={
        "project_id": project_id,
        "display_name": project_id,
        "agents": ["general", "builder", "research"],
        "allowed_tools": ["calculator", "utc_now"],
        "provider": "demo",
    })
    r.raise_for_status()
    print("Store this API key securely; NEXUS only shows it once:", r.json()["api_key"])
