""" Implements main class CspGenerator """

# Import for silencing logs
import logging
import urllib3.connectionpool
import selenium.webdriver.remote.remote_connection

from config import DB_FILE
from src.classes.model.csp import Csp
from src.classes.model.webdriver import WebDriver
from src.classes.db.db_controller import DbController
from src.classes.sorter.script_sorter import ScriptSorter
from src.classes.sorter.content_sorter import ContentSorter
from src.classes.sorter.request_sorter import RequestSorter
from src.classes.reporter.report_generator import ReportGenerator


class CspGenerator(object):
    """"
    Class designed to generate CSPs for the a given domain.

    CspGenerator class is designed to handle the whole workflow of generating a
    CSP for a domain. It proceeds in 3 steps to generates CSPs for the whole
    domain :
        - It calls the spider class to generate a list of urls wich needs a csp
        - It calls the web driver to render html page and get necessary infor-
        mations to establish a CSP
        - It calls the content sorter classes to parse and scrape necessary in-
        formations such as tags and sources associated

    :param list start_url: the list of url (in string) from wich we start spide-
    ring
    :param list domain: the list of url (in string) that we are allowed to navi-
    gate to
    """

    def __init__(self, url_list, generator_id):
        self.url_list = url_list
        self.generator_id = generator_id
        # Silencing the logs
        self._silence_logs(logging.WARNING)
        self.csp_dict = dict()
        # Defining key classes to extract and sort content
        self.driver = WebDriver()
        # Make report generator
        self.report_generator = None
        # Make sorter
        self.content_sorter = ContentSorter()
        self.script_sorter = ScriptSorter()
        self.request_sorter = RequestSorter()
        # Declaring db handler
        self.db_controller = DbController(DB_FILE)
        # Put them into a list

    def renew_report_generator(self):
        """
        Sets a new ReportGenerator for a new page and link it to each resource
        sorter

        :return: None
        """
        report_generator = ReportGenerator()
        self.content_sorter.report_generator = report_generator
        self.request_sorter.report_generator = report_generator
        self.script_sorter.report_generator = report_generator
        self.report_generator = report_generator

    def generate_domain_csp(self):
        """
        Loops through the whole list of found url and generate a CSP for each
        page
        :return:
        """
        # self.generate_link_list()
        for url in self.url_list:
            self.renew_report_generator()
            self.generate_page_csp(url)

        self.db_controller.modify_generator_status(
            self.generator_id,
            1
        )

        csp_list = self.db_controller.get_all_csp(self.generator_id)
        print(csp_list)
        final_csp = Csp.aggregate_csps(csp_list)
        print(final_csp)

        self.driver.close()
        self.driver.proxy.close()

    def generate_page_csp(self, url):
        """
        Perform all the operations needed for generating a CSP for one page
        :param string url: URL of the page that is being generated a CSP
        """
        # Generate an empty CSP and parse the page
        csp = Csp()
        res = self.driver.parse_page(url)
        # Extracting HTML and HAR in order to properly sort content
        html = res[0]
        har = self.driver.proxy.har

        # Sort all the info into dictionaries of directive -> sources set
        data = self.content_sorter.run(html=html, url=url)
        self._add_data(data, csp)
        print('[x] SUCCESS ON CONTENT SORTING')
        # Sort all scripts content and directives to generate CSP
        data = self.script_sorter.run(html=html, url=url)
        self._add_data(data, csp)
        print('[x] SUCCESS ON SCRIPT SORTING')
        # Sort all scripts content and directives to generate CSP
        data = self.request_sorter.run(har=har)
        self._add_data(data, csp)
        print('[x] SUCCESS REQUEST SORTING')

        # Generate the final string of CSP
        csp.generate_csp_string()
        # Add the CSP to the CSP dictionary for the domain
        self.csp_dict[url] = csp
        print("[x] CSP generated for the url " + url)
        print(csp)

        # Running the report generator to raise flags
        self.report_generator.run(html, url)

        # Inserting flags into database
        flags = self.report_generator.flags + self.report_generator.related_flags

        csp_id = self.db_controller.get_table_max_id('flag') + 1
        self.db_controller.add_flags(flags, csp_id)

        # Inserting report into database
        print(' ---------------------------------------------')
        print(' ---     INSERTING INTO REPORT TABLE       ---')
        print(' ---------------------------------------------')

        # Inserting CSP into database
        self.db_controller.add_csp(
            self.generator_id,
            csp_id,
            url,
            csp.formatted_csp
        )

        self.db_controller.increment_processed_url(self.generator_id)

        self.report_generator.pretty_print_report()

    @staticmethod
    def _add_data(data_dict, csp):
        for directive in data_dict:
            source = data_dict[directive]
            csp.directives[directive].update(source)

    @staticmethod
    def _silence_logs(log_level):
        selenium.webdriver.remote.remote_connection.LOGGER.setLevel(log_level)
        urllib3.connectionpool.log.setLevel(log_level)
        logging.getLogger('scrapy').propagate = False
        logging.getLogger('calmjs').propagate = False
