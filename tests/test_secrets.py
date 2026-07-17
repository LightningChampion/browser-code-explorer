from types import SimpleNamespace

import pytest

from explorer import secrets


def test_returns_key_from_keychain(monkeypatch):
    def fake_run(*args, **kwargs):
        return SimpleNamespace(returncode=0, stdout="test-key\n")

    monkeypatch.setattr(secrets.subprocess, "run", fake_run)

    assert secrets.get_openai_api_key() == "test-key"


def test_raises_when_keychain_lookup_fails(monkeypatch):
    def fake_run(*args, **kwargs):
        return SimpleNamespace(returncode=44, stdout="")

    monkeypatch.setattr(secrets.subprocess, "run", fake_run)

    with pytest.raises(RuntimeError):
        secrets.get_openai_api_key()
