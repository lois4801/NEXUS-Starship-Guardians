# Portable LLM Runtime

NEXUS Agentic OS can route prompts through local models and user-operated coding/chat CLIs without requiring a paid model API in the NEXUS core.

## What "no API needed" means

- **Local models:** fully API-key-free when invoked through a local executable such as Ollama.
- **Desktop/coding CLIs:** NEXUS can invoke a CLI already installed and authenticated on your laptop. The external tool may still require its own account, subscription, login, or license.
- **Hosted chat models:** a provider cannot be bypassed. If a hosted model only exposes authenticated web/API access, NEXUS must use the provider's supported authentication path.

NEXUS never embeds or shares provider credentials between projects.

## Windows quick start

```powershell
git clone https://github.com/lois4801/NEXUS-Agentic-OS.git
cd NEXUS-Agentic-OS
powershell -ExecutionPolicy Bypass -File .\install.ps1
.\.venv\Scripts\nexus-portable.exe doctor
```

Install Ollama and a local model, then:

```powershell
ollama pull llama3.2
.\.venv\Scripts\nexus-portable.exe ask --provider ollama --model llama3.2 "Plan a FastAPI feature"
```

## macOS/Linux quick start

```bash
git clone https://github.com/lois4801/NEXUS-Agentic-OS.git
cd NEXUS-Agentic-OS
bash ./install.sh
.venv/bin/nexus-portable doctor
```

## Bridge an existing coding/chat CLI

The `cli` provider deliberately does not invoke a shell. Configure an exact JSON command array and let that external program handle its own authentication.

PowerShell example:

```powershell
$env:NEXUS_LLM_COMMAND='["claude","-p"]'
.\.venv\Scripts\nexus-portable.exe ask --provider cli --model claude "Review this architecture"
```

Codex-style stdin example:

```powershell
$env:NEXUS_LLM_COMMAND='["codex","exec","-"]'
.\.venv\Scripts\nexus-portable.exe ask --provider cli --model codex "Explain the repository"
```

Exact CLI flags can change between tool versions. Run the target tool's own help command before configuring it.

## Adapter contract

Every portable provider implements:

```python
class PortableProvider(Protocol):
    name: str
    def generate(self, prompt: str) -> ProviderResult: ...
```

This keeps Lucio AI Platform, Ember, ChatGPT plugin packaging, future apps, and local automation independent from any one model vendor.

Recommended future adapters:

- llama.cpp local executable
- LM Studio local server
- MLX local models on Apple Silicon
- vLLM local/self-hosted server
- authenticated Claude/Gemini/Codex CLIs
- MCP-backed model/tool gateways
- provider APIs as optional adapters, never as a requirement for the core runtime

## Security

- Never pass arbitrary shell strings from a model into the CLI adapter.
- Keep command configuration under user/admin control.
- Keep project credentials server-side.
- Require explicit approval before repository writes, deployment, destructive commands, external messages, or other consequential actions.
- Treat local model output as untrusted input and validate tool proposals before execution.
