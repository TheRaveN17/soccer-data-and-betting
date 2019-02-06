import re
import json
import concurrent.futures as cf

from urllib import parse

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
        :return: sorted response objects
        """
        futures = list()
        unsorted_result = list()
        sorted_result = list()
        for i in range(0, len(urls)): #initialize list
            sorted_result.append(i)
        ses = FuturesSession(session=session, max_workers=cons.WORKERS)

        for i in range(0, len(urls)):
            futures.append(ses.get(url=urls[i]))
            urls[i] = urls[i].encode('utf-8')
        for future in cf.as_completed(futures):
            unsorted_result.append(future.result())

        for resp in unsorted_result:
            url = parse.unquote_to_bytes(resp.request.url)
            index = urls.index(url)
            sorted_result[index] = resp

        return sorted_result

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

    def add_data(self, leagues: list) -> list:
        """Crawls all seasons and teams in each season
        :param leagues: dicts
        :return: data collected for leagues as dicts
        """
        leagues_mp = self._crawl_leagues(leagues=leagues)
        for index in range(len(leagues)):
            leagues[index]['seasons'] = self._get_seasons(league_mpg=leagues_mp[index])

        return leagues

    def _crawl_leagues(self, leagues: list) -> list:
        """Crawls all leagues' main pages
        :param leagues: dicts
        :return: list of Response objects
        """
        leagues_urls = list()
        for league in leagues:
            leagues_urls.append(league['url'])
        try:
            leagues_mp = self._crawl(urls=leagues_urls, session=self._session)
        except Exception as err:
            log.error('failed to retrieve all leagues\' main pages')
            log.error(err)
            raise SystemExit

        log.info('successfully retrieved all leagues\' main pages')

        return leagues_mp







def main():

    crawler = WhoScoredCrawler(country_code='gb')
    leagues = crawler.get_leagues()[30:100]
    crawler.add_data(leagues=leagues)



if __name__ == '__main__':
    main()