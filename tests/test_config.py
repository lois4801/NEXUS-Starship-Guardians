import pytest

from nexus_os.config import Settings


def test_secrets_required_outside_dev(monkeypatch):
    monkeypatch.delenv("NEXUS_ADMIN_TOKEN", raising=False)
    monkeypatch.delenv("NEXUS_DEV_MODE", raising=False)
    with pytest.raises(RuntimeError):
        Settings.from_env()


def test_insecure_remote_model_endpoint_rejected(monkeypatch):
    monkeypatch.setenv("NEXUS_ADMIN_TOKEN", "test")
    monkeypatch.setenv("NEXUS_MODEL_BASE_URL", "http://example.com/v1")
    with pytest.raises(RuntimeError):
        Settings.from_env()


def test_adaptive_intelligence_path_can_be_configured(monkeypatch, tmp_path):
    adaptive_path = tmp_path / "specialist-intelligence.json"
    monkeypatch.setenv("NEXUS_ADMIN_TOKEN", "test")
    monkeypatch.setenv("NEXUS_MODEL_BASE_URL", "http://localhost:11434/v1")
    monkeypatch.setenv("NEXUS_ADAPTIVE_INTELLIGENCE_PATH", str(adaptive_path))

    settings = Settings.from_env()
    assert settings.adaptive_intelligence_path == str(adaptive_path)
