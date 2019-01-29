import re
import requests

from arrow import utcnow
from bs4 import BeautifulSoup

from utils import cons
from utils import session


class SoccerStatsCrawler(object):

    def __init__(self):

        super().__init__()

        self._session = self._new_session()

    @staticmethod
    def _new_session() -> requests.Session:
        """
        :return: a new requests.Session() object configured to work with https://www.soccerstats.com/
        """

        headers = {
            cons.USER_AGENT_TAG: cons.USER_AGENT_CRAWL,
            'Pragma': 'no-cache',
            'Host': 'www.soccerstats.com'
        }
        ses = session.SessionFactory().build(headers=headers)
        ses.cookies.set(name='cookiesok',
                            value='no',
                            domain='www.soccerstats.com',
                            expires=utcnow().timestamp + 365 * 24 * 60 * 60)

        return ses

    def get_leagues(self) -> list:
        """
        :return: all leagues
        league['name'] = name of the league
        league['country'] = country of provenience
        league['url'] = url to be accessed for stats
        """

        url = 'https://www.soccerstats.com/'
        resp = self._session.get(url=url)
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

        return all_leagues

    def analyze_leagues(self, leagues: list) -> list:
        """
        :param leagues: each league a dict
        :return: data collected for leagues as dicts
        """

        for league in leagues:
            league_mpg = self._session.get(url=league['url'])
            league['seasons'] = self._get_seasons(league_mpg=league_mpg)

            for season in league['seasons']:
                season_mpg = self._session.get(url=season)
                league[season]['teams_urls'] = self._get_teams(season_mpg=season_mpg)

        return leagues

    @staticmethod
    def _get_seasons(league_mpg: requests.Response) -> list:
        """
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
            season['name'] = season_raw.attrs['href']
            seasons.append(season)

        if not seasons:
            #only current year data
            season = dict()
            season['url'] = soup.find('meta', {'property': 'og:url'}).attrs['content']
            seasons.append(season)


        return seasons

    @staticmethod
    def _get_teams(season_mpg: requests.Response) -> list:
        """
        :param league_mpg: the response of the request to this league's url
        :return: all links to all teams' stats from league
        """

        all_hrefs = re.findall('&nbsp;<a href=\'(.*)\' title=', season_mpg.text)
        teams_urls = set()
        for href in all_hrefs:
            teams_urls.add('https://www.soccerstats.com/' + href)

        return list(teams_urls)





def main():

    crawler = SoccerStatsCrawler()
    leagues = crawler.get_leagues()
    crawler.analyze_leagues(leagues[28: 30])


if __name__ == '__main__':
    main()