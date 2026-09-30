from __future__ import annotations

import argparse
import json
import shutil
import sys

from .registry import build_provider, list_providers


def _doctor() -> int:
    checks = {
        "python": sys.executable,
        "ollama": shutil.which("ollama"),
        "claude": shutil.which("claude"),
        "codex": shutil.which("codex"),
        "gemini": shutil.which("gemini"),
    }
    print(json.dumps(checks, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="nexus-portable")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("providers", help="List built-in portable providers")
    sub.add_parser("doctor", help="Detect local model/coding CLIs")

    ask = sub.add_parser("ask", help="Send one prompt through a portable provider")
    ask.add_argument("--provider", required=True, choices=list_providers())
    ask.add_argument("--model")
    ask.add_argument("prompt", nargs="+")

    args = parser.parse_args()
    if args.command == "providers":
        print("\n".join(list_providers()))
        return 0
    if args.command == "doctor":
        return _doctor()
    if args.command == "ask":
        provider = build_provider(args.provider, args.model)
        result = provider.generate(" ".join(args.prompt))
        print(result.text)
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
