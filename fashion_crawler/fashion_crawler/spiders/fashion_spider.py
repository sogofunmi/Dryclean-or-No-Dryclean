import scrapy
from fashion_crawler.items import FashionCrawlerItem
from urllib.parse import urljoin
import asyncio


class FashionSpider(scrapy.Spider):
    name = "fashion"
    
    allowed_domains = ["modaoperandi.com"]

    custom_settings = {
        "CONCURRENT_REQUESTS": 8,
        "PLAYWRIGHT_MAX_PAGES_PER_CONTEXT": 20, 
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 30000,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.seen_links = set()

    async def start(self):
        yield scrapy.Request(
            url="https://www.modaoperandi.com/women/products/clothing",
            meta={
                "playwright": True,
                "playwright_include_page": True},
            callback=self.parse)

    async def parse(self, response):
        page = response.meta["playwright_page"]
        main_url = "https://www.modaoperandi.com/"

        try:
            
            current_position = 0
            
            while True:
                current_position += 1000
                await page.evaluate(f"window.scrollTo(0, {current_position});")
                await asyncio.sleep(2) 
                

                total_height = await page.evaluate("document.body.scrollHeight")
                if current_position >= total_height:
                    break

            scrolled_page = await page.content()
            scrolled = response.replace(body=scrolled_page.encode("utf-8"))

            
            products = scrolled.css("div.VariantCell")


            for product in products:
                item = FashionCrawlerItem() 
                link = product.css('a::attr(href)').get()
                if link:
                    link = urljoin(main_url, link)
                    if link in self.seen_links:
                        continue
                    self.seen_links.add(link)

                    title = product.css('a::attr(aria-label)').get()
                    if not title:
                        title = product.css('::text').get()
                    
                    if title and link and 'modaoperandi.com' in link:
                        item['title'] = title.strip()
                        item['link'] = link
                        yield scrapy.Request(link, callback=self.parse_product, meta={'item': item})

            
            next_button = page.locator("button.Paginator__button--next")
            has_next = not (await next_button.is_disabled())
            
            if has_next:
        
                await next_button.click()
                await page.wait_for_load_state("networkidle", timeout=30000)

                
                webpage = await page.content()
                new_response = response.replace(body=webpage.encode("utf-8"))
                
                async for result in self.parse(new_response):
                    yield result
            else:
                self.logger.info("All webpages visited.")
                await page.close()

        except Exception as e:
            self.logger.error(f"Error encountered during dynamic parser looping: {str(e)}")
            await page.close()
         

    async def parse_product(self, response):
        page = response.meta.get("playwright_page")
        item = response.meta["item"]

        price = response.css("div.ProductDetails span.PDPProductPrice__current-price::text").get()
        details = response.css("div.ProductDetails div.Expandable__contents div ul li p::text").getall()
        if not details:
            details = response.css("div.ProductDetails div.Expandable__contents div ul li::text").getall()
        composition = response.xpath('//li/p[contains(text(), "Composition")]/text()').getall()
        if not composition:
            composition = response.xpath('//li[contains(text(), "Composition")]/text()').getall()
            

        if price:
            item["price"] = price.strip()
        if composition:
            item["composition"] = composition
        if details:
            item["details"] = details

        if page:
            await page.close()  

        yield item



