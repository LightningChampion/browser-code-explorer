import re

from playwright.async_api import Page


class RepositoryOverview:
    def __init__(self, page: Page):
        self.page = page

    async def collect(self, repository_url: str) -> dict:
        await self.page.goto(repository_url, wait_until="domcontentloaded")

        description = await self._description()
        readme = await self._readme()
        purpose = self._purpose(readme, description)

        return {
            "description": description,
            "purpose": purpose,
            "readme_excerpt": readme[:3000],
        }

    async def _description(self) -> str:
        meta = self.page.locator('meta[name="description"]')

        if await meta.count():
            return (await meta.get_attribute("content") or "").strip()

        return ""

    async def _readme(self) -> str:
        article = self.page.locator("article.markdown-body").first

        if await article.count():
            return (await article.inner_text()).strip()

        return ""

    def _purpose(self, readme: str, description: str) -> str:
        paragraphs = re.split(r"\n\s*\n", readme)

        for paragraph in paragraphs:
            clean = " ".join(paragraph.split())

            if clean.startswith("#"):
                continue

            if 60 <= len(clean) <= 1200:
                return clean

        return description or "Repository purpose could not be determined."
