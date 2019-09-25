""" Implements RequestSorter class """
import mimetypes
from src.classes.sorter.abstract_sorter import AbstractSorter


class RequestSorter(AbstractSorter):
    """
    Sort the content of a HAR (HTTP Archive)

    Loop through all the request made for a given HAR and sorts all the relevant
    information such as request type to sort into the right directives. Useful
    for connect-src directive that are mostly request-based and not static
    """
    def __init__(self):
        AbstractSorter.__init__(self)
        self.mime_table = self._load_config_file('mime_table.yaml')
        self.url = ''

    def sort_content(self, **kwargs):
        self.sort_har_info(kwargs.get('har'))
        self.url = kwargs.get('url')

    def sort_har_info(self, har):
        print(har)
        # Getting entries of HAR log
        entries = har['log']['entries']
        # If the entry contains a mimeType we can translate it into a CSP direc-
        # tive
        for entry in entries:
            try:
                mime_type = entry['response']['content']['mimeType']
                mime_type = self._clean_mime_type(mime_type)
                source = entry['request']['url']
                # Retrieving the right directive for the MIME type
                directive = self.mime_table[mime_type]
                # Appending source into dictionary
                source = self.build_source(self.url, source)
                self.directives_sources[directive].add(source)
            except KeyError:
                try:
                    source = entry['request']['url']
                    guess = str(mimetypes.guess_type(source))
                    print(guess)
                    directive = self.mime_table[guess]
                    self.directives_sources[directive].add(source)
                except KeyError:
                    pass

    @staticmethod
    def _clean_mime_type(mime_type):
        res = mime_type.split(' ')[0].replace(';', '')
        return res
