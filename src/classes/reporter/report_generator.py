""" Class implementing ReportGenerator """

from urllib.parse import urlparse
import requests
from src.classes.reporter.flag import Flag
from src.classes.reporter.line_finder import LineFinder


class ReportGenerator(object):
    """
    Class designed to generate reports after CSP audition

    The ReportGenerator class generated report based on a list of flags issued
    by the sorter classes. Then it aggregates the data into an exploitable
    format.
    """

    def __init__(self):
        # List of flags issued by the sorters
        self.flags = list()
        # List of related flags
        self.related_flags = list()
        # Initiating line parser
        self.line_finder = LineFinder(self.flags)
        # Initiating html to empty styrin
        self.html = ''

    def run(self, html, url):
        # Calling the run method to generate the report
        print('[#] Running the report generator')
        # Setting the html page to inspect
        self.html = html
        # Getting the flag location
        self.getting_flags_locations()
        # Generating the related flags
        self.getting_related_flags(url)

    def getting_flags_locations(self):
        """
        Locates the flags in the resource

        Calls the LineFinder class in order

        :return: None
        """
        print(self.flags)
        self.line_finder.find_line(self.html)

    def getting_related_flags(self, url):
        banner = self.get_headers(url)
        if banner:
            csp_dict = banner[0]
            headers = banner[1]

            frame = self.raise_frame_option(csp_dict, headers)
            protocol = self.raise_unsafe_protocol(csp_dict, headers)
            trusted = self.raise_trusted_types(csp_dict)

            print(frame)
            print(protocol)
            print(trusted)
            print(csp_dict)

    def get_headers(self, url):
        req = requests.get(url)
        try:
            csp_header = req.headers['Content-Security-Policy']
            csp_dict = self.extracting_csp_dict(csp_header)
            return csp_dict, req.headers
        except KeyError:
            print('No CSP on this site')

    @staticmethod
    def extracting_csp_dict(header_list):
        res = {}
        header_list = header_list.split(';')
        for i in enumerate(header_list):
            header_list[i] = header_list[i].strip()
            sources = header_list[i].split(' ')
            res[sources[0]] = sources[1:]
        return res

    def generating_csp_flags(self, csp_dict):
        pass

    def raise_unsafe_protocol(self, csp_dict, url):
        if 'block-all-mixed-content' not in csp_dict.keys() and urlparse(url).scheme == 'https':
            for directive in csp_dict:
                for source in csp_dict[directive][1:]:
                    if source == 'http':
                        return Flag('possible_mixed_content')
        elif not self.lower_case_in('upgrade-insecure-requests', csp_dict):
            return Flag('no_upgrade_insecure_requests')
        return None

    def raise_frame_option(self, csp_dict, header):
        try:
            if csp_dict['frame-ancestor'].lower() not in ['none', 'self']:
                flag_id = 'permissive_frame_rule'
                return Flag(flag_id)
        except KeyError:
            pass
        if not self.lower_case_in('X-Frame-Options', csp_dict):
            flag_id = 'no_frame_rule'
        elif header['X-Frame-Options'].lower().startswith('allowall'):
            flag_id = 'permissive_frame_rule'
        elif header['X-Frame-Options'].lower().startswith('allow-from'):
            flag_id = 'permissive_frame_rule'
        else:
            flag_id = 'missing_frame_ancestors'
        return Flag(flag_id)

    def raise_trusted_types(self, csp_dict):
        if not self.lower_case_in('trusted_types', csp_dict):
            return Flag('no_trusted_types')
        return None

    def raise_missing_object(self, csp_dict):
        if not self.lower_case_in('object-src', csp_dict) and \
                csp_dict['default-src'] != 'none':
            return Flag('missing_obj_src')
        return None

    @staticmethod
    def lower_case_in(elem, dic):
        return elem.lower() in [x.lower() for x in dic.keys()]

    def pretty_print_report(self):
        print('*******************************************')
        print('*********** REPORT FOR THE PAGE ***********')
        print('*******************************************')
        if self.flags:
            for flag in self.flags:
                print('---------------------------------------------')
                print('>>> FLAGS RAISED <<<')
                print('>>> At location : ', flag.location)
                print('>>> Type : ', flag.id)
                print('>>> Explanation : ', flag.reco_dict[flag.id]['explanation'])
                if flag.content != '':
                    print('>>> Content : ', flag.content)
                else:
                    print('>>> Content : one liner tag')
                print('---------------------------------------------')
            print('*******************************************')
        else:
            print('No flags have been raised for that specific page')
            print('*******************************************')
