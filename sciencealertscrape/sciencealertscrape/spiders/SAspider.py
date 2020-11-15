import sys
import os
import re
import json
import scrapy
from scrapy.http.request import Request
from scrapy.crawler import CrawlerRunner
from datetime import datetime, timedelta
from twisted.internet import reactor, defer
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from items import TrendingSchema, ArticleSchema

class preProcess:
    """
    Class consists of pre-processing and validating data w.r.t functions before populating the Item
    """
    def __init__(self):
        """
        Initialzer sets value for base_url
        """
        self.base_url = "https://www.sciencealert.com"
    
    def extract_links_deltas(self, hxs):
        """
        Extracts links and Time deltas using hxs during Initial run of crawler return zipped values of links & timeDeltas
        """
        links = (self.base_url+link for link in hxs.xpath('//*[@class="titletext"]/a/@href').extract())
        timeDeltas = (self.get_time_delta(delta.strip()) for delta in hxs.xpath('//*[@class="time"]/text()').extract())
        return ( (link, timeDelta) for link, timeDelta in zip(links, timeDeltas) )
    
    def get_time_delta(self, delta):
        """
        Calculates Time delta for the text extracted in the link
        """
        time_delta = delta.split()
        keywrds = {'hours' : eval('timedelta(hours=int(time_delta[0]))'), 
                'hour' : eval('timedelta(hours=int(time_delta[0]))'),
                'minute' : eval('timedelta(minutes=int(time_delta[0]))'), 
                'minutes' : eval('timedelta(minutes=int(time_delta[0]))'),
                'day' : eval('timedelta(days=int(time_delta[0]))'), 
                'days' : eval('timedelta(days=int(time_delta[0]))'), 
                'second' : eval('timedelta(seconds=int(time_delta[0]))'), 
                'seconds' : eval('timedelta(seconds=int(time_delta[0]))')}
        if time_delta[1] in keywrds:
            return keywrds[time_delta[1]], time_delta[1]
        else:
            dt = datetime.strptime(delta, "%d %B %Y")
            return  dt, None
    
    def extract_date(self, delta, delta_txt):
        """
        Transforms text into datetime format of the given response and appends time delta and returns the datetime object
        """
        if delta_txt in ['second', 'seconds', 'minute', 'minutes', 'hour', 'hours', 'day', 'days']:
            return datetime.utcnow() - delta

    def extract_content(self, hxs):
        """
        Extracts Full text or article content from the set xapth
        """
        return ' '.join(hxs.xpath('//*[@class="article-fulltext"]/*[self::p or self::h2 or self::url or self::a]/text()').extract())

    def extract_category(self, hxs):
        """
        Extracts Category of the article
        """
        return hxs.xpath('//*[@class="article-intro-text-container"]/div/a/text()').extract_first().strip()
    
    def extract_refLinks(self, hxs):
        """
        Extracts all reference links attached to the article content
        """
        links = hxs.xpath('//*[@class="article-fulltext"]/*/a//@href').extract()
        text = hxs.xpath('//*[@class="article-fulltext"]/*/a//text()').extract()
        return [{"name":key.strip(), "link":val} for key, val in zip(text, links)]

    def extract_imageLinks(self, hxs):
        """
        Extracts Article Image and all other image respective links
        """
        Images = dict(Article_img='', Other_Imgs=[])
        Images['Article_img'] = self.base_url+hxs.xpath('//*[@id="article_img"]/@src').extract_first().strip()
        Images['Other_Imgs'].extend([self.base_url+link for link in hxs.xpath('//*[@class="article-fulltext"]/*//img/@src').extract()])
        return Images

    def extract_headline(self, hxs):
        """
        Extracts title of the Article
        """
        return hxs.xpath('//*[@class="article-title"]/h1/text()').extract_first().strip()

    def extract_author_org(self, hxs):
        """
        Extracts Author of the article
        """
        authors_org = hxs.xpath('//*[@class="author-name-text"]/div[1]/span/text()').extract_first().strip()
        if authors_org=='' or (not authors_org):
            authors_org = hxs.xpath('//*[@class="author-name-text"]/div[1]/span/a/text()').extract_first().strip()
        return authors_org
    
    def parseArticleLink(self, response):
        """
        Each Article data is parsed through this method and respective functions are called to get respective data.
        """
        hxs = scrapy.Selector(response)
        item = ArticleSchema()
        delta, delta_txt = response.meta.get('delta')
        item['Link'] = response.meta.get('Link')
        item['Category'] = self.extract_category(hxs)
        item['Heading'] = self.extract_headline(hxs)
        item['PostedDate'] = self.extract_date(delta, delta_txt) if delta_txt else delta
        item['Images'] = self.extract_imageLinks(hxs)
        item['Content'] = self.extract_content(hxs)
        item['RefLinks'] = self.extract_refLinks(hxs)
        item['Authors'] = self.extract_author_org(hxs)
        return item
    
    def extract_trending_data(self, hxs):
        """
        This method captures links, Categories, Titles of Trending articles
        """
        links = (self.base_url+link for link in hxs.xpath('//*[@class="titletext"]/a/@href').extract())
        categories = (hxs.xpath('//*[@class="title-container"]/div[1]/a/text()').extract())
        titles = (hxs.xpath('//*[@class="titletext"]/a/text()').extract())
        return ((link, category.strip("\n"), title.strip("\n")) for link, category, title in zip(links, categories, titles))

    def extract_latest_links_deltas(self, hxs):
        """
        Extracts links withnin 24hours and respective deltas
        """
        keywrds = ['second', 'seconds', 'minutes', 'minute', 'hours', 'hour']
        links = (self.base_url+link for link in hxs.xpath('//*[@class="titletext"]/a/@href').extract())
        deltas = (hxs.xpath('//*[@class="time"]/text()').extract())
        return ((link_delta[1], self.get_time_delta(link_delta[0].strip())) for link_delta in zip(deltas, links) if link_delta[0].split()[1] in keywrds)


