# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
from scrapy.exceptions import DropItem
from scrapy import signals
from scrapy import log
from Med.items import MedItem
from twisted.enterprise import adbapi
from scrapy.exporters import JsonLinesItemExporter

class MedPipeline(object):
    def __init__(self):
        self.ids_seen = set()

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline

    def spider_opened(self, spider):
        self.file = open('medData.json', 'wb')
        self.expoter = JsonLinesItemExporter(self.file)
        self.expoter.start_exporting()
        
    def spider_closed(self, spider):
        self.expoter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        if int(item['reply_num'][0]) == 0:
        	raise DropItem("no reply in %s" % item)
        elif item['post_id'] in self.ids_seen:
        	raise DropItem("Duplicate item found: %s" % item)
        else:
            self.ids_seen.add(item['post_id'])
            self.expoter.export_item(item)
            return item
