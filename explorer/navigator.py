from dataclasses import dataclass, field
from urllib.parse import urljoin

from playwright.async_api import Page

from explorer.config import settings


IGNORED = {
    ".git",
    ".github",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    "dist",
    "build",
    "coverage",
    "target",
}

SOURCE_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx",
    ".go", ".rs", ".java", ".kt", ".md",
    ".toml", ".json", ".yaml", ".yml",
}


@dataclass
class RepositoryTree:
    folders: list[str] = field(default_factory=list)
    files: list[str] = field(default_factory=list)


class GitHubNavigator:
    def __init__(self, page: Page):
        self.page = page
        self.visited_urls: set[str] = set()

    async def explore(self, repository_url: str) -> RepositoryTree:
        tree = RepositoryTree()
        await self.page.goto(repository_url, wait_until="domcontentloaded")
        await self._walk(repository_url, "", 0, tree)
        return tree

    async def _walk(
        self,
        url: str,
        current_path: str,
        depth: int,
        tree: RepositoryTree,
    ):
        if depth > settings.max_depth:
            return

        if url in self.visited_urls:
            return

        self.visited_urls.add(url)
        await self.page.goto(url, wait_until="domcontentloaded")

        rows = self.page.locator(
            'a.Link--primary[href*="/tree/"], '
            'a.Link--primary[href*="/blob/"]'
        )

        entries = []

        for index in range(await rows.count()):
            link = rows.nth(index)
            name = (await link.inner_text()).strip()
            href = await link.get_attribute("href")

            if not name or not href:
                continue

            entries.append((name, urljoin("https://github.com", href)))

        for name, entry_url in entries:
            path = f"{current_path}/{name}".strip("/")

            if "/tree/" in entry_url:
                if name in IGNORED:
                    continue

                if path not in tree.folders:
                    tree.folders.append(path)

                await self._walk(entry_url, path, depth + 1, tree)

            elif "/blob/" in entry_url:
                suffix = "." + name.rsplit(".", 1)[-1] if "." in name else ""

                if suffix in SOURCE_EXTENSIONS or name in {
                    "Dockerfile",
                    "Makefile",
                    "LICENSE",
                }:
                    if path not in tree.files:
                        tree.files.append(path)

                if len(tree.files) >= settings.max_files:
                    return
