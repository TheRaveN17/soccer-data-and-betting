import requests
import re

from arrow import utcnow
from bs4 import BeautifulSoup


class SoccerStatsCrawler(object):

    def __init__(self):

        super().__init__()

        self._session = self._new_session()

    @staticmethod
    def _new_session():
        """
        :return: a new requests.Session() object configured to work with https://www.soccerstats.com/
        """

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:64.0) Gecko/20100101 Firefox/64.0',
            'Pragma': 'no-cache',
            'Host': 'www.soccerstats.com'
        }
        session = requests.Session()
        session.headers.update(headers)
        session.cookies.set(name='cookiesok',
                            value='no',
                            domain='www.soccerstats.com',
                            expires=utcnow().timestamp + 365 * 24 * 60 * 60)

        return session

    def get_league_data(self, league: dict) -> dict:
        """
        :return: all links to all teams' stats from present league
        """

        resp = self._session.get(url=league['url'])

        all_hrefs = re.findall('&nbsp;<a href=\'(.*)\' title=', resp.text)
        teams_urls = set()
        for href in all_hrefs:
            teams_urls.add('https://www.soccerstats.com/' + href)
        league['teams'] = list(teams_urls)

        return league

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







def main():

    crawler = SoccerStatsCrawler()
    leagues = crawler.get_leagues()
    crawler.get_league_data(leagues[8])


if __name__ == '__main__':
    main()