#!/usr/bin/env bash
set -euo pipefail

command -v python3 >/dev/null 2>&1 || { echo "Python 3.11+ is required." >&2; exit 1; }

if [ ! -d .venv ]; then
  python3 -m venv .venv
fi

.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e '.[dev]'

echo "NEXUS Agentic OS installed."
echo "Run: .venv/bin/nexus-portable doctor"
echo "API-free local example: .venv/bin/nexus-portable ask --provider ollama --model llama3.2 'Hello from NEXUS'"
