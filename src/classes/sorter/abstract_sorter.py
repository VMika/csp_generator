""" Implements abstract class AbstractSorter"""
import urllib
import yaml

from config import ROOT_DIR


class AbstractSorter(object):
    """
    Abstract class for sorters

    Designed to be a template for sorters. Calling the method run invokes the
    sort content method and call pull_directives to return the directives of the
    sorter.
    """
    def __init__(self, path='../config/'):
        self.path = path
        self.directives_sources = self.build_empty_directive_dict()
        self.report_generator = None

    def run(self, **kwargs):
        self.sort_content(**kwargs)
        return self.pull_directives()

    def sort_content(self, **kwargs):
        """
        Method to override that sorts the necessary content
        :return: None
        """
        pass

    def pull_directives(self):
        """
        Returns the content of the sorter

        Returns the source dictionary of the corresponding sorter and resets the
        directives sources dictionnary to be ready to parse another page

        :return: The dictionary of directives of the corresponding sorter
        """
        dic = self.directives_sources
        self.directives_sources = self.build_empty_directive_dict()
        return dic

    def build_empty_directive_dict(self):
        """
        Builds empty directive dictionary

        Builds a dictionary of directive based on the directives_list.yaml con-
        figuration file
        :return: Dictionary, a dictionary of empty directives
        """
        config = self._load_config_file('directives_list.yaml')
        res = dict()
        for directive in config:
            res[directive] = set()
        return res

    def build_source(self, url, source, base=''):
        """
        Build a source from a URL and a particule

        Checks the shape of the source to properly format it (eg : '//myjs.js'
        is not a valid source and need to be prefixed with https or http to be
        valid

        :param url string: the provenance URL of the source
        :param source string:
        :param base string: if specified, the base url inside the <base> tag of
        the page

        :return: String, the url of the source
        """
        if self._is_url(source):
            return source
        if base:
            return urllib.parse.urljoin(base, source)
        return urllib.parse.urljoin(url, source)

    def submit_flag(self, flag):
        """
        Submits a flag to the report generator

        :param flag: a flag object describing an issue in the generated CSP
        :return: None
        """
        self.report_generator.flags.append(flag)

    @staticmethod
    def _load_config_file(config_file):
        """
        Loads a yaml config file
        :param config_file: name of the file in the config folder
        :return: a stream of the config file
        """
        stream = open(str(ROOT_DIR/'src'/'config'/config_file))
        file = yaml.safe_load(stream)
        stream.close()
        return file

    @staticmethod
    def _is_url(url, qualifying=None):
        min_attributes = ('scheme', 'netloc')
        qualifying = min_attributes if qualifying is None else qualifying
        token = urllib.parse.urlparse(url)
        return all([getattr(token, qualifying_attr)
                    for qualifying_attr in qualifying])
