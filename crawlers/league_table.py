import requests
import re

from arrow import utcnow



class SoccerStatsCrawler(object):

    def __init__(self):

        super().__init__()

        self._session = self._new_session()
        self._league = 'england'

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

    def get_teams_url(self):
        """
        :return: all links to all teams' stats from present league
        """

        url = 'https://www.soccerstats.com/latest.asp?league=%s' % self._league
        resp = self._session.get(url=url)
        all_hrefs = re.findall('&nbsp;<a href=\'(.*)\' title=', resp.text)
        teams_urls = set()
        for href in all_hrefs:
            teams_urls.add('https://www.soccerstats.com/' + href)

        return teams_urls







def main():

    crawler = SoccerStatsCrawler()
    teams_url = crawler.get_teams_url()
    print(teams_url)


if __name__ == '__main__':
    main()