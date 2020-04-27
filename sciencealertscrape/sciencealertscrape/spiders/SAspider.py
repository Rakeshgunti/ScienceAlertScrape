import sys
import os
import json
import scrapy
from scrapy.http.request import Request
from scrapy.crawler import CrawlerRunner
from datetime import datetime, timedelta
from twisted.internet import reactor, defer
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings


class SATrendingspider(scrapy.Spider):
    name = "ScienceAlertTrending"

    collection_name = 'Trending'

    start_urls = [
        'https://www.sciencealert.com/trending'
    ]

    def __init__(self):
        self.base_url = "https://www.sciencealert.com"

    def parse(self, response):
        hxs = scrapy.Selector(response)
        links = []
        count = 1
        section = '//*[@id="rt-mainbody"]/div/div/div/div[1]/div[1]/div/div/div'
        links.append([self.base_url+
            hxs.xpath(section+'/div[1]/div/div/div[1]/div[1]/a/@href').extract_first().strip(), count])
        
        for x in hxs.xpath(section+'/div[2]/*/div/div[1]/div[1]/a/@href').extract():
            count += 1
            links.append([self.base_url+x.strip(), count])

        for i in links:
            yield Request(i[0], meta={'item': i[1]} ,callback=self.parseEachLink)

    def parseEachLink(self, response):
        hxs = scrapy.Selector(response)
        item = TrendingLink()
        item['Rank'] = response.meta['item']
        item['Category'] = self.__extract_category(hxs)
        item['Heading'] = self.__extract_headline(hxs)
        item['Author'] = self.__extract_author(hxs)
        item['PostedDate'] = self.__extract_date(hxs)
        item['Date'] = datetime.now()
        item['Content'] = self.__extract_content(hxs)
        return item
    
    def __extract_date(self, hxs):
        return datetime.strptime(hxs.xpath(
            '//*[@id="rt-mainbody"]/div/div/div[2]/div/div[1]/div[3]/div/div[3]/div[2]/div[2]/span/text()'
            ).extract_first().strip(), "%d %B %Y")

    def __extract_content(self, hxs):
        return ' '.join(hxs.xpath(
            '//*[@class="article-mainbody-container"]/div/div/*[self::p or self::h2 or self::url or self::a]//text()'
            ).extract())

    def __extract_category(self, hxs):
        return hxs.xpath(
            '//*[@id="rt-mainbody"]/div/div/div[2]/div/div[1]/div[3]/div/div[1]/a/text()').extract_first().strip()

    def __extract_headline(self, hxs):
        return hxs.xpath(
            '//*[@id="rt-mainbody"]/div/div/div[2]/div/div[1]/div[3]/div/div[2]/h1/text()').extract_first().strip()

    def __extract_author(self, hxs):
        return hxs.xpath(
            '//*[@id="rt-mainbody"]/div/div/div[2]/div/div[1]/div[3]/div/div[3]/div[2]/div[1]/span/text()'
            ).extract_first().strip()


class SALatestspider(scrapy.Spider):
    name = "ScienceAlertLatest"

    collection_name = 'Latest'

    start_urls = [
        'https://www.sciencealert.com/latest'
    ]

    def __init__(self):
        self.base_url = "https://www.sciencealert.com"

    def parse(self, response):
        hxs = scrapy.Selector(response)
        section_paths = ['//*[@id="rt-mainbody"]/div/div/div/div[1]/div[1]',
                         '//*[@id="rt-mainbody"]/div/div/div/div[1]/div[3]']
        links = self.__extract_latest_links(hxs, section_paths)
        for i in links:
            yield Request(i[0], meta={'item': i[1]} ,callback=self.parseEachLink)

    def parseEachLink(self, response):
        hxs = scrapy.Selector(response)
        hours = response.meta['item']
        item = LatestLink()
        item['Category'] = self.__extract_category(hxs)
        item['Heading'] = self.__extract_headline(hxs)
        item['Author'] = self.__extract_author(hxs)
        item['Date'] = self.__extract_date(hxs, hours)
        item['Content'] = self.__extract_content(hxs)
        return item

    def __extract_latest_links(self, hxs, section_paths):
        links = []
        for section in section_paths:
            if self.__check_hours(hxs, section, 't'):
                links.append([self.base_url + hxs.xpath(
                    section + '/div/div/div/div[1]/div/div/div[1]/div[1]/a/@href').extract_first().strip(), 
                    self.__get_hours(hxs, section, 't')])
            
            links += [ [self.base_url + x.strip(), self.__get_hours(hxs, section, 'o')] 
                for x in hxs.xpath(section + '/div/div/div/div[2]/*/div/div[1]/div[1]/a/@href').extract()
                    if self.__check_hours(hxs, section, 'o')]
        return links
    
    def __check_hours(self, hxs, section, Id):
        keywrds = ['hours', 'hour', 'minute', 'minutes']
        if Id == 't':
            return hxs.xpath(
                section+'/div/div/div/div[1]/div/div/div[2]/div[2]/div/text()'
                ).extract_first().strip().split()[1] in keywrds
        else:
            return hxs.xpath(
                section+'/div/div/div/div[2]/*/div/div[2]/div[2]/div/text()'
                ).extract_first().strip().split()[1] in keywrds

    def __get_hours(self, hxs, section, Id):
        if Id == 't':
            return int(hxs.xpath(
                section+'/div/div/div/div[1]/div/div/div[2]/div[2]/div/text()').extract_first().strip().split()[0])
        else:
            return int(hxs.xpath(
                section+'/div/div/div/div[2]/*/div/div[2]/div[2]/div/text()').extract_first().strip().split()[0])
    
    def __extract_date(self, hxs, hrs):
        return datetime.strptime(hxs.xpath(
            '//*[@id="rt-mainbody"]/div/div/div[2]/div/div[1]/div[3]/div/div[3]/div[2]/div[2]/span/text()'
            ).extract_first().strip(), "%d %B %Y") + timedelta(hours=hrs)

    def __extract_content(self, hxs):
        return ' '.join(hxs.xpath(
            '//*[@class="article-mainbody-container"]/div/div/*[self::p or self::h2 or self::url or self::a]//text()'
            ).extract())

    def __extract_category(self, hxs):
        return hxs.xpath(
            '//*[@id="rt-mainbody"]/div/div/div[2]/div/div[1]/div[3]/div/div[1]/a/text()').extract_first().strip()

    def __extract_headline(self, hxs):
        return hxs.xpath(
            '//*[@id="rt-mainbody"]/div/div/div[2]/div/div[1]/div[3]/div/div[2]/h1/text()').extract_first().strip()

    def __extract_author(self, hxs):
        return hxs.xpath(
            '//*[@id="rt-mainbody"]/div/div/div[2]/div/div[1]/div[3]/div/div[3]/div[2]/div[1]/span/text()'
            ).extract_first().strip()

@defer.inlineCallbacks
def crawl():
    yield runner.crawl(SALatestspider)
    yield runner.crawl(SATrendingspider)
    d = runner.join()
    d.addBoth(lambda _: reactor.stop())

if __name__ == "__main__":
    sys.path.append(os.getcwd()+"\\..")
    from items import LatestLink, TrendingLink
    s = get_project_settings()
    s.update(dict(LOG_ENABLED="False"))
    configure_logging(s)
    runner = CrawlerRunner(s)
    crawl()
    reactor.run() # the script will block here until the last crawl call is finished
