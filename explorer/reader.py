from urllib.parse import urljoin

from playwright.async_api import Page, Error as PlaywrightError


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

        for path in paths[:self.max_files]:
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
