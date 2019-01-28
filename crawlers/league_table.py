import requests

from bs4 import BeautifulSoup
from arrow import utcnow


def getCookie (session, name, value, expdays):

    expires = utcnow() + expdays * 24 * 60 *60


def main():

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:64.0) Gecko/20100101 Firefox/64.0',
        'Pragma': 'no-cache'
    }
    session = requests.Session()
    session.headers.update(headers)

    url = 'https://www.soccerstats.com/'
    resp = session.get(url=url)
    session.cookies.set(name='cookiesok',
                        value='no',
                        domain='www.soccerstats.com',
                        expires=utcnow().timestamp + 365*24*60*60)
    # session.cookies.set(name='tz',
    #                     value='120',
    #                     domain='www.soccerstats.com')

    #url = 'https://www.soccerstats.com/team_statitems.asp'
    url = 'https://www.soccerstats.com/latest.asp?league=england'
    headers = {
        'Host': 'www.soccerstats.com',
        'Referer' : 'https://www.soccerstats.com/'
    }
    resp = session.get(url=url, headers=headers)
    soup = BeautifulSoup(resp.content, features='lxml')
    all_teams_href = soup.find_all('tr', {'class': 'trow3'})
    print(all_teams_href)


if __name__ == '__main__':
    main()