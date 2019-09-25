""" Implements LineFinder class """
import lxml.etree
import bs4


class LineFinder:
    """
    Class designed to determine the line of the flags submitted by sorters
    """
    def __init__(self, flags):
        self.flags = flags
        self.tags_dict = dict()

    def find_line(self, page):
        """
        Finds the line for each flag in the flag list

        Parses the whole page with lxml, find the tag associated for each
        flag and retrieve its line in the file.
        Given that the flag content can be diverse (either bs4 or tinycss
        node) we rely on building tuple that contains the three information
        necessary for testing :
            - tag name (script, style, div etc...)
            - a frozenset that contains all arguments
            this is used to keep the integrity of attributes and not having
            problems of attribute swapping that makes string to string conversion
            impossible due to attributes being sorted into dictionary and as a
            result may be unordered
            - the raw content of the tag
        :param page: a string containing the whole html file
        :return: None
        """
        print(page)
        tree = lxml.html.fromstring(page)
        # offset = [elem for elem in tree.xpath('/html')]
        # print(len(offset))
        # print(offset[0].sourceline)
        # print(offset[0].expat)
        # Getting all the tags in the document
        tags = [elem for elem in tree.xpath('//*')]
        print(tags[0].sourceline)
        unresolved_flags = []

        for tag in tags:
            # Enforcing the content of the node to at least empty instead of
            # None to keep the tag from autoclosing
            if tag.text is None:
                tag.text = ''
            # Building a tuple to identify the tag
            elem_tuple = self._make_lxml_tag_tuple(tag)
            # Determining the lines for all the tags
            self.tags_dict[elem_tuple] = tag.sourceline

        # Looping through the flags
        for flag in self.flags:
            # If it's a bs4 Tag build the comparison tuple
            if isinstance(flag.content, bs4.Tag):
                flag_tuple = self._make_bs_tag_tuple(flag.content)
                # Offset (given Doctype delcaration and html tag is excluded)
                flag.location = self.tags_dict[flag_tuple] + 2
            # Else adds the flag into the unresolved flag list
            else:
                unresolved_flags.append(flag)

        # If flags are left unresolved calling the method to resolve flags that
        # are issued by eval statement
        for flag in unresolved_flags:
            self.resolve_eval_flags(flag, page)

    @staticmethod
    def resolve_eval_flags(flag, page):
        """
        Resolves all the line number of flags that could not be resolved previ-
        ously. They are eval flags raised by tinycss (the javascirpt parser)
        that are not tags but js instructions. To find the of these instructions
        it parses the page line by line.

        :param flag: the unresolved flag
        :param page: the page to search from
        :return: None
        """
        # print('Resolving  eval flags')
        split_lines = page.split('\n')
        for index, line in enumerate(split_lines):
            if line.strip() == str(flag.content) + ';':
                # Offset (given Doctype delcaration and html tag is excluded
                # and the tag is embed into script/style tag)
                flag.location = index + 3

    @staticmethod
    def _make_lxml_tag_tuple(elem):
        """
        Makes the comparison tuple for a given lxml tag element

        :param elem: element that we need the tuple of
        :return: tuple (tag_name, tag_attrs, tag_content)
        """
        elem_list = []
        elem_list.append(elem.tag)
        elem_list.append(frozenset(elem.attrib))
        elem_list.append(elem.text.strip())
        res = tuple(elem_list)
        return res

    @staticmethod
    def _make_bs_tag_tuple(elem):
        """
        Makes the comparison tuple for a given bs4 tag element

        :param elem: element that we need the tuple of
        :return: tuple (tag_name, tag_attrs, tag_content)
        """
        elem_list = [elem.name, frozenset(elem.attrs), elem.text.strip()]
        res = tuple(elem_list)
        return res
