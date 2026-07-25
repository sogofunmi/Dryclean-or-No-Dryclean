# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class FashionCrawlerPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        if adapter.get('title'):
            adapter['title'] = " ".join(adapter['title'].split())
        if adapter.get('link') and not adapter['link'].startswith('http'):
            adapter['link'] =  spider.stats_urls[0] + adapter['link']
        if adapter.get('details'):
            adapter['details'] = " ".join(adapter['details'].split())

            
        return item
