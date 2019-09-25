""" File implementing crawler runner class """

from scrapy import signals
from scrapy.crawler import CrawlerRunner


class UrlCrawlerRunner(CrawlerRunner):
    """
    Class defining the crawler runner object user to crawl asynchronously
    """

    def __init__(self, settings=None):
        super().__init__(settings=None)
        self.settings = settings
        self.gen_id = None
        self.items = []

    def crawl(self, crawler_or_spidercls, *args, **kwargs):
        # keep all items scraped
        self.gen_id = kwargs['gen_id']
        # create crawler (Same as in base CrawlerProcess)
        crawler = self.create_crawler(crawler_or_spidercls)

        # handle each item scraped
        crawler.signals.connect(self.item_scraped, signals.item_scraped)

        # create Twisted.Deferred launching crawl
        dfd = self._crawl(crawler, *args, **kwargs)

        # add callback - when crawl is done cal return_items
        dfd.addCallback(self.return_items)
        return dfd

    def item_scraped(self, item, response, spider):
        self.items.append(item)

    def return_items(self, result):
        return self.items, self.gen_id
