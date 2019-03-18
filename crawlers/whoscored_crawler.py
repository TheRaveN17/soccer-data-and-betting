import re
import json
import concurrent.futures as cf

from urllib import parse

import requests

from requests_futures.sessions import FuturesSession
from bs4 import BeautifulSoup

from utils import cons
from utils import session
from utils import countries
from utils import log
from database import db


logger = log.get_logger(logging_file='crawler.log')


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
                self._country_code = country_code
            except KeyError:
                logger.error('bad country_code: %s' % country_code)
                raise SystemExit
        else:
            self._session = self._new_session()

        logger.info('successfully initialized WhoScored crawler object')

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
        ses.cookies.set(name='ct',
                        value=country_code.upper(),
                        domain='.whoscored.com')

        logger.info('successfully created new session')

        return ses

    def _crawl(self, urls: list) -> list:
        """Crawls faster using requests_futures lib
        :param urls: urls to be crawled
        :return: sorted response objects
        """
        futures = list()
        unsorted_result = list()
        sorted_result = list()
        for i in range(0, len(urls)): #initialize list
            sorted_result.append(i)
        ses = FuturesSession(session=self._session, max_workers=cons.WORKERS)

        for i in range(0, len(urls)):
            futures.append(ses.get(url=urls[i]))
            urls[i] = urls[i].encode('utf-8')
        for future in cf.as_completed(futures):
            result = future.result()
            unsorted_result.append(result)

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
            logger.error('problems connecting to %s\n...ABORTING...' % cons.WHOSCORED_URL)
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

        logger.info('successfully retrieved all leagues')

        return leagues

    @staticmethod
    def select_leagues_by_region(leagues: list, region_name: str) -> list:
        """Gets only leagues specific to a country or region
        :param leagues: list of leagues as returned by crawler.get_leagues()
        :param region_name: name of filter region (exp: Romania, only Liga 1, Liga2, etc.)
        :return: list of filtered leagues
        """
        return list((lg for lg in leagues if lg['region'] == region_name))

    def add_data(self, leagues: list) -> list:
        """Crawls all seasons and teams in current season
        :param leagues: dicts
        :return: data collected for leagues as dicts
        """
        leagues_mp = self._crawl_leagues(leagues=leagues)
        for index in range(len(leagues)):
            leagues[index]['seasons'] = self._get_seasons(league_mpg=leagues_mp[index])
            leagues[index]['stats_urls'] = self._get_stats_urls(league_mpg=leagues_mp[index])

        detailed_leagues = list()
        for index in range(len(leagues)):
            if not leagues[index]['stats_urls']:
                continue
            nl = leagues[index]
            nl['teams'] = self._get_teams(league=leagues[index])

            for team in nl['teams']:
                team['players'] = self._get_players(team=team)
            detailed_leagues.append(nl)

        return detailed_leagues

    def _crawl_leagues(self, leagues: list) -> list:
        """Crawls all leagues' main pages
        :param leagues: dicts
        :return: list of Response objects
        """
        leagues_urls = list()
        for league in leagues:
            leagues_urls.append(league['url'])
        try:
            leagues_mp = self._crawl(urls=leagues_urls)
        except Exception as err:
            logger.error('failed to retrieve all leagues\' main pages')
            logger.error(err)
            raise SystemExit

        logger.info('successfully retrieved all leagues\' main pages')

        return leagues_mp

    @staticmethod
    def _get_seasons(league_mpg: requests.Response) -> dict:
        """ Retrieves all seasons for a league
        :param league_mpg: the response of the request to this league's url
        :return: dict
        dict[year] = url
        """
        soup = BeautifulSoup(league_mpg.content, 'lxml')
        all_options = soup.find_all('option')

        seasons = dict()
        for option in all_options:
            if 'Seasons' not in option.attrs['value']:
                continue
            seasons[option.contents[0]] = cons.WHOSCORED_URL + option.attrs['value'][1:]

        return seasons

    @staticmethod
    def _get_stats_urls(league_mpg: requests.Response) -> dict:
        """ Retrieves all useful urls for league (both teams and players)
        :param league_mpg: the response of the request to this league's url
        :return: dict
        dict[teams] = url for teams' stats
        dict[players] = dict for players' stats
        """
        urls = dict()
        soup = BeautifulSoup(league_mpg.content, 'lxml')
        try:
            urls['teams'] = cons.WHOSCORED_URL + soup.find('a', {'id': 'link-statistics'}).attrs['href'][1:]
            urls['players'] = cons.WHOSCORED_URL + soup.find('a', {'id': 'link-player-statistics'}).attrs['href'][1:]
        except:
            urls = None

        return urls

    def _get_teams(self, league: dict) -> list:
        """ Gets all teams that are playing in this league
        :param league: league to be checked
        :return: all teams as dicts
        """
        all_teams = list()

        resp = self._session.get(url=league['stats_urls']['teams'])
        stageId = re.findall('([0-9]{5})', league['stats_urls']['teams'])[0]
        model_last_mode= self._get_header_value(resp)

        params = {
            'category': 'summaryteam',
            'subcategory': 'all',
            'statsAccumulationType': '0',
            'field': 'Overall',
            'tournamentOptions': '',
            'timeOfTheGameStart': '',
            'timeOfTheGameEnd': '',
            'teamIds': '',
            'stageId': stageId,
            'sortBy': 'Rating',
            'sortAscending': '',
            'page': '',
            'numberOfTeamsToPick': '',
            'isCurrent': 'true',
            'formation': ''
        }
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Model-last-Mode': model_last_mode,
            'Referer': league['stats_urls']['teams']
        }
        resp = self._session.get(url=cons.TEAM_STATS_URL, params=params, headers=headers)
        resp = re.sub(' ', '', resp.content.decode('utf-8'))
        resp = resp.split(',"paging')[0] #eliminate stats columns and paging vars
        resp = resp.split('Stats":')[1]
        resp = json.loads(resp)

        for item in resp:
            team = dict()
            team['name'] = item['name']
            team['id'] = item['teamId']
            team['leagueId'] = league['id']
            team['url'] = 'https://www.whoscored.com/Teams/{}/Show/{}-{}'.format(team['id'], item['teamRegionName'], team['name'])
            all_teams.append(team)

        logger.info('succesfully retrieved all teams\' ids and urls for league %s' % league['name'])

        return all_teams

    def _get_players(self, team: dict) -> list:
        """ Gets all players currently in this team
        :param team: team to be checked
        :return: all players as dicts
        """
        all_players = list()

        resp = self._session.get(url=team['url'])
        model_last_mode = self._get_header_value(resp)

        params = {
            'category': 'summary',
            'subcategory': 'all',
            'statsAccumulationType': '0',
            'isCurrent': 'true',
            'playerId': '',
            'teamIds': team['id'],
            'matchId': '',
            'stageId': '',
            'tournamentOptions': team['leagueId'],
            'sortBy': 'Rating',
            'sortAscending': '',
            'age': '',
            'ageComparisonType': '',
            'appearances': '',
            'appearancesComparisonType': '',
            'field': 'Overall',
            'nationality': '',
            'positionOptions': '',
            'timeOfTheGameStart': '',
            'timeOfTheGameEnd': '',
            'isMinApp': 'false',
            'page': '',
            'includeZeroValues': 'true',
            'numberOfPlayersToPick': ''
        }
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Model-last-Mode': model_last_mode,
            'Referer': team['url']
        }
        resp = self._session.get(url=cons.PLAYER_STATS_URL, params=params, headers=headers)
        resp = re.sub(' ', '', resp.content.decode('utf-8'))
        resp = resp.split(',"paging')[0]  # eliminate stats columns and paging vars
        resp = resp.split('Stats":')[1]
        resp = json.loads(resp)

        for item in resp:
            player = dict()
            player['name'] = item['name']
            player['id'] = item['playerId']
            player['url'] = 'https://www.whoscored.com/Players/{}/Show/{}'.format(player['id'], player['name'])
            all_players.append(player)

        logger.info('successfully retrieved all players\' ids and urls for team %s' % team['name'])
        self._clear_bad_cookies()

        return all_players

    @staticmethod
    def _get_header_value(page: requests.Response) -> str:
        """Returns the Model-last-Mode (fucked up name for a header)
        :return: header value
        """
        return re.findall('\'Model-last-Mode\': \'(.*=)\' }', page.text)[0]

    def _clear_bad_cookies(self):
        """Clear bad cookies that crash the crawler
        :return: None
        """
        val = self._session.cookies['ct']
        self._session.cookies.clear()
        self._session.cookies.set(name='ct',
                        value=val,
                        domain='.whoscored.com')

        return

    def get_basic_player_info(self, players: list) -> list:
        """Given a list of players and their urls, gather basic info about them, such as age, position, history, etc.
        :param players: list
        :return: list
        """
        detailed_players = list()
        for player in players:
            try:
                dp = self._get_player_data(player=player)
            except:
                self._session = self._new_session(country_code='gb')
                dp = self._get_player_data(player=player)
            detailed_players.append(dp)

        return detailed_players

    def _get_player_data(self, player: dict) -> dict:
        """Given a player with name and url, gather basic info about him
        :param player: dict
        :return: dict
        """
        resp = self._session.get(url=player['url'])
        model_last_mode = self._get_header_value(page=resp)

        params = {
            'category': 'summary',
            'subcategory': 'all',
            'statsAccumulationType': '0',
            'isCurrent': 'true',
            'playerId': player['id'],
            'teamIds': '',
            'matchId': '',
            'stageId': '',
            'tournamentOptions': '',
            'sortBy': 'Rating',
            'sortAscending': '',
            'age': '',
            'ageComparisonType': '',
            'appearances': '',
            'appearancesComparisonType': '',
            'field': 'Overall',
            'nationality': '',
            'positionOptions': '',
            'timeOfTheGameStart': '',
            'timeOfTheGameEnd': '',
            'isMinApp': 'false',
            'page': '',
            'includeZeroValues': 'true',
            'numberOfPlayersToPick': ''
        }
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Model-last-Mode': model_last_mode,
            'Referer': player['url']
        }
        resp = self._session.get(url=cons.PLAYER_STATS_URL, params=params, headers=headers)
        resp = json.loads(resp.content.decode('utf-8'))
        items = resp['playerTableStats'][0]

        player['position'] = items['positionText']
        player['age'] = items['age']
        player['height'] = items['height']
        player['weight'] = items['weight']
        player['played_positions'] = items['playedPositions']
        player['rating'] = round(items['rating'], 2)
        player.pop('id')

        logger.info('successfully retrieved info about %s' % player['name'])
        self._clear_bad_cookies()

        return player



def main():
    crawler = WhoScoredCrawler(country_code='gb')
    italy_db = db.SoccerDatabase(name='Italy')
    leagues = crawler.get_leagues()
    leagues = crawler.select_leagues_by_region(leagues=leagues, region_name='Italy')
    italy_league = crawler.add_data(leagues=[leagues[0]])
    team_id = 1
    for team in italy_league[0]['teams'][:2]:
        team['players'] = crawler.get_basic_player_info(players=team['players'])
        for player in team['players']:
            player['team_id'] = team_id
        italy_db.add_players(players=team['players'])
        team.pop('id')
        team.pop('leagueId')
        team.pop('players')
        italy_db.add_team(team=team)
        team_id += 1

if __name__ == '__main__':
    main()