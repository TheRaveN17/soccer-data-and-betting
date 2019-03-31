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
                self._session = self._new_session(country_code=self._country_code)
                dp = self._get_player_data(player=player)
            detailed_players.append(dp)

        return detailed_players

    def _get_player_data(self, player: dict) -> dict:
        """Given a player with name and url, gather basic info about him
        :param player: dict
        :return: dict
        """
        try:
            resp = self._session.get(url=player['url'], timeout=10)
        except:
            self._session = self._new_session(country_code=self._country_code)
            return self._get_player_data(player=player)
        model_last_mode = self._get_header_value(page=resp)

        params = cons.PLAYER_PARAMS
        params['category'] = 'summary'
        params['subcategory'] = 'all'
        params['statsAccumulationType'] = '0'
        params['isCurrent'] = 'true'
        params['playerId'] = player['id']
        params['sortBy'] = 'Rating'
        params['field'] = 'Overall'
        params['isMinApp'] = 'false'
        params['ageComparisonType'] = ''
        params['appearancesComparisonType'] = ''
        params['positionOptions'] = ''
        params['timeOfTheGameStart'] = ''
        params['timeOfTheGameEnd'] = ''
        params['page'] = ''
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Model-last-Mode': model_last_mode,
            'Referer': player['url']
        }
        try:
            resp = self._session.get(url=cons.PLAYER_STATS_URL, params=params, headers=headers, timeout=10)
        except:
            self._session = self._new_session(country_code=self._country_code)
            return self._get_player_data(player=player)
        resp = json.loads(resp.content.decode('utf-8'))
        items = resp['playerTableStats'][0]

        player['role'] = items['positionText']
        player['age'] = items['age']
        player['height'] = items['height']
        player['weight'] = items['weight']
        player['played_positions'] = items['playedPositions']

        logger.info('successfully retrieved info about %s' % player['name'])
        self._clear_bad_cookies()

        return player

    def update_players(self, players: list) -> list:
        """Call self._player_stats_by_role for all players provided
        :param players: as stored in the database (player[n][role] = role)
        :return: updated players
        """
        for player in players:
            self._player_stats_by_role(player=player)

        return players

    def _player_stats_by_role(self, player: dict) -> dict:
        """Get statistics for player by his role (Defender, Midfielder, Forward, Goalkeeper)
        :param player: as stored in the database (player[n][role] = role)
        :return: updated player
        """
        try:
            if player['role']  == 'Defender':
                self._get_defender_stats(defender=player)
            elif player['role']  == 'Midfielder':
                self._get_midfielder_stats(midfielder=player)
            elif player['role']  == 'Forward':
                self._get_forward_stats(forward=player)
            elif player['role']  == 'Goalkeeper':
                self._get_goalkeeper_stats(goalkeeper=player)
            else:
                logger.error('player %s has no role assigned' % player['name'])
        except:
            self._session = self._new_session(country_code=self._country_code)
            return self._player_stats_by_role(player=player)

        return player

    def _get_goalkeeper_stats(self, goalkeeper: dict) -> dict:
        """Get statistics for players that have the goalkeeper role
        :param goalkeeper: player as stored in the database --> player['role'] == Goalkeeper
        :return: goalkeeper with extra stats
        """
        history_url = re.sub('Show', 'History', goalkeeper['url'])
        resp = self._session.get(url=history_url)
        model_last_mode = self._get_header_value(page=resp)

        params = cons.PLAYER_PARAMS
        params['category'] = 'saves'
        params['subcategory'] = 'shotzone'
        params['playerId'] = re.findall('(\d.*\d)', goalkeeper['url'])[0]
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Model-last-Mode': model_last_mode,
            'Referer': re.sub('Show', 'History', goalkeeper['url'])
        }
        resp = self._session.get(url=cons.PLAYER_STATS_URL, params=params, headers=headers)
        resp = json.loads(resp.content.decode('utf-8'))

        saveObox, savePenaltyArea, saveSixYardBox = 0, 0, 0
        for item in resp['playerTableStats']:
            if item['seasonName'] == cons.FIRST_IRRELEVANT_SEASON:
                break
            saveObox += item['saveObox']
            savePenaltyArea += item['savePenaltyArea']
            saveSixYardBox += item['saveSixYardBox']
        goalkeeper['savesSixYardBox'] = int(saveSixYardBox)
        goalkeeper['savesPenaltyArea'] = int(savePenaltyArea)
        goalkeeper['savesOutOfBox'] = int(saveObox)

        params['category'] = 'clearances'
        params['subcategory'] = 'success'
        resp = self._session.get(url=cons.PLAYER_STATS_URL, params=params, headers=headers)
        resp = json.loads(resp.content.decode('utf-8'))
        clearances = 0
        for item in resp['playerTableStats']:
            if item['seasonName'] == cons.FIRST_IRRELEVANT_SEASON:
                break
            clearances += item['clearanceTotal']
        goalkeeper['clearances'] = int(clearances)

        goalkeeper = self._get_aerial_data(player=goalkeeper, model_last_mode=model_last_mode)
        goalkeeper = self._get_player_xp(player=goalkeeper, model_last_mode=model_last_mode)
        self._clear_bad_cookies()

        logger.info('successfully retrieved forward stats for %s' % goalkeeper['name'])
        return goalkeeper

    def _get_forward_stats(self, forward: dict) -> dict:
        """Get statistics for players that have the forward role
        :param forward: player as stored in the database --> player['role'] == Forward
        :return: forward with extra stats
        """
        history_url = re.sub('Show', 'History', forward['url'])
        resp = self._session.get(url=history_url)
        hv = self._get_header_value(page=resp)

        forward = self._get_offensive_data(player=forward, model_last_mode=hv)
        forward = self._get_aerial_data(player=forward, model_last_mode=hv)
        forward = self._get_goals_data(player=forward, model_last_mode=hv)
        forward = self._get_passing_data(player=forward, model_last_mode=hv)
        forward = self._get_player_xp(player=forward, model_last_mode=hv)
        self._clear_bad_cookies()

        logger.info('successfully retrieved forward stats for %s' % forward['name'])
        return forward

    def _get_defender_stats(self, defender: dict) -> dict:
        """Get statistics for players that have the defender role
        :param defender: player as stored in the database --> player['role'] == Defender
        :return: defender with extra stats
        """
        history_url = re.sub('Show', 'History', defender['url'])
        resp = self._session.get(url=history_url)
        hv = self._get_header_value(page=resp)

        defender = self._get_defensive_data(player=defender, model_last_mode=hv)
        defender = self._get_aerial_data(player=defender, model_last_mode=hv)
        defender = self._get_goals_data(player=defender, model_last_mode=hv)
        self._clear_bad_cookies()
        defender = self._get_passing_data(player=defender, model_last_mode=hv)
        defender = self._get_player_xp(player=defender, model_last_mode=hv)
        self._clear_bad_cookies()

        logger.info('successfully retrieved defender stats for %s' % defender['name'])
        return defender

    def _get_midfielder_stats(self, midfielder: dict) -> dict:
        """Get statistics for players that have the defender role
        :param midfielder: player as stored in the database --> player['role'] == Midfielder
        :return: midfielder with extra stats
        """
        history_url = re.sub('Show', 'History', midfielder['url'])
        resp = self._session.get(url=history_url)
        hv = self._get_header_value(page=resp)

        midfielder = self._get_offensive_data(player=midfielder, model_last_mode=hv)
        midfielder = self._get_defensive_data(player=midfielder, model_last_mode=hv)
        midfielder = self._get_aerial_data(player=midfielder, model_last_mode=hv)
        self._clear_bad_cookies()
        midfielder = self._get_goals_data(player=midfielder, model_last_mode=hv)
        midfielder = self._get_passing_data(player=midfielder, model_last_mode=hv)
        midfielder = self._get_player_xp(player=midfielder, model_last_mode=hv)
        self._clear_bad_cookies()

        logger.info('successfully retrieved midfielder stats for %s' % midfielder['name'])
        return midfielder

    def _get_player_xp(self, player: dict, model_last_mode: str) -> dict:
        """Get player game experience
        :param player: player as stored in the database
        :param model_last_mode: header value necessary for the get request --> see self._get_header_value
        :return: player with experience stats as total minutes played
        !!! international experience counts as 1.3 * minutes played, second rate leagues experience counts as 0.7 * minutes played
        """
        params = cons.PLAYER_PARAMS
        params['category'] = 'summary'
        params['subcategory'] = 'all'
        params['statsAccumulationType'] = '0'
        params['playerId'] = re.findall('(\d.*\d)', player['url'])[0]
        params['field'] = 'Overall'
        params['isMinApp'] = 'false'
        params['ageComparisonType'] = ''
        params['appearancesComparisonType'] = ''
        params['positionOptions'] = ''
        params['timeOfTheGameStart'] = ''
        params['timeOfTheGameEnd'] = ''
        params['page'] = ''
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Model-last-Mode': model_last_mode,
            'Referer': re.sub('Show', 'History', player['url'])
        }
        resp = self._session.get(url=cons.PLAYER_STATS_URL, params=params, headers=headers)
        resp = json.loads(resp.content.decode('utf-8'))

        experience, apps = 0, 0
        for item in resp['playerTableStats']:
            if item['seasonName'] == cons.FIRST_IRRELEVANT_SEASON:
                break
            if item['tournamentName'] in cons.INTERNATIONAL_LEAGUES:
                experience += 1.3 * item['minsPlayed']
            elif item['tournamentName'] in cons.A_RATED_LEAGUES:
                experience += item['minsPlayed']
            else:
                experience += 0.7 * item['minsPlayed']
            apps += item['apps']
        player['xp'] = int(experience)
        player['apps'] = int(apps)

        logger.info('successfully retrieved game experience for %s' % player['name'])
        return player

    def _get_offensive_data(self, player: dict, model_last_mode: str) -> dict:
        """Gets shots taken player statistics
        :param player: player as stored in the database
        :param model_last_mode: header value necessary for the get request --> see self._get_header_value
        :return: player with shots accuracy stats
        """
        params = cons.PLAYER_PARAMS
        params['playerId'] = re.findall('(\d.*\d)', player['url'])[0]
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Model-last-Mode': model_last_mode,
            'Referer': re.sub('Show', 'History', player['url'])
        }

        params['category'] = 'shots'
        params['subcategory'] = 'accuracy'
        resp = self._session.get(url=cons.PLAYER_STATS_URL, params=params, headers=headers)
        resp = json.loads(resp.content.decode('utf-8'))
        son, sof, sb, sp = 0, 0, 0, 0
        for item in resp['playerTableStats']:
            if item['seasonName'] == cons.FIRST_IRRELEVANT_SEASON:
                break
            son += item['shotOnTarget']
            sof += item['shotOffTarget']
            sb += item['shotBlocked']
            sp += item['shotOnPost']
        player['shotsOnTarget'] = int(son)
        player['shotsOffTarget'] = int(sof)
        player['shotsBlocked'] = int(sb)
        player['shotsPost'] = int(sp)

        params['category'] = 'dribbles'
        params['subcategory'] = 'success'
        resp = self._session.get(url=cons.PLAYER_STATS_URL, params=params, headers=headers)
        resp = json.loads(resp.content.decode('utf-8'))
        td, sd = 0, 0
        for item in resp['playerTableStats']:
            if item['seasonName'] == cons.FIRST_IRRELEVANT_SEASON:
                break
            sd += item['dribbleWon']
            td += item['dribbleTotal']
        player['dribbling'] = round(sd / td * 100, 2)

        logger.info('successfully retrieved offensive stats for %s' % player['name'])
        return player

    def _get_goals_data(self, player: dict, model_last_mode: str) -> dict:
        """Gets goals scored player statistics
        :param player: player as stored in the database
        :param model_last_mode: header value necessary for the get request --> see self._get_header_value
        :return: player with goals scored stats
        """
        params = cons.PLAYER_PARAMS
        params['category'] = 'goals'
        params['subcategory'] = 'situations'
        params['playerId'] = re.findall('(\d.*\d)', player['url'])[0]
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Model-last-Mode': model_last_mode,
            'Referer': re.sub('Show', 'History', player['url'])
        }
        resp = self._session.get(url=cons.PLAYER_STATS_URL, params=params, headers=headers)
        resp = json.loads(resp.content.decode('utf-8'))

        g, spg = 0, 0
        for item in resp['playerTableStats']:
            if item['seasonName'] == cons.FIRST_IRRELEVANT_SEASON:
                break
            g += item['goalNormal']
            spg += item['goalSetPiece']
        player['goals'] = int(g)
        player['setPieceGoals'] = int(spg)

        logger.info('successfully retrieved goals scored for %s' % player['name'])
        return player

    def _get_passing_data(self, player: dict, model_last_mode: str) -> dict:
        """Gets player passing statistics
        :param player: player as stored in the database
        :param model_last_mode: header value necessary for the get request --> see self._get_header_value
        :return: player with passing data added
        """
        params = cons.PLAYER_PARAMS
        params['playerId'] = re.findall('(\d.*\d)', player['url'])[0]
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Model-last-Mode': model_last_mode,
            'Referer': re.sub('Show', 'History', player['url'])
        }

        params['category'] = 'passes'
        params['subcategory'] = 'length'
        resp = self._session.get(url=cons.PLAYER_STATS_URL, params=params, headers=headers)
        resp = json.loads(resp.content.decode('utf-8'))
        alp, ilp, asp, isp = 0, 0, 0, 0
        for item in resp['playerTableStats']:
            if item['seasonName'] == cons.FIRST_IRRELEVANT_SEASON:
                break
            alp += item['passLongBallAccurate']
            ilp += item['passLongBallInaccurate']
            asp += item['shortPassAccurate']
            isp += item['shortPassInaccurate']
        player['shortPassAccuracy'] = round(asp / (asp + isp) * 100, 2)
        player['longPassAccuracy'] = round(alp / (alp + ilp) * 100, 2)

        params['subcategory'] = 'type'
        resp = self._session.get(url=cons.PLAYER_STATS_URL, params=params, headers=headers)
        resp = json.loads(resp.content.decode('utf-8'))
        ac, ic = 0, 0
        for item in resp['playerTableStats']:
            if item['seasonName'] == cons.FIRST_IRRELEVANT_SEASON:
                break
            ac += item['passCrossAccurate']
            ic += item['passCrossInaccurate']
        player['totalCrosses'] = int(ac + ic)
        player['crossAccuracy'] = round(ac / player['totalCrosses'] * 100, 2)

        params['category'] = 'key-passes'
        params['subcategory'] = 'length'
        resp = self._session.get(url=cons.PLAYER_STATS_URL, params=params, headers=headers)
        resp = json.loads(resp.content.decode('utf-8'))
        kp = 0
        for item in resp['playerTableStats']:
            if item['seasonName'] == cons.FIRST_IRRELEVANT_SEASON:
                break
            kp += item['keyPassesTotal']
        player['keyPasses'] = int(kp)

        params['category'] = 'assists'
        params['subcategory'] = 'type'
        resp = self._session.get(url=cons.PLAYER_STATS_URL, params=params, headers=headers)
        resp = json.loads(resp.content.decode('utf-8'))
        a = 0
        for item in resp['playerTableStats']:
            if item['seasonName'] == cons.FIRST_IRRELEVANT_SEASON:
                break
            a += item['assist']
        player['assists'] = int(a)

        logger.info('successfully retrieved passing stats for %s' % player['name'])
        return player

    def _get_aerial_data(self, player: dict, model_last_mode: str) -> dict:
        """Gets aerial player statistics
        :param player: player as stored in the database
        :param model_last_mode: header value necessary for the get request --> see self._get_header_value
        :return: player with aerial stats
        """
        params = cons.PLAYER_PARAMS
        params['category'] = 'aerial'
        params['subcategory'] = 'success'
        params['playerId'] = re.findall('(\d.*\d)', player['url'])[0]
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Model-last-Mode': model_last_mode,
            'Referer': re.sub('Show', 'History', player['url'])
        }
        resp = self._session.get(url=cons.PLAYER_STATS_URL, params=params, headers=headers)
        resp = json.loads(resp.content.decode('utf-8'))

        won, lost = 0, 0
        for item in resp['playerTableStats']:
            if item['seasonName'] == cons.FIRST_IRRELEVANT_SEASON:
                break
            won += item['duelAerialWon']
            lost += item['duelAerialLost']
        player['aerial'] = round(won / (won + lost) * 100, 2)

        logger.info('successfully retrieved aerial data for %s' % player['name'])
        return player

    def _get_defensive_data(self, player: dict, model_last_mode: str) -> dict:
        """Gets tackling player statistics
        :param player: player as stored in the database
        :param model_last_mode: header value necessary for the get request --> see self._get_header_value
        :return: player with tackling stats
        """
        params = cons.PLAYER_PARAMS
        params['playerId'] = re.findall('(\d.*\d)', player['url'])[0]
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Model-last-Mode': model_last_mode,
            'Referer': re.sub('Show', 'History', player['url'])
        }

        params['category'] = 'tackles'
        params['subcategory'] = 'success'
        resp = self._session.get(url=cons.PLAYER_STATS_URL, params=params, headers=headers)
        resp = json.loads(resp.content.decode('utf-8'))
        st, dp = 0, 0
        for item in resp['playerTableStats']:
            if item['seasonName'] == cons.FIRST_IRRELEVANT_SEASON:
                break
            st += item['tackleWonTotal']
            dp += item['challengeLost']
        player['tackling'] = round(st / (st + dp) * 100, 2)

        params['category'] = 'interception'
        params['subcategory'] = 'success'
        resp = self._session.get(url=cons.PLAYER_STATS_URL, params=params, headers=headers)
        resp = json.loads(resp.content.decode('utf-8'))
        interceptions = 0
        for item in resp['playerTableStats']:
            if item['seasonName'] == cons.FIRST_IRRELEVANT_SEASON:
                break
            interceptions += item['interceptionAll']
        player['interceptions'] = int(interceptions)

        params['category'] = 'clearances'
        params['subcategory'] = 'success'
        resp = self._session.get(url=cons.PLAYER_STATS_URL, params=params, headers=headers)
        resp = json.loads(resp.content.decode('utf-8'))
        clearances = 0
        for item in resp['playerTableStats']:
            if item['seasonName'] == cons.FIRST_IRRELEVANT_SEASON:
                break
            clearances += item['clearanceTotal']
        player['clearances'] = int(clearances)

        params['category'] = 'blocks'
        params['subcategory'] = 'type'
        resp = self._session.get(url=cons.PLAYER_STATS_URL, params=params, headers=headers)
        resp = json.loads(resp.content.decode('utf-8'))
        sb, cb, pb = 0, 0, 0
        for item in resp['playerTableStats']:
            if item['seasonName'] == cons.FIRST_IRRELEVANT_SEASON:
                break
            sb += item['outfielderBlock']
            cb += item['passCrossBlockedDefensive']
            pb += item['outfielderBlockedPass']
        player['shotsBlocked'] = int(sb)
        player['crossesBlocked'] = int(cb)
        player['passesBlocked'] = int(pb)

        logger.info('successfully defensive data for %s' % player['name'])
        return player
