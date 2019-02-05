import re
import json

import requests

from arrow import utcnow
from requests_futures.sessions import FuturesSession

from utils import cons
from utils import session
from utils import countries
from utils import logger

log = logger.get_logger()




class WhoScoredCrawler(object):

    def __init__(self, country_code: str=None):
        """Initializes a crawler for www.whoscored.com
        :param country_code: the country_code for the proxy if one is desired
        """
        super().__init__()

        if country_code:
            try:
                countries.get_country_name(country_code)
                self._session = self._new_session(country_code=country_code)
            except KeyError:
                log.error('bad country_code: %s' % country_code)
                raise SystemExit
        else:
            self._session = self._new_session()

        log.info('successfully initialized WhoScored crawler object')

    @staticmethod
    def _new_session(country_code: str=None) -> requests.Session:
        """
        :return: a new requests.Session() object configured to work with https://www.soccerstats.com/
        """
        headers = {
            cons.USER_AGENT_TAG: cons.USER_AGENT_CRAWL,
            'Pragma': 'no-cache',
            'Host': 'www.whoscored.com',
            'TE': 'Trailers',
            'Cache-Control': 'no-cache'
        }
        if country_code:
            ses = session.SessionFactory().build(headers=headers, proxy=True, country_code=country_code)
        else:
            ses = session.SessionFactory().build(headers=headers)

        log.info('successfully created new session')

        return ses

    @staticmethod
    def _crawl(urls: list, session: requests.Session) -> list:
        """Crawls faster using requests_futures lib
        :param urls: urls to be crawled
        :return: Response objects
        """
        future = list()
        result = list()
        ses = FuturesSession(session=session, max_workers=cons.WORKERS)

        for url in urls:
            future.append(ses.get(url=url))
        for resp in future:
            result.append(resp.result())

        return result

    def get_leagues(self) -> list:
        """Creates a list with all leagues on www.whoscored.com
        :return: all leagues or empty list if connection failed
        """
        try:
            resp = self._session.get(url=cons.WHOSCORED_URL)
        except ConnectionError as err:
            log.error(err)
            log.error('problems connecting to %s\n...ABORTING...' % cons.WHOSCORED_URL)
            return []

        resp = re.sub('\n', '', resp.content.decode('utf-8'))
        match = re.findall('var\sallRegions\s=\s(.*\]}\]);', resp)
        var = re.sub('\'', '"', match[0])
        var = re.sub('{', '{"', var)
        var = re.sub(':', '":', var)
        var = re.sub(', ', ', "', var)
        all_leagues = json.loads(var)
        log.info('successfully retrieved all leagues')

        return all_leagues





def main():

    crawler = WhoScoredCrawler(country_code='gb')
    leagues = crawler.get_leagues()


if __name__ == '__main__':
    main()