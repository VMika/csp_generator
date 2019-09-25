""" Implements ScripSorter class (inherits from AbstractSorter) """
import tinycss2
from tinycss2.ast import StringToken, URLToken

from calmjs.parse import es5
from calmjs.parse.walkers import Walker
from calmjs.parse.exceptions import ECMASyntaxError
from calmjs.parse.asttypes import (FunctionCall, VarDecl, NewExpr, Assign,
                                   DotAccessor, String, Identifier)

from bs4 import BeautifulSoup
from src.classes.reporter.flag import Flag
from src.classes.sorter.abstract_sorter import AbstractSorter


class ScriptSorter(AbstractSorter):
    """
    Class designed to generate sources for directives  that handles script calls
    and connect policy

    Performs different actions in order to properly generate the pair directive
    sources for static script tags, include of external scripts and external co-
    nnections
    """
    def __init__(self):
        AbstractSorter.__init__(self)
        # Config file loading
        self.inline_instructions = \
            self._load_config_file('inline_instructions.yaml')
        self.eval_instructions = \
            self._load_config_file('eval_instructions.yaml')
        # List for the script trees and styles
        self.trees = []
        self.styles = []
        # Aliases and variable for nested variable declarations
        self.variable = dict()
        self.nested_source = dict()
        self.url = ''

    def sort_content(self, **kwargs):
        """
        Main function for script sorter, calls all necessary methods for sorting

        :param kwargs: contains url and html parameters that correspond respec-
        tively to the url of the page and the html of the pas
        :return:
        """
        self.url = kwargs.get('url')
        # Getting inline script and style
        self.parse_sources(kwargs.get('html'))
        for tree in self.trees:
            self.find_script_sources(tree)
        for style in self.styles:
            self.extract_inline_style_source(style)
        print(self.styles)
        self.set_inline_directive()
        self.resolve_nested_sources()

    def parse_sources(self, html):
        """
        Function called to parse html

        Parses resources and prepare the resource analysis. Retrieves the script
        tags that have text (inline script) and calls another method to handle
        script includes and parses the html page (makes a soup).

        :param html: the html body of the page to parse
        :return: none
        """
        soup = BeautifulSoup(html, 'html.parser')
        scripts = soup.find_all("script")
        styles = soup.find_all("style")

        for script in scripts:
            # If it is an inline script, format it and adds it to tree list
            if script.text:
                # Submitting a flag for each script encountered
                self.submit_flag(Flag('inline_script', script))
                try:
                    self.trees.append(es5(script.text))
                except ECMASyntaxError:
                    pass
            # Else it is an include script, just extract the source directly
            else:
                self.extract_inline_script_source(script)
        # Extract the sources in inline style (fonts, style dynamic stylesheets)
        self.styles = styles
        for style in styles:
            self.submit_flag(Flag('inline_style', style))
            self.extract_inline_style_source(style)

    def extract_inline_script_source(self, script):
        """
        Extracts sources for <script> tag

        Builds the right absolute URL from the script tag and adds it into the
        right directive

        :param script: script tag to extract the source from
        :return: None
        """
        source = self.build_source(self.url, script['src'])
        self.directives_sources['script-src'].add(source)

    def find_script_sources(self, tree):
        """
        Extract all the relevant sources in <script>

        Parse all the inline scripts using their AST and extracting all relevant
        sources for CSP directives

        :param tree: a script parsed into an AST (Abstract Syntax Tree)
        :return: None
        """
        # Visit tree if a relevant node falls under a CSP directive
        walker = Walker()
        for node in walker.filter(tree, lambda node: (
                isinstance(node, (FunctionCall, VarDecl, Assign, NewExpr))
        )):
            # Calls the right function for each node
            if isinstance(node, FunctionCall):
                print('FUNCTION CALL')
                self.extract_function_call(node)

            elif isinstance(node, VarDecl):
                print('VAR DECL')
                self.extract_var_declaration(node)

            elif isinstance(node, Assign):
                print('ASSIGN')
                self.extract_assign(node)

            elif isinstance(node, NewExpr):
                print('NEW EXPR')
                self.extract_new_expr(node)

    ################################
    #   FUNCTION CALL EXTRACTION   #
    ################################

    def extract_function_call(self, node):
        """
        Extract source from a function call node

        Analyzes a function call node and checks if the call falls under a CSP
        directive and, if applicable, retrieves the source associated with the
        call

        :param node: node corresponding to a function call
        :return: None
        """
        instruction = self.get_node_instruction(node)
        # Checking if the instruction make a instruction that would require an
        # addition to a CSP directive
        if instruction in self.inline_instructions:
            self.extract_func_call_inline_instruction(node, instruction)
        elif instruction in self.eval_instructions:
            self.extract_func_call_eval_instruction(node, instruction)

    def get_node_instruction(self, node):
        # Retrieve the identifier of the function call
        instruction = node.identifier
        # If it is a DotAcessor, the instruction is the identifier
        if isinstance(instruction, DotAccessor):
            instruction = instruction.identifier
        return str(instruction)

    def extract_func_call_inline_instruction(self, node, instruction):
        for child in node.args:
            print(str(child), 'in ', self.variable, str(child) in self.variable)
            # Clean arguments URL of quotes
            child = self._clear_url(str(child))
            directive = self.inline_instructions[str(instruction)]
            # If the child is an URL and belongs to a relevant function call
            # we can add it to our directives
            if self._is_url(child):
                print(child, ' is a url')
                self.directives_sources[directive].add(str(child))
            elif str(child) in self.variable.keys():
                self.nested_source[child] = directive

    def extract_func_call_eval_instruction(self, node, instruction):
        try:
            directive = self.eval_instructions[instruction]
            self.directives_sources[directive].add("'unsafe-eval'")
            if directive == 'script-src':
                # print('SUBMITTING THIS FOR FLAG VALUE ', node.identifier)
                self.submit_flag(Flag('eval_script', node))
            elif directive == 'style-src':
                # print('SUBMITTING THIS FOR FLAG VALUE ', node.identifier)
                self.submit_flag(Flag('eval_style', node))
        except KeyError:
            pass

    ##################################
    #   VAR DECLARATION EXTRACTION   #
    ##################################
    def extract_var_declaration(self, node):
        """
        Parses a variable declaration node

        Try to find if a variable is nested and directly reference another
        variable eg :
            >>> var n = 4;
            >>> var n1 = n;
        If the value of the new variable is know at parsing time, we had it to
        the variable dictionnary with its parent.
        If a variable is the return of a function call it cannot be retrieved at
        parsing time so we do not append it eg :
            >>> var n = 'test';
            >>> var n1 = n.toUpperCase();

        :param node: variable declaration node
        :return: None
        """
        if isinstance(node.initializer, (String, Identifier)):
            self.variable[str(node.identifier)] = self._clear_url(node.initializer.value)

    ##########################
    #    EXTRACT NEW EXPR    #
    ##########################

    def extract_new_expr(self, node):
        # If it is an eval instruction simply add unsafe-eval to the right di-
        # rective
        if str(node.identifier) in self.eval_instructions:
            self.extract_new_expr_eval_instruction(node)

        # If it is an inline instruction, we have to determine the directive and
        # the source to add
        elif str(node.identifier) in self.inline_instructions:
            self.extract_new_expr_inline_instruction(node)

    def extract_new_expr_inline_instruction(self, node):
        directive = self.inline_instructions[str(node.identifier)]
        for arg in node.args:
            # Testing if it's a hard-coded name
            if isinstance(arg, String):
                candidate = self._clear_url(str(arg))
                if self._is_url(candidate):
                    self.directives_sources[directive].add(candidate)
            # Add the already encountered variable into nested_source for
            # later resolution
            elif isinstance(arg, Identifier) and str(arg) in self.variable:
                self.nested_source[str(arg)] = directive

    def extract_new_expr_eval_instruction(self, node):
        # TO DO : make the adding condition more flexible for legit use case
        # setTimeout not evil if used with built-in function for example
        directive = self.eval_instructions[str(node.identifier)]
        self.directives_sources[directive].add("'unsafe-eval'")
        # Submitting the flag according to the directive
        if directive == 'script-src':
            self.submit_flag(Flag('eval-script', node))
        elif directive == 'style-src':
            self.submit_flag(Flag('eval-style', node))

    ##################################
    #        ASSIGN EXTRACTION       #
    ##################################

    def extract_assign(self, node):
        """
        Sort assign statement into directive. Only cssText is concerned

        :param node: the Assign node
        :return: None
        """
        try:
            directive = self.eval_instructions[str(node.left.identifier)]
            print(directive)
            self.directives_sources[directive].add("'unsafe-eval'")
            self.submit_flag(Flag('eval_style', node))
        except (AttributeError, KeyError) as e:
            print(e)

    ##########################
    #      EXTRACT STYLE     #
    ##########################

    def extract_inline_style_source(self, style):
        """
        Extracts sources for an inline style tag

        Parses inline style tags in order to extract sources that are relevant
        to the style-src directive.

        :param style: style tag to extract the source from
        :return: None
        """
        parsed = tinycss2.parse_rule_list(style.text)
        for node in parsed:
            if isinstance(node, tinycss2.ast.AtRule):
                print(node, type(node))
                if node.lower_at_keyword == 'import':
                    print('import')
                    self.find_import_source(node)
                if node.lower_at_keyword == 'font-face':
                    print('font-face')
                    self.find_fontface_source(node)

    def find_import_source(self, node):
        """
        Adds the source of a CSS @import statement

        :param node: BeautifulSoup style tag
        :return: None
        """
        if isinstance(node.prelude[1], URLToken):
            self.directives_sources['style-src'].add(str(node.prelude[1].value))
        elif isinstance(node.prelude[1], StringToken):
            source = self.build_source(self.url, str(node.prelude[1].value))
            self.directives_sources['style-src'].add(source)

    def find_fontface_source(self, node):
        """
        Adds the source of a CSS @fontface statement

        Loop through the token of the statement and set a boolean to true if we
        meet the src attribute. If one of the following token is a StringToken
        or a URLToken, it must be the source of the font, so we add it to the
        font-src directive

        :param node: BeautifulSoup style tag
        :return: None
        """
        # Boolean to see when the src attribute is reached
        next_source = False
        for token in node.content:
            print("TOKEN : ", str(token))
            # Making the boolean True if we met the src attribute
            # Next StringToken or URLToken will be a source
            if isinstance(token, tinycss2.ast.IdentToken) and\
                    token.value == 'src':
                next_source = True
            # When the boolean has been triggered and the node can be a source
            elif next_source and isinstance(token, URLToken):
                print("URL TOKEN")
                self.directives_sources['font-src'].add(token.value)
            elif next_source and isinstance(token, StringToken):
                print("STRING TOKEN")
                source = self.build_source(self.url, str(token.value))
                self.directives_sources['font-src'].add(source)

    def set_inline_directive(self):
        # If at least one inline script, add the unsafe-inline directive for
        # scirpt-src
        if self.trees:
            print("UNSAFE INLINE SCRIPT")
            self.directives_sources['script-src'].add("'unsafe-inline'")
        # If at least one inline style, add the unsafe-inline directive for
        # style
        if self.styles:
            self.directives_sources['style-src'].add("'unsafe-inline'")

    def resolve_nested_sources(self):
        # Looping through all variable that aren't resolved already
        for source in self.nested_source:
            resolved = source
            # As long as there is a "parent" variable
            while self.has_parent_variable(resolved):
                resolved = self.variable[resolved]

            directive = self.nested_source[source]

            resolved = self._clear_url(resolved)
            print(directive, resolved)
            # If it's a url, we can add it in the list as resolved
            if self._is_url(resolved):
                self.directives_sources[directive].add(resolved)

    def has_parent_variable(self, node):
        try:
            return self.variable[node] is not None
        except KeyError:
            return False

    def pull_directives(self):
        self.variable = dict()
        self.nested_source = dict()
        self.styles = []
        self.trees = []
        return super().pull_directives()

    @staticmethod
    def _clear_url(url):
        res = url
        res = res.replace('"', '')
        res = res.replace("'", '')
        return res
