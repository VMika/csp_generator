""" Implements LinkSpider class """
from bs4 import BeautifulSoup
from selenium import webdriver
from scrapy.spiders import Spider
from scrapy.crawler import CrawlerProcess

from config import GECKO_DRIVER, DB_FILE


class Crawler(Spider):
    """
    Class designed to crawl links of the page

    Visits the url of a webpage recursively until all links in the allowed do-
    main has been visited. Used to build a complete URL list that will allow us
    to build a CSP for the entire domain.
    """
    name = 'Crawler'
    db_file = DB_FILE

    def __init__(self, start_urls='', allowed_domains='', links=None, gen_id=None):
        print('Initiated driver')

        self.start_urls = start_urls
        self.allowed_domains = allowed_domains
        self.links = links
        self.gen_id = gen_id

        self._driver_path = GECKO_DRIVER

        options = webdriver.FirefoxOptions()
        options.headless = True

        profile = webdriver.FirefoxProfile()
        profile.assume_untrusted_cert_issuer = True
        profile.accept_untrusted_certs = True

        capabilities = webdriver.DesiredCapabilities.FIREFOX.copy()
        capabilities['accepSslCerts'] = True
        capabilities['trustAllSSLCertificates'] = True

        self.driver = webdriver.Firefox(
            firefox_options=options,
            firefox_profile=profile,
            executable_path=str(self._driver_path),
            desired_capabilities=capabilities
        )

    def parse(self, response):
        print("Parsing  page :", response.url)
        self.links.add(response.url)
        print(self.links)
        print("Getting response")
        self.driver.get(response.url)
        print("Got response")
        while self.driver.execute_script('return document.readyState;') != 'complete':
            print('not done loading')

        html = self.driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
        soup = BeautifulSoup(html, 'html.parser')
        links = soup.find_all('a')
        for link in links:
            print(link)
            print(link.attrs)
            print(type(link.attrs))
            try:
                link = link['href']
                yield response.follow(link)
            except KeyError:
                pass

    def self_contained_run(self):
        process = CrawlerProcess({
            'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
        })
        process.crawl(self, self.start_urls, self.allowed_domains, self.links)
        process.start()
        self.driver.quit()
