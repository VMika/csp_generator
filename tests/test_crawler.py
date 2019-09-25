import unittest

from src.classes.model.crawler import Crawler


class TestCrawler(unittest.TestCase):

    def test_url_list(self):
        """
        Tests the extraction of all links inside a page. It should
        exclude all the links outside of the allowed domains, links that returns
        errors (typically 404) and it should not return duplicates of links.

        :return: passed or failed in test pipeline
        """
        crawler = Crawler(
            ['http://localhost:4000/test_link_list'],
            ['localhost'],
            set()
        )

        url_list = [
            'http://localhost:4000/test_link_list',
            'http://localhost:4000/d1',
            'http://localhost:4000/d2',
            'http://localhost:4000/d3',
            'http://localhost:4000/d4',
            'http://localhost:4000/d5',
            'http://localhost:4000/d6',
            'http://localhost:4000/d7',
            'http://localhost:4000/d8',
            'http://localhost:4000/d9'
        ]

        res = set(url_list)
        crawler.self_contained_run()
        print(crawler.links)
        assert (res == crawler.links)
