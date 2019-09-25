import unittest
from bs4 import BeautifulSoup
from src.classes.model.webdriver import WebDriver
from src.classes.sorter.content_sorter import ContentSorter
from src.classes.reporter.report_generator import ReportGenerator


class TestContentSorter(unittest.TestCase):

    def setUp(self):
        self.driver = WebDriver()
        self.test_content_sorter = ContentSorter()
        self.res_content_sorter = ContentSorter()

    def tearDown(self):
        self.driver.proxy.close()
        self.driver.driver.close()
        self.driver.driver.quit()

    def getting_sorter_resource(self, url):
        html = self.driver.parse_page(url)[0]
        soup = BeautifulSoup(html, 'html.parser')
        return soup

    def test_regular_tag_content(self):
        """
        Aims to test if regular tags are sorted properly into the right directi-
        ves.

        :return: passed or failed in test pipeline
        """

        # Setting the url attribute in the sorter
        url = 'http://localhost:4000/regular_tag_content'
        soup = self.getting_sorter_resource(url)
        self.test_content_sorter.url = url
        self.test_content_sorter.soup = soup
        self.test_content_sorter.sort_regular_tag_info()

        self.res_content_sorter.directives_sources['img-src'].add('http://localhost:4000/img.gif')
        self.res_content_sorter.directives_sources['media-src'].add('http://localhost:4000/audio1.ogg')
        self.res_content_sorter.directives_sources['media-src'].add('http://localhost:4000/audio/audio2.mp3')
        self.res_content_sorter.directives_sources['media-src'].add('http://localhost:4000/video/pass-countdown.ogg')
        self.res_content_sorter.directives_sources['media-src'].add(
            'http://mysuperaudioresourcesite.com/awesomesound.ogg')
        self.res_content_sorter.directives_sources['media-src'].add('http://localhost:4000/media/track1.vtt')
        self.res_content_sorter.directives_sources['media-src'].add('http://localhost:4000/media/track2.vtt')
        self.res_content_sorter.directives_sources['object-src'].add('http://localhost:4000/embed.swf')
        self.res_content_sorter.directives_sources['object-src'].add('http://localhost:4000/applet.class')
        self.res_content_sorter.directives_sources['form-action'].add('http://evil_test.fr')
        self.res_content_sorter.directives_sources['child-src'].add('http://frame.access')

        print(self.res_content_sorter.directives_sources)
        print(self.test_content_sorter.directives_sources)
        assert (self.res_content_sorter.directives_sources == self.test_content_sorter.directives_sources)

    def test_link_tag_content(self):
        """
        Aims to test if nested variable are resolved correctly when possible ty-
        pically if it gets renamed of is referred  with another alias within the
        code

        :return: passed or failed in test pipeline
        """

        # Setting the url attribute in the sorter
        url = 'http://localhost:4000/link_tag_content'
        soup = self.getting_sorter_resource(url)
        self.test_content_sorter.url = url
        self.test_content_sorter.soup = soup
        self.test_content_sorter.sort_link_tag_info()

        # Building reference for empty directive dictionary
        self.res_content_sorter.build_empty_directive_dict()
        # Defining the solution
        self.res_content_sorter.directives_sources['script-src'].add('http://localhost:4000/test.js')
        self.res_content_sorter.directives_sources['img-src'].add('http://localhost:4000/favicon')
        self.res_content_sorter.directives_sources['style-src'].add(
            'http://localhost:4000/media/examples/link-element-example.css')
        self.res_content_sorter.directives_sources['prefetch-src'].add('http://localhost:4000/style.css')
        self.res_content_sorter.directives_sources['prefetch-src'].add('http://localhost:4000/preload.css')
        self.res_content_sorter.directives_sources['manifest-src'].add('http://localhost:4000/preload.css')
        self.res_content_sorter.directives_sources['manifest-src'].add('http://localhost:4000/manifest.css')
        self.res_content_sorter.directives_sources['prefetch-src'].add('http://localhost:4000/dns-prefetch.dns')

        print(self.res_content_sorter.directives_sources)
        print(self.test_content_sorter.directives_sources)

        assert (self.res_content_sorter.directives_sources == self.test_content_sorter.directives_sources)

    def test_inline_directive_nonce(self):
        """
        Aims to test if nonce are correctly taken into account when looping
        through the script tags

        :return: passed or failed in test pipeline
        """
        # Setting the url attribute in the sorter
        url = 'http://localhost:4000/inline_directive_nonce'
        soup = self.getting_sorter_resource(url)
        self.test_content_sorter.url = url
        self.test_content_sorter.soup = soup
        self.test_content_sorter.add_inline_directives()

        assert (self.test_content_sorter.directives_sources == self.res_content_sorter.directives_sources)

    def test_inline_directive_source(self):
        """
        Aims to test if inline directive are correctly added when inline script
        and inline style is present

        :return: passed or failed in test pipeline
        """
        # Setting the url attribute in the sorter
        url = 'http://localhost:4000/inline_directive'
        soup = self.getting_sorter_resource(url)
        self.test_content_sorter.report_generator = ReportGenerator()
        self.test_content_sorter.url = url
        self.test_content_sorter.soup = soup
        self.test_content_sorter.add_inline_directives()

        self.res_content_sorter.directives_sources['script-src'].add("'unsafe-inline'")
        self.res_content_sorter.directives_sources['style-src'].add("'unsafe-inline'")

        print(self.test_content_sorter.directives_sources)
        assert (self.test_content_sorter.directives_sources == self.res_content_sorter.directives_sources)

    def test_sandbox_sourcing(self):
        """
        Aims to test if sandbox attributes are correctly added to the sandbox
        directive
        :return: passed or failed in test pipeline
        """
        # Setting the url attribute in the sorter
        url = 'http://localhost:4000/sandbox_directive'
        soup = self.getting_sorter_resource(url)
        self.test_content_sorter.url = url
        self.test_content_sorter.soup = soup
        self.test_content_sorter.add_sandbox_directive()

        self.res_content_sorter.directives_sources['sandbox'].add('allow-same-origin')
        self.res_content_sorter.directives_sources['sandbox'].add('allow-scripts')
        self.res_content_sorter.directives_sources['sandbox'].add('allow-top-navigation')
        assert (self.res_content_sorter.directives_sources == self.test_content_sorter.directives_sources)
