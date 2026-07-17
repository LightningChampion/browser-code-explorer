import pytest

from explorer.navigator import GitHubNavigator, RepositoryTree


class FakeLink:
    def __init__(self, name: str, href: str):
        self.name = name
        self.href = href

    async def inner_text(self) -> str:
        return self.name

    async def get_attribute(self, attribute: str) -> str | None:
        if attribute == "href":
            return self.href
        return None


class FakeRows:
    def __init__(self, entries: list[tuple[str, str]]):
        self.links = [FakeLink(name, href) for name, href in entries]

    async def count(self) -> int:
        return len(self.links)

    def nth(self, index: int) -> FakeLink:
        return self.links[index]


class FakePage:
    def __init__(self, entries: list[tuple[str, str]]):
        self.entries = entries

    def locator(self, selector: str) -> FakeRows:
        return FakeRows(self.entries)


@pytest.mark.anyio
async def test_walk_discovers_more_than_fifty_files(monkeypatch):
    entries = [
        (
            f"file_{index}.py",
            f"https://github.com/example/project/blob/main/file_{index}.py",
        )
        for index in range(60)
    ]

    navigator = GitHubNavigator(FakePage(entries))

    async def successful_goto(url: str) -> bool:
        return True

    monkeypatch.setattr(navigator, "_safe_goto", successful_goto)

    tree = RepositoryTree()
    await navigator._walk(
        "https://github.com/example/project",
        "",
        0,
        tree,
    )

    assert len(tree.files) == 60
