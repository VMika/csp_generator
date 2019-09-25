"""
A Flask web app that scrapes http://quotes.toscrape.com using Scrapy and Twisted.
To run this app, run it directly:

    python flask_twisted.py

Alternatively, use Twisted's `twist` executable. This assumes you're in the directory where the
source files are located:

    PYTHONPATH=$(pwd) twist web --wsgi flask_twisted.app --port tcp:9000:interface=0.0.0.0

"""

import sys
import os

sys.path.append(os.getcwd())

from flask import Flask
from flask import request
from flask import redirect, url_for, jsonify
from config import DB_FILE
from tornado.template import Loader
from twisted.internet.threads import deferToThread

from src.classes.model.csp import Csp
from src.classes.model.crawler import Crawler
from src.classes.db.db_controller import DbController
from src.classes.model.csp_generator import CspGenerator
from src.classes.model.url_crawler_runner import UrlCrawlerRunner

template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
static_url_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

app = Flask('Scrape With Flask', static_folder=static_url_path)
app.debug = True

db = DbController(DB_FILE)
template_loader = Loader(template_dir)


@app.route('/')
@app.route('/home')
def generate():
    return template_loader.load('generator.html').generate()


@app.route('/crawl_url', methods=['POST'])
def crawl_url():
    """
    Scrapes all URL
    """
    global db
    gen_id = db.get_table_max_id('generator') + 1
    print("TEST GEN ID")
    print(gen_id)
    # Getting the content of the request form
    result = request.form
    # Getting raw parameters
    start_url = result['start_url']
    allowed_domain = result['allowed_domain']
    links = set()
    # Adding generator to db with correct parameter
    db.add_generator(gen_id, start_url, allowed_domain, 0)

    # Starting the crawler and add the appropriate callback
    eventual = UrlCrawlerRunner()
    defer = eventual.crawl(
        Crawler,
        # Adding list casting since scrapy spider needs lists
        start_urls=[start_url],
        allowed_domains=[allowed_domain],
        links=links,
        gen_id=gen_id
    )
    # When crawling is done, insert all data in database
    defer.addCallback(process_data, (links, gen_id))
    # Redirect to the result page
    return redirect(url_for('report', generator_id=gen_id))


@app.route('/data/<generator_id>')
def data(generator_id):
    return jsonify(build_res_dict(generator_id))


@app.route('/report')
def report_list():
    global db
    report_list = db.get_all_generator()
    print(report_list)
    tr_class = ["colId", "colStart", "colDomain", "colReport"]
    return template_loader.load('report_list.html').generate(
        report_list=report_list,
        tr_class=tr_class
    )


@app.route('/report/<generator_id>')
def report(generator_id):
    """
    Route to get the results of a given generator (session). Display status page
    if the crawling is not done.
    """
    global db
    status = db.get_generator_status(generator_id)
    print(len(status))
    if len(status) == 1:
        status_code = status[0]
        if status_code == 0:
            progress = db.get_generator_progress(generator_id)
            if progress:
                return template_loader.load('progress.html').generate()
            else:
                return template_loader.load('progress.html').generate()
        else:
            db.clean_generator_progress(generator_id)
            return template_loader.load('report.html').generate()

    else:
        return "No report found"


@app.route('/status/<generator_id>')
def status(generator_id):
    global db
    progress = db.get_generator_progress(generator_id)
    res = dict()
    try:
        res['url_crawled'] = progress[0]
        res['url_total'] = progress[1]
        return jsonify(res)
    except TypeError:
        tmp_dict = dict()
        tmp_dict['crawling'] = True
        return jsonify(tmp_dict)


def process_data(request, data):
    """
    Method called when the CrawlerRunner is done. Insert all links in database
    and call the CSP generator to generate CSP from crawled url.

    :param request: dummy first arg of the callback, needed to pass actual data
    in the second param
    :param data; the link_list and generator id for the crawn
    """
    link_list = data[0]
    generator_id = data[1]

    # For each link add crawler
    for link in link_list:
        db.add_crawled_url(generator_id, link)
        print('link added')

    # Make the csp generator call in another thread in order to get non blocking
    # operations
    deferToThread(call_csp_generator, link_list, generator_id)


