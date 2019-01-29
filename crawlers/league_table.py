import re
import requests

from arrow import utcnow
from bs4 import BeautifulSoup

from utils import cons
from utils import session
from utils import countries
from utils import logger

log = logger.get_logger()


class SoccerStatsCrawler(object):

    def __init__(self, country_code: str=None):
        """Initializes a crawler for www.soccerstats.com
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

        log.info('successfully initialized SoccerStats crawler object')

    @staticmethod
    def _new_session(country_code: str=None) -> requests.Session:
        """
        :return: a new requests.Session() object configured to work with https://www.soccerstats.com/
        """
        headers = {
            cons.USER_AGENT_TAG: cons.USER_AGENT_CRAWL,
            'Pragma': 'no-cache',
            'Host': 'www.soccerstats.com'
        }
        if country_code:
            ses = session.SessionFactory().build(headers=headers, proxy=True, country_code=country_code)
        else:
            ses = session.SessionFactory().build(headers=headers)
        ses.cookies.set(name='cookiesok',
                            value='no',
                            domain='www.soccerstats.com',
                            expires=utcnow().timestamp + 365 * 24 * 60 * 60)

        log.info('successfully created new session')

        return ses

    def get_leagues(self) -> list:
        """Creates a list with all leagues on www.soccerstats.com
        :return: all leagues or empty list if connection failed
        league['name'] = name of the league
        league['country'] = country of provenience
        league['url'] = url to be accessed for stats
        """
        url = 'https://www.soccerstats.com/'
        try:
            resp = self._session.get(url=url)
        except ConnectionError as err:
            log.error(err)
            log.error('problems connecting to %s\n...ABORTING...' % url)
            return []
        soup = BeautifulSoup(resp.content, 'lxml')
        pick_form = soup.find('form', {'name': 'MenuList'})
        raw_data = pick_form.find_all('optgroup')
        all_leagues = list()
        for data in raw_data:
            country = data.attrs['label']
            if country == 'Favourite leagues':
                continue
            leagues = data.find_all('option')
            for league in leagues:
                new_league = dict()
                new_league['country'] = country
                new_league['name'] = league.contents[0]
                new_league['url'] = 'https://www.soccerstats.com/' + league.attrs['value']
                all_leagues.append(new_league)

        log.info('successfully retrieved all leagues')

        return all_leagues

    def analyze_leagues(self, leagues: list) -> list:
        """Crawls all seasons and teams in each season
        :param leagues: each league a dict
        :return: data collected for leagues as dicts
        """
        for league in leagues:
            league_mpg = self._session.get(url=league['url'])
            league['seasons'] = self._get_seasons(league_mpg=league_mpg)

            for season in league['seasons']:
                season_mpg = self._session.get(url=season['url'])
                season['teams'] = self._get_teams(season_mpg=season_mpg)

        log.info('successfully retrieved all seasons and teams')

        return leagues

    @staticmethod
    def _get_seasons(league_mpg: requests.Response) -> list:
        """ Retrieves all seasons for a league
        :param league_mpg: the response of the request to this league's url
        :return: all seasons' urls to be checked for stats; first one in list is the most recent
        """
        soup = BeautifulSoup(league_mpg.content, 'lxml')
        seasons_raw = soup.find('div', {'class': 'dropdown-content'})
        seasons_raw = seasons_raw.find_all('a')

        seasons = list()
        for season_raw in seasons_raw:
            season = dict()
            season['url'] = 'https://www.soccerstats.com/' + season_raw.attrs['href']
            if 'latest' not in season['url']:
                continue
            season['year'] = season_raw.contents[0]
            seasons.append(season)

        if not seasons:
            #only current year data
            season = dict()
            season['url'] = soup.find('meta', {'property': 'og:url'}).attrs['content']
            season['year'] = cons.CURRENT_SEASON
            seasons.append(season)

        return seasons

    @staticmethod
    def _get_teams(season_mpg: requests.Response) -> list:
        """ Gets all teams that played in this season
        :param season_mpg: the response of the request to this season's url
        :return: all teams as dicts with name and url
        """
        all_teams = list()
        all_hrefs = re.findall('nbsp;<a href=\'(.*)\' target=\'_top\'>(.*)</a>', season_mpg.text)
        for href in all_hrefs:
            team = dict()
            team['name'] = href[1]
            if '.' in team['name']:  # without abbreviations is better
                continue
            if 'title' in href[0]:  # format for current season main page
                team['url'] = 'https://www.soccerstats.com/%s' % href[0].split('\' title')[0].strip()
            else:  # format for previous seasons main page
                team['url'] = href[0]
            if team not in all_teams:
                all_teams.append(team)

        return all_teams





def main():

    crawler = SoccerStatsCrawler(country_code='gb')
    leagues = crawler.get_leagues()
    crawler.analyze_leagues(leagues[21: 30])


if __name__ == '__main__':
    main()