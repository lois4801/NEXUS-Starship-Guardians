"""Small opt-in NEXUS v0.1 REST client. Python 3.11+, standard library only.

This is not an MCP server. Environment: NEXUS_URL, NEXUS_PROJECT_KEY.
No project registration, shell execution, or automatic approvals.
"""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from urllib.parse import urlsplit

_MAX_BODY = 2 * 1024 * 1024

class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

def _base_url() -> str:
    raw = os.getenv("NEXUS_URL", "").strip().rstrip("/")
    if not raw:
        raise ValueError("NEXUS_URL must be set to your authorized NEXUS instance")
    parsed = urlsplit(raw)
    if parsed.username or parsed.password or not parsed.hostname or parsed.query or parsed.fragment:
        raise ValueError("NEXUS_URL must be a clean HTTPS origin or explicit loopback HTTP URL")
    is_local = parsed.hostname in {"localhost", "127.0.0.1", "::1"}
    if parsed.scheme != "https" and not (parsed.scheme == "http" and is_local):
        raise ValueError("NEXUS_URL must use HTTPS except for localhost/loopback")
    return raw

def request(method: str, path: str, payload: dict | None = None, auth: bool = True) -> dict:
    base = _base_url()
    key = os.getenv("NEXUS_PROJECT_KEY", "")
    if auth and not key:
        raise ValueError("Set NEXUS_PROJECT_KEY in the secure host environment")
    headers = {"Accept": "application/json"}
    if auth:
        headers["Authorization"] = "Bearer " + key
    body = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(base + path, data=body, headers=headers, method=method)
    opener = urllib.request.build_opener(_NoRedirect)
    try:
        with opener.open(req, timeout=20) as response:
            content = response.read(_MAX_BODY + 1)
            if len(content) > _MAX_BODY:
                raise ValueError("NEXUS response exceeded 2 MiB")
            return json.loads(content.decode("utf-8"))
    except urllib.error.HTTPError as exc:
        # Never print server response body: error traces could contain sensitive data.
        raise ValueError(f"NEXUS returned HTTP {exc.code}") from None
    except urllib.error.URLError:
        raise ValueError("NEXUS endpoint is unavailable or TLS verification failed") from None

def safe_view(data: dict, full: bool = False) -> dict:
    if full:
        # Caller must have authorized disclosure of run goal/events.
        return data
    return {k: data[k] for k in ("status","run_id","project_id","agent","answer","steps_used")
            if k in data} | ({"pending_approval": {"tool": data["pending_approval"].get("tool")}}
                            if isinstance(data.get("pending_approval"), dict) else {})

def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Operate an authorized NEXUS v0.1 project")
    subs = p.add_subparsers(dest="command", required=True)
    subs.add_parser("health", help="Check API health without credentials")
    run = subs.add_parser("run", help="Start a project-scoped run")
    run.add_argument("--project", required=True)
    run.add_argument("--agent", default="general", choices=("general","builder","research"))
    goal = run.add_mutually_exclusive_group(required=True)
    goal.add_argument("--goal", help="For nonsensitive goals only (visible in shell process list)")
    goal.add_argument("--goal-stdin", action="store_true", help="Read goal text from standard input")
    run.add_argument("--full", action="store_true", help="Print private full events after authorization")
    inspect = subs.add_parser("inspect", help="Inspect an existing run")
    inspect.add_argument("--run-id", required=True)
    inspect.add_argument("--full", action="store_true", help="Print private goal and events")
    approve = subs.add_parser("approve", help="Explicit approval/denial; never run automatically")
    approve.add_argument("--run-id", required=True)
    approve.add_argument("--decision", choices=("yes","no"), required=True)
    args = p.parse_args(argv)
    try:
        if args.command == "health":
            result = request("GET","/health", auth=False)
        elif args.command == "run":
            if not re.fullmatch(r"[a-z][a-z0-9-]{2,47}", args.project):
                raise ValueError("Invalid project ID")
            user_goal = sys.stdin.read() if args.goal_stdin else args.goal
            if not (1 <= len(user_goal) <= 4000):
                raise ValueError("Goal must contain 1-4000 characters")
            result = safe_view(request(
                "POST",f"/v1/projects/{args.project}/runs",
                {"goal":user_goal,"agent":args.agent}),args.full)
        else:
            if not re.fullmatch(r"[A-Za-z0-9_-]{8,80}", args.run_id):
                raise ValueError("Invalid run ID")
            if args.command == "inspect":
                result = safe_view(request("GET",f"/v1/runs/{args.run_id}"),args.full)
            else:
                result = safe_view(request("POST",f"/v1/runs/{args.run_id}/approval",
                                           {"approved": args.decision == "yes"}))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

if __name__ == "__main__":
    sys.exit(main())
