import scrapy
from urllib.parse import urljoin
from farfetch_crawler.items import FarfetchCrawlerItem
from scrapy_playwright.page import PageMethod
from urllib.parse import urljoin, urlparse
import os
import asyncio

class FarfetchSpider(scrapy.Spider):
    name = "farfetch"
    allowed_domains = ["farfetch.com"]
    custom_settings = {
        "PLAYWRIGHT_MAX_PAGES_PER_CONTEXT": 20, 
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 50000,
        "CLOSESPIDER_ITEMCOUNT": 20000
    }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.seen_links = set()


    async def start(self):
        url = "https://www.farfetch.com/shopping/women/clothing-1/items.aspx"
        
        yield scrapy.Request(
            url=url,
            meta={
                "playwright": True,
                "playwright_include_page": True},
            callback=self.parse)

    async def parse(self, response):
        page = response.meta["playwright_page"]
        main_url = "https://www.farfetch.com/"
        
        try:
            current_position = 0

            while True:
                current_position += 2000
                await page.evaluate(f"window.scrollTo(0, {current_position});")
                await asyncio.sleep(2)

                total_height = await page.evaluate("document.body.scrollHeight")
                if current_position >= total_height:
                    break

            scrolled_page = await page.content()
            scrolled = response.replace(body=scrolled_page.encode("utf-8"))

            products = scrolled.css("li[data-testid='productCard']")
                
            for product in products:
                item = FarfetchCrawlerItem()
                link = product.css("a::attr(href)").get()
                if link:
                    link = urljoin(main_url, link)

                    if link in self.seen_links:
                        continue
                    self.seen_links.add(link)


                    if "farfetch.com" in link:
                        
                        item["link"] = link
                        
                        yield scrapy.Request(link, callback=self.parse_product, meta={"item": item})

            next_page = scrolled.css("a[data-component='PaginationNextActionButton']::attr(href)").get()

            if next_page:

                next_page_url = urljoin(page.url, next_page)

                yield scrapy.Request(
                    url=next_page_url,
                    callback=self.parse,
                    meta={
                        "playwright": True,
                        "playwright_include_page": True
                    },
                )

            else:
                self.logger.info("All webpages visited")
                await page.close()
        except Exception as e:
            self.logger.error(f"Error encountered. Could not scroll page {str(e)}")
            await page.close()

    async def parse_product(self, response):
        page = response.meta.get("playwright_page")
        item = response.meta["item"]

        composition = response.xpath('//span[contains(text(), "%")]/text()').getall()
        care = response.xpath('//p[contains(text(), "Machine")]/text()').getall()
        title = response.css("div[data-component='Grid'] p[data-testid='product-short-description']::text").get()
        price = response.css("div[data-component='Grid'] p[data-component='PriceFinal']::text").get()

        if price:
            item["price"] = price.strip()
        if composition:
            item["composition"] = composition
        if care:
            item["care"] = care
        if title:
            item["title"] = title
        if page:
            await page.close()

        yield item

