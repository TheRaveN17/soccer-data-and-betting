''' Live crawler for unibet'''
import requests

from threading import Thread

class UnibetCrawler(Thread):

    def __init__(self, sport, database):
        super().__init__()

        self._session = requests.Session()
        self._sport = sport
        self._database = database