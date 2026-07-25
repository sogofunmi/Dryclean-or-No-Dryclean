import scrapy
from fashion_crawler.items import FashionCrawlerItem
from urllib.parse import urljoin, urlencode



class FashionSpider(scrapy.Spider):
    name = "fashion"
    
    allowed_domains = ["modaoperandi.com"]

    start_urls = [
        "https://www.modaoperandi.com/women/products/clothing?page=%s" % page for page in range(1, 20)
        #"https://www.theoutnet.com/en-us/collections/clothing?pageNumber=1"
    ]

    #def start_requests(self):
        #url = "https://www.modaoperandi.com/women/products/clothing"

      
        #yield scrapy.Request(url=api_url, callback=self.parse)
        #yield scrapy.Request(url, callback=self.parse, meta={"playwright": True})
        
    
    def parse(self, response):
        main_url = "https://www.modaoperandi.com/"

        #products = response.css("div.ProductList0_productItemContainer")
        products = response.css("div.VariantCell")
        seen_links = set()
        for product in products:
            item = FashionCrawlerItem()
            link = product.css('a::attr(href)').get()

            if link:
                link = urljoin(main_url, link)

            if link in seen_links:
                continue
            seen_links.add(link)
            title = product.css('a::attr(aria-label)').get()
            if not title:
                title = product.css('::text').get()


            if title and link and 'modaoperandi.com' in link:
                item['title'] = title.strip()
                item['link'] = link

                yield scrapy.Request(
                    link,
                    callback=self.parse_product,
                    meta={'item':item, "playwright": True}
                )

        #for product in response.css("div.ProductList0_productItemContainer"):
            #link_element = product.css("a")

            #yield response.follow(link_element, callback=self.parse_item_details)
            #yield {
                #"item_link": product.css("a::attr(href)").get()}
        #next_page = response.css("div.Pagination7__box a::attr(href)").get()

        #if next_page is not None:
            #yield response.follow(next_page, callback=self.parse)

        #item_link =  product.css("a::attr(href)").get()

    def parse_product(self, response):
        item = response.meta['item']
        price = response.css("div.ProductDetails span.PDPProductPrice__current-price::text").get()
        details = response.css("div.ProductDetails div.Expandable__contents div ul li::text").getall()
        
        composition = response.xpath('//li[contains(text(), "Composition")]/text()').getall()

        if price:
            item['price'] = price.strip()
        if details:
            item['details'] = [det for det in details if not any(word in det for word in ["Fall", "Spring", "Winter", "Summer", "Made", "Our model"])]
        if composition:
            item['composition'] = composition
        
        yield item


