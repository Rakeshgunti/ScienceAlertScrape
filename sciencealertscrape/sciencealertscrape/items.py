# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class TrendingSchema(scrapy.Item):
    Rankings = scrapy.Field()
    Category = scrapy.Field()
    Heading = scrapy.Field()
    Link = scrapy.Field()

class ArticleSchema(scrapy.Item):
    Category = scrapy.Field()
    Heading = scrapy.Field()
    Authors = scrapy.Field()
    PostedDate = scrapy.Field()
    Images = scrapy.Field()
    Content = scrapy.Field()
    RefLinks = scrapy.Field()
    Link = scrapy.Field()