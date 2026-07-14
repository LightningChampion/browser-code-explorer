import asyncio
from dataclasses import dataclass, field
from urllib.parse import urljoin

from playwright.async_api import Error as PlaywrightError
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
        await self._walk(repository_url, "", 0, tree)
        tree.files.sort(key=self._priority)
        return tree

    async def _safe_goto(self, url: str) -> bool:
        for attempt in range(3):
            try:
                await self.page.goto(
                    url,
                    wait_until="domcontentloaded",
                    timeout=settings.timeout_ms,
                )
                return True
            except PlaywrightError as exc:
                print(f"Retry {attempt + 1}/3: {url}")
                if attempt == 2:
                    print(f"Skipped: {url} ({exc})")
                    return False
                await asyncio.sleep(2)

        return False

    async def _walk(
        self,
        url: str,
        current_path: str,
        depth: int,
        tree: RepositoryTree,
    ) -> None:
        if depth > settings.max_depth:
            return

        if len(tree.files) >= settings.max_files:
            return

        if url in self.visited_urls:
            return

        self.visited_urls.add(url)

        if not await self._safe_goto(url):
            return

        rows = self.page.locator(
            'a.Link--primary[href*="/tree/"], '
            'a.Link--primary[href*="/blob/"]'
        )

        entries: list[tuple[str, str]] = []

        for index in range(await rows.count()):
            link = rows.nth(index)

            try:
                name = (await link.inner_text()).strip()
                href = await link.get_attribute("href")
            except PlaywrightError:
                continue

            if name and href:
                entries.append((name, urljoin("https://github.com", href)))

        for name, entry_url in entries:
            if len(tree.files) >= settings.max_files:
                return

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

    def _priority(self, path: str) -> tuple[int, str]:
        lower = path.lower()

        if lower.startswith("src/"):
            return (0, path)

        if any(
            name in lower
            for name in (
                "main.py",
                "app.py",
                "cli.py",
                "config.py",
                "__init__.py",
            )
        ):
            return (1, path)

        if lower.startswith("tests/"):
            return (3, path)

        if lower.startswith("examples/"):
            return (4, path)

        if lower.startswith("docs/"):
            return (5, path)

        return (2, path)
