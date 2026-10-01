"""Small opt-in Nexus Starship Guardians REST v1 client.

Python 3.11+, standard library only. This is not an MCP server.
Environment: NEXUS_URL, NEXUS_PROJECT_KEY.
No project registration, shell execution, deployment, or automatic approvals.
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
_GUARDIANS = ("general", "builder", "research")


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _base_url() -> str:
    raw = os.getenv("NEXUS_URL", "").strip().rstrip("/")
    if not raw:
        raise ValueError("NEXUS_URL must be set to your authorized Nexus instance")
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
                raise ValueError("Nexus response exceeded 2 MiB")
            return json.loads(content.decode("utf-8"))
    except urllib.error.HTTPError as exc:
        # Never print the server body: traces may contain sensitive data.
        raise ValueError(f"Nexus returned HTTP {exc.code}") from None
    except urllib.error.URLError:
        raise ValueError("Nexus endpoint is unavailable or TLS verification failed") from None


def safe_view(data: dict, full: bool = False) -> dict:
    if full:
        # Caller must have authorized disclosure of run goal/events.
        return data
    result = {
        key: data[key]
        for key in ("status", "run_id", "project_id", "answer", "steps_used")
        if key in data
    }
    # REST v1 wire compatibility keeps `agent`; product-facing output says Guardian.
    if "agent" in data:
        result["guardian"] = data["agent"]
    if isinstance(data.get("pending_approval"), dict):
        result["pending_approval"] = {"tool": data["pending_approval"].get("tool")}
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Operate an authorized Nexus Starship Guardians project")
    subs = parser.add_subparsers(dest="command", required=True)
    subs.add_parser("health", help="Check API health without credentials")

    run = subs.add_parser("run", help="Start a project-scoped Guardian run")
    run.add_argument("--project", required=True)
    guardian = run.add_mutually_exclusive_group()
    guardian.add_argument("--guardian", dest="guardian", choices=_GUARDIANS, default="general")
    guardian.add_argument(
        "--agent",
        dest="guardian",
        choices=_GUARDIANS,
        help="Legacy compatibility alias for --guardian",
    )
    goal = run.add_mutually_exclusive_group(required=True)
    goal.add_argument("--goal", help="For nonsensitive goals only (visible in shell process list)")
    goal.add_argument("--goal-stdin", action="store_true", help="Read goal text from standard input")
    run.add_argument("--full", action="store_true", help="Print private full events after authorization")

    inspect = subs.add_parser("inspect", help="Inspect an existing run")
    inspect.add_argument("--run-id", required=True)
    inspect.add_argument("--full", action="store_true", help="Print private goal and events")

    approve = subs.add_parser("approve", help="Explicit approval/denial; never run automatically")
    approve.add_argument("--run-id", required=True)
    approve.add_argument("--decision", choices=("yes", "no"), required=True)

    args = parser.parse_args(argv)
    try:
        if args.command == "health":
            result = request("GET", "/health", auth=False)
        elif args.command == "run":
            if not re.fullmatch(r"[a-z][a-z0-9-]{2,47}", args.project):
                raise ValueError("Invalid project ID")
            user_goal = sys.stdin.read() if args.goal_stdin else args.goal
            if not (1 <= len(user_goal) <= 4000):
                raise ValueError("Goal must contain 1-4000 characters")
            result = safe_view(
                request(
                    "POST",
                    f"/v1/projects/{args.project}/runs",
                    # REST v1 retains `agent` as a compatibility wire field.
                    {"goal": user_goal, "agent": args.guardian},
                ),
                args.full,
            )
        else:
            if not re.fullmatch(r"[A-Za-z0-9_-]{8,80}", args.run_id):
                raise ValueError("Invalid run ID")
            if args.command == "inspect":
                result = safe_view(request("GET", f"/v1/runs/{args.run_id}"), args.full)
            else:
                result = safe_view(
                    request(
                        "POST",
                        f"/v1/runs/{args.run_id}/approval",
                        {"approved": args.decision == "yes"},
                    )
                )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
