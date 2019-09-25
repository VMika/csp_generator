""" Implements WebDriver class"""
from selenium import webdriver
from browsermobproxy import Server
from config import PROXY, GECKO_DRIVER


class WebDriver:
    """
    Class designed to navigate to a specific URL

    Will only parse and send material to CSP generator for further analysis
    """
    def __init__(self):
        print('init webdriver')
        self.server = Server(
            path=PROXY
        )
        self.server.start()
        self.proxy = self.server.create_proxy()
        self._executable_path = GECKO_DRIVER
        options = webdriver.FirefoxOptions()
        options.headless = True
        profile = webdriver.FirefoxProfile()
        profile.set_proxy(self.proxy.selenium_proxy())
        profile.accept_untrusted_certs = True
        profile.assume_untrusted_cert_issuer = True
        # profile.set_preference()

        self.driver = webdriver.Firefox(
            firefox_options=options,
            firefox_profile=profile,
            executable_path=self._executable_path,
            proxy=self.proxy.proxy,
        )
        print('end webdriver')

    def parse_page(self, url):
        print("Parsing : ", url)
        self.proxy.new_har(url, options={'captureHeaders': True})
        print("Getting URL : ", url)
        self.driver.get(url)

        while self.driver.execute_script('return document.readyState;') != 'complete':
            print('not done loading')
        html = self.parse_html()
        har = self.parse_har()
        print('HAR : ', har)
        return html, har

    def parse_html(self):
        html = self.driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
        return html

    def parse_har(self):
        return self.proxy.har

    def close(self):
        self.driver.stop_client()
        self.driver.close()
        self.driver.quit()
