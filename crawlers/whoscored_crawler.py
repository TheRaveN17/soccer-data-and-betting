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
        """Creates a list with all leagues on whoscored.com
        league['type'] = 1 if Regional, 0 if National level
        league['id'] = identification number for whoscored.com -> int
        league['flag'] = identification flag for whoscored.com -> str
        league['region'] = name of country or region of provenience
        league['name'] = name
        league['url'] = main page
        :return: all leagues or empty list if connection failed
        """
        try:
            resp = self._session.get(url=cons.WHOSCORED_URL)
        except ConnectionError:
            log.error('problems connecting to %s\n...ABORTING...' % cons.WHOSCORED_URL)
            return []

        resp = re.sub('\n', '', resp.content.decode('utf-8'))
        match = re.findall('var\sallRegions\s=\s(.*\]}\]);', resp)
        var = re.sub('\'', '"', match[0])
        var = re.sub('{', '{"', var)
        var = re.sub(':', '":', var)
        var = re.sub(', ', ', "', var)
        regions = json.loads(var)

        leagues = list()
        for region in regions:
            for tournament in region['tournaments']:
                league = dict()
                league['id'] = tournament['id']
                league['url'] = cons.WHOSCORED_URL + tournament['url'][1:]
                league['name'] = tournament['name'] if tournament['name'] else 'Name not provided. plly coupe'
                league['region'] = region['name']
                league['flag'] = region['flg']
                league['type'] = region['type']
                leagues.append(league)
                continue

        log.info('successfully retrieved all leagues')

        return leagues





def main():

    crawler = WhoScoredCrawler(country_code='gb')
    leagues = crawler.get_leagues()


if __name__ == '__main__':
    main()