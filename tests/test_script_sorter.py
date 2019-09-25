import unittest

import tinycss2
from bs4 import BeautifulSoup
from calmjs.parse import es5
from calmjs.parse.walkers import Walker
from calmjs.parse.asttypes import *

from src.classes.reporter.flag import Flag
from src.classes.model.webdriver import WebDriver
from src.classes.sorter.script_sorter import ScriptSorter
from src.classes.reporter.report_generator import ReportGenerator


class TestContentSorter(unittest.TestCase):

    def setUp(self):
        self.driver = WebDriver()
        self.test_sorter = ScriptSorter()
        self.res_sorter = ScriptSorter()

    def tearDown(self):
        self.driver.proxy.close()
        self.driver.driver.close()

    def getting_sorter_resource(self, url):
        """
        Gets html and soup associated for a given url
        :param url: url of the desired resource
        :return:
        """
        html = self.driver.parse_page(url)[0]
        soup = BeautifulSoup(html, 'html.parser')
        return html, soup

    def gen_js_style_nodes(self, node_type, styles):
        res = []
        # Parsing the node
        for style in styles:
            parsed = tinycss2.parse_rule_list(style.text)
            for node in parsed:
                if isinstance(node, tinycss2.ast.AtRule) and node.lower_at_keyword == node_type:
                    res.append(node)
        return res

    def gen_js_script_nodes(self, node_type, scripts):
        res = []
        for script in scripts:
            program = es5(script)
            walker = Walker()
            for node in walker.filter(program, lambda node: (isinstance(node, node_type))):
                res.append(node)
        return res

    def test_resolve_nested_sources(self):
        url = 'http://localhost:4000/nested_variable'
        resource = self.getting_sorter_resource(url)
        html = resource[0]
        self.test_sorter.report_generator = ReportGenerator()

        res_nested = {
            'n2': 'connect-src',
            'n7': 'connect-src'
        }
        res_variable = {
            'n1': 'http://localhost:4000/nest_connect_xmlhttp',
            'n2': 'n1',
            'n5': 'http://localhost:4000/nest_connect_socket',
            'n6': 'n5',
            'n7': 'n6',
            'n8': 'n7'
        }

        self.test_sorter.sort_content(url=url, html=html)

        assert (res_nested == self.test_sorter.nested_source
                and res_variable == self.test_sorter.variable)

    def test_parse_sources(self):
        """
        Only testing the flag for this method, rest is handled in following the
        following tests
        :return:
        """
        script = u"""
        <style>
            h1 {color:red;}
            p {color:blue;}
        </style>
        
        <script>
            alert('test'); 
        </script>
        """
        soup = BeautifulSoup(script, 'html.parser')
        script_tag = soup.find_all('script')
        style_tag = soup.find_all('style')

        # Setting up res_sorter generators and falgs
        report_generator = ReportGenerator()
        report_generator.flags.append(Flag('inline_script', script_tag[0]))
        report_generator.flags.append(Flag('inline_style', style_tag[0]))
        self.res_sorter.report_generator = report_generator
        # Setting report generator for test sorter
        self.test_sorter.report_generator = ReportGenerator()

        self.test_sorter.parse_sources(script)

        assert (self.test_sorter.report_generator.flags == self.res_sorter.report_generator.flags)

    def test_get_node_instruction(self):
        case = []
        script = u"""
            navigator.sendBeacon(dummyArg);
            navigator.serviceWorker.register(dummyArg);
            very.long.DotAcessor.dummy.serviceWorker.register(dummyArg);
            var test = funct_in_a_var(dummyArg);
            test = xhr.open(dummyArg);
            test = send(dummyArg);
        """
        program = es5(script)
        walker = Walker()
        nodes = []
        for node in walker.filter(program, lambda node: (
                isinstance(node, FunctionCall)
        )):
            nodes.append(node)
            print(type(node))

        case.append(('sendBeacon', self.test_sorter.get_node_instruction(nodes[0])))
        case.append(('register', self.test_sorter.get_node_instruction(nodes[1])))
        case.append(('register', self.test_sorter.get_node_instruction(nodes[2])))
        case.append(('funct_in_a_var', self.test_sorter.get_node_instruction(nodes[3])))
        case.append(('open', self.test_sorter.get_node_instruction(nodes[4])))
        case.append(('send', self.test_sorter.get_node_instruction(nodes[5])))

        for test_case in case:
            with self.subTest(case=test_case):
                print(test_case[0], test_case[1])
                self.assertEqual(test_case[0], test_case[1])

    def test_extract_func_call_inline_instruction(self):
        # --- ARRANGE ---
        script = u"""
            navigator.sendBeacon('http://mybeacon_to_treat.com', data);
            navigator.serviceWorker.register('https://myworker_to_treat.com'); 
            
            var connect_variable = 'http://mynestedvariable.com';
            navigator.sendBeacon(connect_variable, moreData);
            
            var bait_url = "http://should_not_be_in.com"
            open('bait_url'); 
            
        """
        # Getting all the FunctionCall nodes
        nodes = self.gen_js_script_nodes(FunctionCall, [script])
        # Setting expected results for the directives
        self.res_sorter.directives_sources['connect-src'].add('http://mybeacon_to_treat.com')
        self.res_sorter.directives_sources['worker-src'].add('https://myworker_to_treat.com')
        self.res_sorter.nested_source['connect_variable'] = 'connect-src'

        # Setting up the variable to be able to retrieve nested variable
        self.test_sorter.variable['connect_variable'] = 'http://mynestedvariable.com'

        for node in nodes:
            instruction = self.test_sorter.get_node_instruction(node)
            self.test_sorter.extract_func_call_inline_instruction(node, instruction)
        # print(self.test_sorter.directives_sources)
        # print(self.res_sorter.directives_sources)
        #
        # print(self.test_sorter.nested_source)
        # print(self.res_sorter.nested_source)
        assert (self.res_sorter.directives_sources == self.test_sorter.directives_sources)
        assert (self.res_sorter.nested_source == self.test_sorter.nested_source)

    def test_extract_func_call_eval_instruction(self):
        """
        Aims to test if eval instruction properly generate unsafe-eval directive
        and raise correct flags
        :return:
        """
        # ------------------------------- #
        # ----------- ARRANGE ----------- #
        # ------------------------------- #
        self.res_sorter.report_generator = ReportGenerator()
        self.test_sorter.report_generator = ReportGenerator()
        script = """
            eval('2*3;')
            
            var m = 3;
            var f = new Function('a', 'return a');
            
            document.getElementsByTagName("body").style.cssText = "background-color:pink;font-size:55px;border:2px dashed green;color:white;"
            myStyle.insertRule('#blanc { color: white }', 0);
        """
        # Getting the node from the script
        nodes = []
        walker = Walker()
        for node in walker.filter(es5(script), lambda node: (
                isinstance(node, FunctionCall)
        )):
            nodes.append(node)
        # Adding unsafe-eval directives for each relevant directive
        self.res_sorter.directives_sources['script-src'].add("'unsafe-eval'")
        self.res_sorter.directives_sources['style-src'].add("'unsafe-eval'")
        # Adding flag into test report generator
        flag_eval = Flag('eval_script', nodes[0])
        flag_insert_rule = Flag('eval_style', nodes[2])
        self.res_sorter.report_generator.flags.append(flag_eval)
        self.res_sorter.report_generator.flags.append(flag_insert_rule)
        # ------------------------------- #
        # ------------- ACT ------------- #
        # ------------------------------- #
        for node in nodes:
            instruction = self.test_sorter.get_node_instruction(node)
            self.test_sorter.extract_func_call_eval_instruction(node, instruction)
        # ------------------------------- #
        # ----------- ASSERT ------------ #
        # ------------------------------- #
        assert (self.res_sorter.directives_sources == self.test_sorter.directives_sources)
        assert (set(self.res_sorter.report_generator.flags) == set(self.test_sorter.report_generator.flags))

    def test_extract_var_declaration(self):
        script = """
        var ignore_this = new ('this error');
        var number_to_ignore = 555;
        
        var string = 'count me in';
        var url = 'http://test.com';
        var ref_to_url = url;
        var unreferenced_variable = not_ref;
        """

        nodes = self.gen_js_script_nodes(VarDecl, [script])
        self.res_sorter.variable['string'] = 'count me in'
        self.res_sorter.variable['url'] = 'http://test.com'
        self.res_sorter.variable['ref_to_url'] = 'url'
        self.res_sorter.variable['unreferenced_variable'] = 'not_ref'

        for node in nodes:
            self.test_sorter.extract_var_declaration(node)

        assert (self.res_sorter.variable == self.test_sorter.variable)

    def test_extract_new_expr(self):
        script = """
        // Raises unsafe-eval for script and raise flag
        var func = new Function("console.log('a');");
        
        // We suppose that a variable named original_link has already
        // been encountered to test variable nesting
        // adds original_link: connect-src to nested_sources
        nested = new Worker(original_link, test, fake, bait);
        
        // adds <http://worker.com> to worker-src
        n = new Worker("http://worker.com"); 
        
        // adds <http://shared-worker.com> to worker-src
        var share = new SharedWorker('http://shared-worker.com');
        
        // adds <wss://socket.com> to connect-src
        var socket = new WebSocket("wss://socket.com");
        
        // adds <http://test.php> to connect-src
        var event_source = new EventSource('http://test.php');
        
        // Let and const are not parsed by the library
        // let test = 1;
        """
        nodes = self.gen_js_script_nodes(NewExpr, [script])
        print(nodes)

        self.res_sorter.report_generator = ReportGenerator()
        self.res_sorter.nested_source['original_link'] = 'worker-src'
        self.res_sorter.report_generator.flags.append(Flag('eval_style', nodes[0]))
        self.res_sorter.directives_sources['script-src'].add("'unsafe-eval'")
        self.res_sorter.directives_sources['worker-src'].add('http://worker.com')
        self.res_sorter.directives_sources['worker-src'].add('http://shared-worker.com')
        self.res_sorter.directives_sources['connect-src'].add('wss://socket.com')
        self.res_sorter.directives_sources['connect-src'].add('http://test.php')

        self.test_sorter.report_generator = ReportGenerator()
        self.test_sorter.variable['original_link'] = 'http://test.lu'

        for node in nodes:
            self.test_sorter.extract_new_expr(node)

        print(self.test_sorter.nested_source)
        print(self.res_sorter.nested_source)
        assert (self.res_sorter.directives_sources == self.test_sorter.directives_sources)
        assert (self.res_sorter.nested_source == self.test_sorter.nested_source)

    def test_extract_assign(self):
        script = """
        document.getElementById("myP").style.cssText = "background-color:pink;font-size:55px;border:2px dashed green;color:white;"
        """
        self.test_sorter.report_generator = ReportGenerator()
        self.res_sorter.report_generator = ReportGenerator()

        nodes = self.gen_js_script_nodes(Assign, [script])

        self.res_sorter.directives_sources['style-src'].add("'unsafe-eval'")
        self.res_sorter.report_generator.flags.append(Flag('eval_style', nodes[0]))

        for node in nodes:
            self.test_sorter.extract_assign(node)

        print(self.test_sorter.directives_sources)
        print(self.res_sorter.directives_sources)
        assert (self.res_sorter.directives_sources == self.test_sorter.directives_sources)
        assert (self.res_sorter.report_generator.flags == self.test_sorter.report_generator.flags)

    def test_find_fontface_source(self):
        """
        Aims to test if fontface sources are resolved correctly and that no
        other elements from the inline style is included"
        :return: pass or failed in the test pipeline
        """
        # --- ARRANGE ---
        # Define the url for the sorter
        url = 'http://localhost:4000/inline_style'
        self.test_sorter.url = url
        # Getting the material
        resource = self.getting_sorter_resource(url)
        # Setting the material
        soup = resource[1]
        styles = soup.find_all('style')
        # Arrangement
        self.res_sorter.directives_sources['font-src'].add('http://myfontsite.font')
        self.res_sorter.directives_sources['font-src'].add('https://otherfontsite.lu')

        # Getting the js style nodes
        nodes = self.gen_js_style_nodes('font-face', styles)
        for node in nodes:
            self.test_sorter.find_fontface_source(node)

        assert (self.res_sorter.directives_sources == self.test_sorter.directives_sources)

    def test_find_import_source(self):
        # --- ARRANGE ---
        # Define the url for the sorter
        url = 'http://localhost:4000/inline_style'
        self.test_sorter.url = url
        # Getting the material
        resource = self.getting_sorter_resource(url)
        # Setting the material
        soup = resource[1]
        styles = soup.find_all('style')

        # Getting the js style nodes
        nodes = self.gen_js_style_nodes('import', styles)

        # Arrangement
        self.res_sorter.directives_sources['style-src'].add('http://localhost:4000/relative.css')
        self.res_sorter.directives_sources['style-src'].add('url.css')

        # Calling the method
        for node in nodes:
            self.test_sorter.find_import_source(node)

        assert (self.res_sorter.directives_sources == self.test_sorter.directives_sources)
