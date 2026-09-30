$ErrorActionPreference = "Stop"

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
  throw "Python 3.11+ is required and was not found on PATH."
}

if (-not (Test-Path ".venv")) {
  python -m venv .venv
}

& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -e ".[dev]"

Write-Host "Nexus Starship Guardians installed."
Write-Host "Run: .\.venv\Scripts\nexus-guardians.exe doctor"
Write-Host "API-free local example: .\.venv\Scripts\nexus-guardians.exe ask --provider ollama --model llama3.2 'Hello from Nexus Starship Guardians'"
