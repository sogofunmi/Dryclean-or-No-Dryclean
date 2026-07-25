from camoufox.async_api import AsyncCamoufox
from scrapy_playwright.handler import Config

class CamoufoxProvider:
    def __init__(self, config: Config) -> None:
        self.config = config

    async def launch_browser(self, playwright):
        # This correctly intercepts Playwright and forces it to use Camoufox
        return await AsyncCamoufox(playwright).launch(headless=True)