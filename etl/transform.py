import boto3



class FashionSpider(scrapy.Spider):
    name = "fashion"
    
    allowed_domains = ["modaoperandi.com"]

        
    async def start(self):
        yield scrapy.Request(
            url="https://www.modaoperandi.com/women/products/clothing",
            meta={
                "playwright": True,
                "playwright_include_page": True,
                
            },
            callback=self.parse)

    async def parse(self, response):
        page = response.meta["playwright_page"]
        main_url = "https://www.modaoperandi.com/"
        
        
        products = response.css("div.VariantCell")
        seen_links = set()
        
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

            yield scrapy.Request(link, 
                                  callback=self.parse_product, 
                                  meta={
                                      'item': item
                                      })

        next_button = page.locator("button.Paginator__button--next")
        has_next = (await next_button.count() > 0) and not (await next_button.is_disabled())

        if has_next:
            await next_button.click()
            await page.wait_for_load_state("networkidle")

            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(3000)

            webpage = await page.content()
            new_response = response.replace(body=webpage.encode("utf-8"))

            # recurse into the same live page for the next round of clicks/scraping
            async for result in self.parse(new_response):
                yield result
        else:
            await page.close()
         

    def parse_product(self, response):
        item = response.meta['item']
        price = response.css("div.ProductDetails span.PDPProductPrice__current-price::text").get()
        details = response.css("div.ProductDetails div.Expandable__contents div ul li::text").getall()
        
        composition = response.xpath('//li[contains(text(), "Composition")]/text()').getall()

        if price:
            item['price'] = price.strip()
        if composition:
            item['composition'] = composition
        if details:
            item['details'] = details
        
        yield item


class FashionSpider(scrapy.Spider):
    name = "fashion"
    
    allowed_domains = ["modaoperandi.com"]

    custom_settings = {
        "CONCURRENT_REQUESTS": 8,
        "PLAYWRIGHT_MAX_PAGES_PER_CONTEXT": 20,  # give enough headroom for listing + product pages
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 30000,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # FIX 1: Track seen links at the class level so it spans across pages
        self.seen_links = set()

    async def start(self):
        yield scrapy.Request(
            url="https://www.modaoperandi.com/women/products/clothing",
            meta={
                "playwright": True,
                "playwright_include_page": True,
                "playwright_page_methods": [
                    # 1. Scroll to the bottom of the page
                    PageMethod("evaluate", "window.scrollTo(0, document.body.scrollHeight)"),
                    # 2. Wait 3 seconds for the new items to load into the HTML
                    PageMethod("wait_for_timeout", 3000), 
                    # Optional: Add another scroll if the page loads items in multiple batches
                    PageMethod("evaluate", "window.scrollTo(0, document.body.scrollHeight)"),
                    PageMethod("wait_for_timeout", 3000),
                ]
            },
            callback=self.parse)

    async def parse(self, response):
        page = response.meta["playwright_page"]
        main_url = "https://www.modaoperandi.com/"
        
        
        products = response.css("div.VariantCell")
        seen_links = set()
        
        for product in products:
            item = FashionCrawlerItem()
            link = product.css('a::attr(href)').get()

            if link:
                link = urljoin(main_url, link)

            if link in self.seen_links:
                continue
            seen_links.add(link)
            title = product.css('a::attr(aria-label)').get()
            if not title:
                title = product.css('::text').get()


            if title and link and 'modaoperandi.com' in link:
                item['title'] = title.strip()
                item['link'] = link

            yield response.follow(link, 
                                  callback=self.parse_product, 
                                  meta={
                                      'item': item, 
                                      'playwright': True, 
                                      "playwright_include_page": True,
                                      })

        next_button = page.locator("button.Paginator__button--next")
        has_next = (await next_button.count() > 0) and not (await next_button.is_disabled())

        if has_next:
            await next_button.click()
            await page.wait_for_load_state("networkidle")

            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(3000)

            webpage = await page.content()
            new_response = response.replace(body=webpage.encode("utf-8"))

            # recurse into the same live page for the next round of clicks/scraping
            async for result in self.parse(new_response):
                yield result
        else:
            await page.close()
         

    async def parse_product(self, response):
        page = response.meta.get("playwright_page")
        item = response.meta["item"]

        price = response.css(
            "div.ProductDetails span.PDPProductPrice__current-price::text"
        ).get()
        details = response.css(
            "div.ProductDetails div.Expandable__contents div ul li::text"
        ).getall()
        composition = response.xpath(
            '//li[contains(text(), "Composition")]/text()'
        ).getall()

        if price:
            item["price"] = price.strip()
        if composition:
            item["composition"] = composition
        if details:
            item["details"] = details

        if page:
            await page.close()  # <-- the missing piece: release the product page every time

        yield item