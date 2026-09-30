import pytest

from nexus_os.portable.registry import build_provider, list_providers


def test_provider_list_is_stable():
    assert list_providers() == ["ollama", "cli"]


def test_ollama_requires_model():
    with pytest.raises(RuntimeError, match="--model is required"):
        build_provider("ollama")


def test_unknown_provider_rejected():
    with pytest.raises(RuntimeError, match="Unknown portable provider"):
        build_provider("unknown")
