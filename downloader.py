import requests
from bs4 import BeautifulSoup
import sqlite3
import logging
from dao import DAO

logger = logging.getLogger(__name__)

### Helper method for method download ###
def extract_urls(seed, session):
    """ Extract urls
    """
    htmltext = session.get(seed).text
    soup = BeautifulSoup(htmltext, 'html.parser')
    return soup.find_all('a')

def process_name(raw, ext):
    """ generate proper name
    """
    raw = raw.replace('/', ' and ').replace(' ', '_')
    return raw + ext

def pdf_filter(ahref, urls, url_names):
    """ add url and url_name if ahref is pdf
    """
    url = ahref['href']
    if url.endswith(".pdf"):
        urls.append(url)
        name = ahref.div.text
        url_names.append(process_name(name, ".pdf"))
        
def mp4_filter(ahref, urls, url_names):
    """ add url and url_name if ahref is mp4
    """
    href_type = ahref['title'].lower()
    if "mp4" in href_type:
        url = ahref['href']
        name = ahref.div.text
        urls.append(url)
        url_names.append(process_name(name, ".mp4"))

### End of helper method for download

### dispatch method command

def url_phase(urls, url_names, dao):
    """ Store urls in db
    """
    logger.info("URL phase begin.")
    dao.createTable()
    dao.addURLs(url_names, urls)
    
def download_phase(item_num, dao, session):
    """ Fetch Entry with empty data column and download the resource
    """
    logger.info("Download phase begin.")
    ids, urls = dao.fetchEmpty(item_num)
    for id, url in zip(ids, urls):
        logger.info("Downloading ... from {}".format(url))
        data = session.get(url).content
        logger.info("Successfully downloadeed for {}".format(url))
        dao.addResources(id, data)

def dump_phase(dump_loc, dao):
    """ Dump resource into local file systems
    """
    logger.info("Dump phase begin.")
    dao.dumpResource(dump_loc)
 
def cleanup_phase(dao):
    """ Drop the table in db
    """
    logger.info("Clean up phase begin")
    dao.dropTable()

### dispatch method end

def download(seed, name, filter, dump, action, item_num, session):
    """ Download function
    Parameters
    ----------
    seed: str
          The Course Main URL
    name: str
          The task name, also for DB table, and dump file_name
    filter: list[str]
          The resource type, currently only mp4 and pdf is available
    dump: str
          The base dump location for dump operation
    action: str 
          The State parameter for operation guide.
          launch, download, dump, cleanup
    iter_num:  int
          The amount of items should be downloaded.
          The default is -1 which means for all material available in DB
    session: requests.Session
          The session object to perform download action.
    """

    # command dispatch
    command_dict = {"dump" : ["url_phase", "download_phase", "dump_phase"],
                    "download" : ["url_phase", "download_phase"],
                    "launch" : ["url_phase"],
                    "cleanup" : ["cleanup_phase"]
                   } 

    # resolve filter
    filter_action = {"pdf" : pdf_filter,
                   "mp4" : mp4_filter
                  }

    # extract urls
    logger.info("Extracting URLS ... ")
    ahrefs = extract_urls(seed, session)

    # filter urls
    logger.info("Pattern are {}".format(filter))
 
    urls = []
    url_names = []
  
    logger.info("Generating target urls ... ")
    for each_a in ahrefs:
        """Filter strategy : 
            filter pdf: fetch the url endswith ".pdf"
            filter mp4: fetch the href_tpye contains mp4   
        """
        # filter the link with title
        if not 'title' in each_a.attrs:
            continue
        # do the filter action
        for marker in filter:
             call_method = filter_action[marker]
             call_method(each_a, urls, url_names)

    # release memory
    ahrefs = [] 

    # generate DAO
    logger.info(" Connecting DB.")
    dbname = './db/' + name + '.db'
    conn = sqlite3.connect(dbname)
    mydao = DAO(name, conn)
 
    # Perform action
    commands = command_dict[action]
    logger.info(" Commands are : {}".format(commands))
    for command in commands:
        if command == "url_phase":
            url_phase(urls, url_names, mydao)
        elif command == "download_phase":
            download_phase(item_num, mydao, session)
        elif command == "dump_phase":
            dump_phase(dump, mydao)
        else:
            cleanup_phase(mydao)
   
    if conn:
        logger.info("Closing the db.")
        conn.close()
    logger.info('Action Done.')


