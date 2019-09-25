""" Implements CSP class """

from urllib.parse import urljoin, urlparse
import yaml
from config import ROOT_DIR


class Csp:
    """
    Model class to encapsulate a CSP.

    Data is stored in a dictionary : keys are directives and items are strings
    corresponding to CSP sources

    :param str name: CSP name, corresponding to the URL
    """

    def __init__(self, config_file=None):
        self.directives = dict()
        self.formatted_csp = ''
        if config_file:
            self.generate_directive_keys(config_file)
        else:
            path = str(ROOT_DIR / 'src' / 'config' / 'directives_list.yaml')
            self.generate_directive_keys(path)

    def generate_directive_keys(self, config_file):
        """Generates empty CSP from configuration file
        :param str config_file: path of the directives config file
        """
        with open(config_file, 'r') as stream:
            data = yaml.safe_load(stream)
        for directive in data:
            self.directives[directive] = set()

    @staticmethod
    def aggregate_csps(csp_data):
        """Merge all csp from raw database data into one csp. Proceeds to clean
        :param csp_data:
        :return:
        """
        # Building directive and sources from raw data
        csp_list = [x[3] for x in csp_data]
        dicts = Csp.build_csp_dicts(csp_list)
        dicts = Csp.merge_csp_dicts(dicts)
        # Creating new CSP with associated directives and sources
        csp = Csp()
        csp.directives = dicts

        return csp

    @staticmethod
    def build_csp_dicts(csp_list):
        """
        Build csp dictionary (directives -> sources) from raw database values
        :param csp_list: list of raw csp from the database
        :return:
        """
        res = []
        for csp in csp_list:
            csp_dict = dict()
            print(csp)
            split = csp.strip()
            print(split)
            split = split.split(';')
            for directive in split:
                # print(directive)
                try:
                    directive = directive.strip()
                    directive = directive.split()
                    csp_dict[directive[0]] = set(directive[1:])
                except IndexError:
                    pass
            res.append(csp_dict)
        return res

    @staticmethod
    def merge_csp_dicts(csp_dicts):
        try:
            res = csp_dicts[0]
        except IndexError:
            return {}
        for csp_dict in csp_dicts:
            for directive in csp_dict:
                for source in csp_dict[directive]:
                    try:
                        res[directive].add(source)
                    except KeyError:
                        pass

        return Csp.remove_none_directives(res)

    @staticmethod
    def remove_none_directives(csp_dict):
        for directive in csp_dict:
            if len(csp_dict[directive]) != 1:
                try:
                    csp_dict[directive].remove("'none'")
                except KeyError:
                    print('none not present')
        return csp_dict

    def clean_merged_csp_dict(self):
        self.factorize_sources()
        self.clean_none_values()

    def simplify_self_sources(self, start_url):
        for directive in self.directives:
            to_remove = set()
            for source in self.directives[directive]:
                # Comparing if sources matches with self value ie the start_url
                print(start_url)
                source_hostname = urlparse(source).hostname
                start_url_hostname = urlparse(start_url).hostname
                if source_hostname == start_url_hostname and source_hostname:
                    to_remove.add(source)
            # If there is at least one item we can simplify, remove it and add
            # self
            if to_remove:
                print("To remove : ", to_remove)
                # Removing the sources that matched the self url
                self.directives[directive] = \
                    self.directives[directive].difference(to_remove)
                # Adding self
                self.directives[directive].add("'self'")

    def factorize_sources(self):
        for directive in self.directives:
            # Building dictionary about
            dictionaries = self.build_occurrence_dictionaries(directive)
            origin_dict = dictionaries[0]
            res_dict = dictionaries[1]

            # Retrieving the source that can be simplified and replacing them
            for source in origin_dict:
                print(origin_dict)
                simplified = origin_dict[source]

                # If it does appear more than one time it can get simplified
                if res_dict[simplified] > 1:
                    print('To remove : ', source)
                    print('From dict : ', self.directives[directive])
                    # Building simplified source
                    # Then removing orignal source
                    # Finally add simplified source
                    simplified = urljoin(source, simplified)
                    self.directives[directive].remove(source)
                    print("Removed ", source)
                    self.directives[directive].add(simplified)
                    print("Added ", simplified)

    def build_occurrence_dictionaries(self, directive):
        origin_dict = {}
        res_dict = {}
        for source in self.directives[directive]:
            path = urlparse(source).path
            # Getting the path without the last particule
            # Only if it nested into directories
            stripped_source = path.split('/')[:-1]
            if len(stripped_source) > 1:
                stripped_source = '/'.join(stripped_source)
                # Keeping track of the full source
                origin_dict[source] = stripped_source
                # Counting occurences to see if source simplification is
                # possible
                if stripped_source in res_dict:
                    res_dict[stripped_source] += 1
                else:
                    res_dict[stripped_source] = 1
        return origin_dict, res_dict

    def clean_none_values(self):
        for directive in self.directives:
            for source_set in directive:
                if len(source_set) > 1:
                    try:
                        source_set.remove("'none'")
                    except KeyError:
                        pass

    def generate_csp_string(self):
        """Generates final CSP string, ready to be sent in header"""
        res = ''
        for directive in self.directives:
            if self.directives[directive]:
                res += directive + ' ' + ' '.join(self.directives[directive])
                res += '; '
            else:
                res += directive + " 'none'; "
        self.formatted_csp = res

    def __repr__(self):
        return self.formatted_csp