def call_csp_generator(link_list, generator_id):
    """
    Instanciate CSP generator and run the main program to run the CSP
    :param link_list: the domain link list
    :param generator_id: id of the generation
    :return: None
    """
    csp_generator = CspGenerator(link_list, generator_id)
    db.add_generator_progress(generator_id, len(link_list))
    csp_generator.generate_domain_csp()


def build_res_dict(generator_id):
    """
    Build the dictionnary that will contain the four possibilities for CSP and
    the data needed to view the results
    :param generator_id: id of the generation
    :return: dictionary containing four versions of CSP and configuraiton infor-
    mations needed for the program to work
    """
    res_dict = dict()
    csp_list = db.get_all_csp(generator_id)
    url = db.get_generator_by_id(generator_id)[1]
    print()
    print('URL FED TO SIMPLIFY SELF', url)

    # Getting base csp from database entry
    csp = Csp.aggregate_csps(csp_list)

    res_dict['header'] = dict()
    # Raw csp, no simplification
    csp_raw = csp.directives.copy()
    csp.generate_csp_string()
    res_dict['csp-raw'] = csp_raw
    res_dict['header']['raw'] = csp.formatted_csp

    # Simplifying the csp by facotrizing sources
    csp = Csp.aggregate_csps(csp_list)
    csp.factorize_sources()
    csp.generate_csp_string()
    csp_directory_simplified = csp.directives
    res_dict['csp-directory-simplified'] = csp_directory_simplified
    res_dict['header']['directory-simplified'] = csp.formatted_csp

    # Getting a new virgin copy of base csp to apply another transformation
    csp = Csp.aggregate_csps(csp_list)
    # Simplifying only by self sources
    csp.simplify_self_sources(url)
    csp.generate_csp_string()
    csp_self_simplified = csp.directives
    res_dict['csp-self-simplified'] = csp_self_simplified
    res_dict['header']['self-simplified'] = csp.formatted_csp
    # Getting a fully simplified version by simplifying sources on a csp already
    # simplified by self sources
    csp = Csp.aggregate_csps(csp_list)
    csp.simplify_self_sources(url)
    csp.factorize_sources()
    csp.generate_csp_string()
    csp_fully_simplified = csp.directives
    res_dict['csp-fully-simplified'] = csp_fully_simplified
    res_dict['header']['fully-simplified'] = csp.formatted_csp

    flags = db.get_flags_from_generator(generator_id)
    flag_list = build_flag_dict(flags)

    data = db.get_generator_by_id(generator_id)

    res_dict['flags'] = flag_list
    res_dict['start_url'] = data[1]
    res_dict['allowed_domain'] = data[2]

    make_csp_directives_json_ready([csp_raw,
                                    csp_self_simplified,
                                    csp_directory_simplified,
                                    csp_fully_simplified])

    return res_dict


def make_csp_directives_json_ready(csp_directives_list):
    """
    Converts mulitple csp dictionnary into csp lists
    :param csp_directives_list:
    :return:
    """
    for csp_directives in csp_directives_list:
        for key in csp_directives:
            csp_directives[key] = list(csp_directives[key])


def build_flag_dict(flags):
    """
    Build data for flags
    :param flags: list of flags from db
    :return: dictionary containing flag data
    """
    res = []
    for flag in flags:
        flag_dict = dict()
        flag_dict['url'] = flag[0]
        flag_dict['content'] = flag[1]
        flag_dict['flag_info_id'] = flag[2]
        flag_dict['location'] = flag[3]
        flag_dict['reco'] = flag[4]
        flag_dict['explanation'] = flag[5]
        flag_dict['description'] = flag[6]
        res.append(flag_dict)
    return res


if __name__ == '__main__':
    from sys import stdout

    from twisted.logger import globalLogBeginner, textFileLogObserver
    from twisted.web import server, wsgi
    from twisted.internet import endpoints, reactor

    # start the logger
    globalLogBeginner.beginLoggingTo([textFileLogObserver(stdout)])

    # start the WSGI server
    root_resource = wsgi.WSGIResource(reactor, reactor.getThreadPool(), app)
    factory = server.Site(root_resource)
    http_server = endpoints.TCP4ServerEndpoint(reactor, 9000)
    http_server.listen(factory)

    # start event loop
    reactor.run()
