# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class FarfetchCrawlerItem(scrapy.Item):
    title = scrapy.Field()
    link = scrapy.Field()
    price = scrapy.Field()
    composition = scrapy.Field()
    care = scrapy.Field()
