''' Live crawler for unibet'''
import requests

class UnibetCrawler(object):

    def __init__(self):

        self._session = requests.Session()