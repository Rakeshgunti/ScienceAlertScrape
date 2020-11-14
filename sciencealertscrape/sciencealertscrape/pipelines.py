# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import sys
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
        self.count = 0

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
        print("{num} records are processed by {name}".format(num=self.count, name=spider.name))
        self.client.close()

    def process_item(self, item, spider):
        try:
            self.count += 1
            if spider.name == "ScienceAlertHomePage":
                self.collection.update_one({"Heading" : item['Heading'], "Link": item['Link'], 'Category': item['Category'] }, 
                                            {"$set": item}, upsert=True)
                
            if spider.name == "ScienceAlertLatest":
                atleastOne = self.collection.find_one({"Heading" : item['Heading'], "Link": item['Link'], 'Category': item['Category']})
                
                if atleastOne and atleastOne['PostedDate'] > item['PostedDate']:
                    item['PostedDate'] = atleastOne['PostedDate']
                    self.collection.update_one({"Heading" : item['Heading'], "Link": item['Link'], 'Category': item['Category']}, {"$set": item}, upsert=True)
                
                elif atleastOne is None or (atleastOne and atleastOne['PostedDate'] < item['PostedDate']):
                    self.collection.update_one({"Heading" : item['Heading'], "Link": item['Link'], 'Category': item['Category']}, {"$set": item}, upsert=True)

            if spider.name == "ScienceAlertTrending":
                Articles_col = self.db['Articles']
                Article = Articles_col.find_one({"Heading" : item['Heading'], "Link": item['Link'], 'Category': item['Category']}, {"_id":1})
                
                if Article.get("_id"):
                    item['Rankings']['Date'] = item['Rankings']['Date'].replace(hour=0, minute=0, second=0, microsecond=0)
                    self.collection.update_one({"ArticleId" : Article['_id']}, {"$set" : {"Link": item['Link'], 'Category': item['Category'] },
                            "$addToSet" : {"Rankings": item['Rankings']}}, upsert=True)
            
            print("Item No: "+str(self.count)+" by "+spider.name)
        except Exception as e:
            self.close_spider()
            sys.exit(e)