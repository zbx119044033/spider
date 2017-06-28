# -*- coding: utf-8 -*-

import codecs
import json
from scrapy.exceptions import DropItem
import pymongo

# Define your item pipelines here
# Don't forget to add your pipelines to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class FilterPipeline(object):
    def __init__(self):
        self.title_seen = set()

    def process_item(self, item, spider):
        if item['name'] in self.title_seen:
            raise DropItem("Duplicate item found: %s" % item['name'])
        else:
            self.title_seen.add(item['name'])
        return item


class JsonWriterPipeline(object):
    def __init__(self):
        self.file = codecs.open('test.json', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(line)
        return item


class MongoPipeline(object):

    collection_name = 'zbx_vobao_product13'

    def __init__(self, mongo_uri, mongo_db):
        print "MongoPipeline init"
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'Simba')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        print "MongoPipeline open_spider"

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        print "MongoPipeline process "
        self.db[self.collection_name].insert(dict(item))
        return item