class SATrendingspider(scrapy.Spider):
    """
    This spider will scrape the data from Trending Page of Sciencealert.com website
    """
    name = "ScienceAlertTrending"
    collection_name = 'TrendingArticles'
    start_urls = [ 'https://www.sciencealert.com/trending' ]

    def parse(self, response):
        try:
            hxs = scrapy.Selector(response)
            PP = preProcess()
            TrendingData = enumerate(PP.extract_trending_data(hxs), start=1)
            item = TrendingSchema()
            for data in TrendingData:
                item['Rankings'] = { 'Rank' : data[0], 'Date': datetime.utcnow() }
                item['Link'], item['Category'], item['Heading']  = data[1]
                yield item
        except  Exception as e:
            sys.exit(e)

class SALatestspider(scrapy.Spider):
    """
    This spider will scrape the data of last 24 hours from Latest Page of Sciencealert.com website
    """
    name = "ScienceAlertLatest"
    collection_name = 'Articles'
    start_urls = [ "https://www.sciencealert.com/index.php?option=com_sciencealertfrontpage&view=latestarticles&start={num}&cat_title=latest&tmpl=component".format(num=i) for i in range(0, 16, 5) ]
        
    def parse(self, response):
        try:
            hxs = scrapy.Selector(response)
            PP = preProcess()
            linksDeltas = PP.extract_latest_links_deltas(hxs)
            for i in linksDeltas:
                yield Request(i[0], meta={'Link': i[0], 'delta': i[1]}, callback=PP.parseArticleLink)
        except Exception as e:
            sys.exit(e)

class SAHomePagespider(scrapy.Spider):
    """
    This spider will scrape the all Articles under 700 latest Pages of Sciencealert.com website
    """
    name = "ScienceAlertHomePage"
    collection_name = 'Articles'
    start_urls = [ 'https://www.sciencealert.com/index.php?option=com_sciencealertfrontpage&view=latestarticles&start={num}&cat_title=the-latest&tmpl=component'.format(num=i) for i in range(0, 700, 5) ]

    def parse(self, response):
        hxs = scrapy.Selector(response)
        PP = preProcess()
        linksDeltas = PP.extract_links_deltas(hxs)
        for i in linksDeltas:
            yield Request(i[0], meta={'Link': i[0], 'delta': i[1]}, callback=PP.parseArticleLink)

@defer.inlineCallbacks
def initialCrawl():
    """
    This method will enable the SAHomePagespider Spider
    """
    try:
        print("Starting Initial download crawl")
        yield runner.crawl(SAHomePagespider)
        d = runner.join()
        d.addBoth(lambda _: reactor.stop())
    except Exception as e:
        sys.exit(e)

@defer.inlineCallbacks
def dailyCrawl():
    """
    This method will enable the SALatestspider, SATrendingspider Spiders
    """
    try:
        print("Starting daily download crawl")
        yield runner.crawl(SALatestspider)
        yield runner.crawl(SATrendingspider)
        d = runner.join()
        d.addBoth(lambda _: reactor.stop())
    except Exception as e:
        sys.exit(e)

if __name__ == "__main__":
    try:
        load = sys.argv[1]
        s = get_project_settings()
        s.update(dict(LOG_ENABLED="False"))
        configure_logging(s)
        runner = CrawlerRunner(s)
        if load == "initial":
            initialCrawl()
        elif load == "daily":
            dailyCrawl()
        reactor.run() # the script will block here until the last crawl call is finished
    except Exception as e:
        sys.exit(e)
