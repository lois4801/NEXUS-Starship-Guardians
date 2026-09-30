#!/usr/bin/env bash
set -euo pipefail

command -v python3 >/dev/null 2>&1 || { echo "Python 3.11+ is required." >&2; exit 1; }

if [ ! -d .venv ]; then
  python3 -m venv .venv
fi

.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e '.[dev]'

echo "Nexus Starship Guardians installed."
echo "Run: .venv/bin/nexus-guardians doctor"
echo "API-free local example: .venv/bin/nexus-guardians ask --provider ollama --model llama3.2 'Hello from Nexus Starship Guardians'"
