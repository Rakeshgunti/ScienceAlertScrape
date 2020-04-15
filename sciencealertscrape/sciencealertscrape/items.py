# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class LatestLink(scrapy.Item):
    Category = scrapy.Field()
    Heading = scrapy.Field()
    Author = scrapy.Field()
    Date = scrapy.Field()
    Content = scrapy.Field()

class TrendingLink(scrapy.Item):
    Rank = scrapy.Field()
    Category = scrapy.Field()
    Heading = scrapy.Field()
    Author = scrapy.Field()
    PostedDate = scrapy.Field()
    Date = scrapy.Field()
    Content = scrapy.Field()