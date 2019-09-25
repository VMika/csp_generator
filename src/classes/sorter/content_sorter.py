""" Implements ContentSorter class (inherits from AbstractSorter) """

from bs4 import BeautifulSoup
from src.classes.sorter.abstract_sorter import AbstractSorter
from src.classes.reporter.flag import Flag


class ContentSorter(AbstractSorter):
    """
    Class designed to scrap and extract page information used to generate pair
    of directive/source for a CSP

    Scraps all the information about a page and the requests it has made. It
    relies on several configuration files to generate the sources for
    static tags directives (<img src ''> into img-src directive etc) and sort
    links tag into the right directives.
    """

    def __init__(self):
        AbstractSorter.__init__(self)
        self.mime_table = self._load_config_file('mime_table.yaml')
        self.simple_tag = self._load_config_file('simple_tag_table.yaml')
        self.link_tag = self._load_config_file('link_tag_table.yaml')
        self.inline_event = self._load_config_file('inline_event.yaml')
        self.report_generator = None
        self.soup = ''
        self.url = ''

    def sort_content(self, **kwargs):
        self.url = kwargs.get('url')
        self.soup = BeautifulSoup(kwargs.get('html'), 'html.parser')
        self.sort_regular_tag_info()
        self.sort_link_tag_info()
        self.add_inline_directives()
        self.add_sandbox_directive()

    def sort_regular_tag_info(self):
        """
        Sorts regular tags into the right directives

        Parses all tags into the right directives
        :return: None
        """
        # Looping through simple_tag list
        for tag_type in self.simple_tag:
            # Getting all tags
            tag_list = self.soup.find_all(tag_type)
            for tag in tag_list:
                self.extract_simple_tag_source(tag, tag_type)

    def extract_simple_tag_source(self, tag, tag_type):
        for attr in tag.attrs:
            if "javascript:" in tag.attrs[attr]:
                self.directives_sources['script-src'].add("'unsafe-inline'")
                self.submit_flag(Flag('inline_javascript', tag))
        try:
            # Retrieving the source
            source = tag[self.simple_tag[tag_type][0]]
            if source:
                # Determining the directive the source belongs to
                directive = self.simple_tag[tag_type][1]
                # Building the source before adding it to directive
                source = self.build_source(
                    self.url,
                    source
                )
                print('The source of the resource is : ', source)
                # Adding the source
                self.directives_sources[directive].add(source)
        except KeyError:
            pass

    def sort_link_tag_info(self):
        """
        Sorts link tag into the right directives

        Parses the rel attribute of each link and retrieves the right directive
        for the tag
        :return: None
        """
        # Parsing all links
        link_list = self.soup.find_all('link')
        print(link_list)
        for tag in link_list:
            # Checking if link tag got 'rel' attribute
            if tag.attrs['rel'][0]:
                rel = tag.attrs['rel'][0]
                try:
                    directive = self.link_tag[rel][1]
                    if self.is_javascript_protocol(tag.attrs[self.link_tag[rel][0]]):
                        self.directives_sources[directive].add("'unsafe-inline'")
                        self.submit_flag(Flag('inline_javascript', tag))
                    # Retrieving the right directive for the source of the tag
                    # Building the source
                    else:
                        source = self.build_source(
                            self.url,
                            tag.attrs[self.link_tag[rel][0]]
                        )
                        # Adding the source to a directive
                        self.directives_sources[directive].add(source)
                except KeyError:
                    pass

    def add_inline_directives(self):
        """
        Adds unsafe-inline directives for script-src and style-src

        Checks if a tag has a style attribute and if a script tags have no inte-
        grity attribute. In these cases, add unsafe-inline into the right direc-
        tives to keep integrity of the page

        :return: None
        """
        # Checking if a tag got a style attribute, if it does, add unsafe-inline
        # into the style directive
        if self.soup.find_all(style=True):
            self.directives_sources['style-src'].add("'unsafe-inline'")

        # Retrieving all the script tag
        inline_script = self.soup.find_all(
            lambda tag: any(
                attr in self.inline_event for attr in tag.attrs.keys()))
        # Checking if script tag are safe by checking presence of integrity a-
        # ttribute
        if inline_script:
            for script in inline_script:
                if not script.has_attr('integrity') or not script.has_attr('nonce'):
                    self.submit_flag(Flag('inline_event', script))
                    self.directives_sources['script-src'].add("'unsafe-inline'")

    def add_sandbox_directive(self):
        """
        Adds directive for sandbox src if an iframe is sandboxed.

        Given that we use a dictionary of tag -> source_attribute to determine
        the directive and source associated with a tag we can't retrieve both
        src value and sandbox value so we retrieve the later in this method.

        :return: None
        """
        iframe = self.soup.find_all(sandbox=True)
        for frame in iframe:
            print(frame)
            for value in frame['sandbox']:
                self.directives_sources['sandbox'].add(value)

    @staticmethod
    def is_javascript_protocol(source):
        protocols = [
            'javascript:',
            'jscript:',
            'livescript:',
            'vbscript:',
            'data:',
            'about:',
            'mocha:'
        ]
        for protocol in protocols:
            if protocol in source:
                return True
        return False
