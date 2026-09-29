"""Environment-based server configuration; secrets are never stored in source control."""

from dataclasses import dataclass
import os
from urllib.parse import urlsplit


@dataclass(frozen=True)
class Settings:
    admin_token: str
    db_path: str
    model_base_url: str
    model_api_key: str
    model_name: str
    dev_mode: bool

    @classmethod
    def from_env(cls) -> "Settings":
        dev = os.getenv("NEXUS_DEV_MODE", "false").lower() == "true"
        token = os.getenv("NEXUS_ADMIN_TOKEN", "")
        if not token and not dev:
            raise RuntimeError("NEXUS_ADMIN_TOKEN must be set unless NEXUS_DEV_MODE=true")
        if dev and not token:
            token = "unsafe-local-demo-only"
        url = os.getenv("NEXUS_MODEL_BASE_URL", "http://localhost:11434/v1").rstrip("/")
        parsed = urlsplit(url)
        if parsed.scheme != "https" and not (
            parsed.scheme == "http" and parsed.hostname in {"localhost", "127.0.0.1", "::1", "host.docker.internal"}
        ):
            raise RuntimeError("Model endpoint must be HTTPS or an explicit local HTTP endpoint")
        if parsed.username or parsed.password or not parsed.hostname:
            raise RuntimeError("Invalid model endpoint")
        return cls(
            admin_token=token,
            db_path=os.getenv("NEXUS_DB_PATH", "./data/nexus.db"),
            model_base_url=url,
            model_api_key=os.getenv("NEXUS_MODEL_API_KEY", ""),
            model_name=os.getenv("NEXUS_MODEL_NAME", "llama3.2"),
            dev_mode=dev,
        )
