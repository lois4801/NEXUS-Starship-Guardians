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
