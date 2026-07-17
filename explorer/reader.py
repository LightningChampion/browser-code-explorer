from urllib.parse import urljoin

from playwright.async_api import Page, Error as PlaywrightError


def select_representative_files(
    paths: list[str],
    max_files: int,
) -> list[str]:
    priority_groups = [
        ("README.md", "README.rst", "README.txt"),
        (
            "pyproject.toml",
            "requirements.txt",
            "package.json",
            "Cargo.toml",
            "go.mod",
            "pom.xml",
        ),
        (".github/workflows/",),
        ("tests/", "test/"),
        ("docs/",),
    ]

    selected: list[str] = []

    for group in priority_groups:
        for path in paths:
            if path in selected:
                continue

            if any(
                path == pattern or path.startswith(pattern)
                for pattern in group
            ):
                selected.append(path)
                break

    for path in paths:
        if len(selected) >= max_files:
            break

        if path not in selected:
            selected.append(path)

    return selected[:max_files]


class CodeReader:
    def __init__(self, page: Page, max_files: int = 15):
        self.page = page
        self.max_files = max_files

    async def read_files(
        self,
        repository_url: str,
        paths: list[str],
    ) -> dict[str, str]:
        contents = {}
        selected_paths = select_representative_files(
            paths,
            self.max_files,
        )

        for path in selected_paths:
            content = await self.read_file(repository_url, path)

            if content:
                contents[path] = content
                print(f"Read: {path}")
            else:
                print(f"Could not read: {path}")

        return contents

    async def read_file(self, repository_url: str, path: str) -> str:
        for branch in ("main", "master"):
            file_url = f"{repository_url}/blob/{branch}/{path}"

            try:
                await self.page.goto(file_url, wait_until="domcontentloaded")
            except PlaywrightError:
                continue

            raw_link = self.page.locator(
                'a[data-testid="raw-button"], a[href*="/raw/"]'
            ).first

            if not await raw_link.count():
                continue

            raw_href = await raw_link.get_attribute("href")

            if not raw_href:
                continue

            raw_url = urljoin("https://github.com", raw_href)

            try:
                await self.page.goto(raw_url, wait_until="domcontentloaded")
                content = await self.page.locator("body").inner_text()
            except PlaywrightError:
                continue

            if content.strip():
                return content.strip()

        return ""
