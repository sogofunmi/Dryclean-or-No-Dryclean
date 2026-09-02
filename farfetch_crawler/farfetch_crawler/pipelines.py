# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class FarfetchCrawlerPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        if adapter.get('title'):
            adapter['title'] = " ".join(adapter['title'].split())
        if adapter.get('composition'):
            adapter['composition'] = " ".join(adapter['composition'].split())
        if adapter.get('care'):
            adapter['care'] = " ".join(adapter['care'].split())
