from playwright.async_api import async_playwright

from explorer.config import settings


class BrowserController:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None

    async def start(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=settings.headless
        )
        context = await self.browser.new_context(
            viewport={"width": 1440, "height": 1000}
        )
        context.set_default_timeout(settings.timeout_ms)
        self.page = await context.new_page()
        return self.page

    async def stop(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
