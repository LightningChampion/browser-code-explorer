import asyncio

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
            url = f"{repository_url}/blob/{branch}/{path}"

            try:
                await self.page.goto(
                    url,
                    wait_until="domcontentloaded",
                    timeout=30000,
                )
            except PlaywrightError:
                continue

            if "404" in await self.page.title():
                continue

            raw_link = self.page.locator(
                'a[data-testid="raw-button"], '
                'a[href*="/raw/"], '
                'a:has-text("Raw")'
            ).first

            if await raw_link.count():
                try:
                    await raw_link.click()
                    await self.page.wait_for_load_state("domcontentloaded")

                    content = await self.page.locator("body").inner_text()
                    if content.strip():
                        return content.strip()
                except PlaywrightError:
                    pass

            selectors = [
                'textarea[aria-label="file content"]',
                'div[data-testid="read-only-cursor-text-area"]',
                'table.highlight',
                '.react-code-lines',
            ]

            for selector in selectors:
                locator = self.page.locator(selector).first
                if await locator.count():
                    content = await locator.inner_text()
                    if content.strip():
                        return content.strip()

            await asyncio.sleep(1)

        return ""
