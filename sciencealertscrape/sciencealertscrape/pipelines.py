# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from pymongo import MongoClient
from scrapy.exceptions import DropItem
from datetime import datetime, timedelta


class MongoDBPipeline(object):

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.client = None
        self.db = None
        self.collection = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items')
        )

    def open_spider(self, spider):
        print("Database connection started")
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        if hasattr(spider, 'collection_name'):
            self.collection = self.db[spider.collection_name]

    def close_spider(self, spider):
        print("Database connection closed")
        self.client.close()

    def process_item(self, item, spider):
        if self.collection == 'Latest':
            if item.get('Date') >= (datetime.now() - timedelta(1)):
                print("Processing Item : "+item['Category'])
                self.collection.insert_one(dict(item))
                return item
            else:
                raise DropItem("Older Record")
        else:
            self.collection.insert_one(dict(item))
            return item

    # def process_item(self, item, spider):
    #     print("Processing Item : {}".format(item['Category']))
    #     return item