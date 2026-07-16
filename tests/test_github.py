import pytest

from explorer.github import normalize_repository


def test_normalizes_short_repository_name():
    assert (
        normalize_repository("pallets/flask")
        == "https://github.com/pallets/flask"
    )


def test_keeps_full_github_url():
    assert (
        normalize_repository("https://github.com/pallets/flask")
        == "https://github.com/pallets/flask"
    )


def test_rejects_invalid_repository():
    with pytest.raises(ValueError):
        normalize_repository("invalid-repository")