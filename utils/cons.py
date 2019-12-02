#session related constants
USER_AGENT_TAG = 'User-Agent'
USER_AGENT_CRAWL = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:64.0) Gecko/20100101 Firefox/64.0'
USER_AGENT_NT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0'

#crawler related constants
CURRENT_SEASON = '2018/2019'
FIRST_IRRELEVANT_SEASON = '2014/2015' #crawl only current season and last three years
A_RATED_LEAGUES = ['Premier League', 'Serie A', 'La Liga', 'Bundesliga', 'Ligue 1']
INTERNATIONAL_LEAGUES = ['UEFA Champions League', 'FIFA World Cup', 'UEFA Europa League']
WORKERS = 10
WHOSCORED_URL = 'https://www.whoscored.com/'
TEAM_STATS_URL = 'https://www.whoscored.com/StatisticsFeed/1/GetTeamStatistics'
PLAYER_STATS_URL = 'https://www.whoscored.com/StatisticsFeed/1/GetPlayerStatistics'
PLAYER_PARAMS = {
            'category': '',
            'subcategory': '',
            'statsAccumulationType': '2',
            'isCurrent': 'false',
            'playerId': '',
            'teamIds': '',
            'matchId': '',
            'stageId': '',
            'tournamentOptions': '',
            'sortBy': 'seasonId',
            'sortAscending': '',
            'age': '',
            'ageComparisonType': '0',
            'appearances': '',
            'appearancesComparisonType': '0',
            'field': '',
            'nationality': '',
            'positionOptions': "'FW','AML','AMC','AMR','ML','MC','MR','DMC','DL','DC','DR','GK','Sub'",
            'timeOfTheGameStart': '0',
            'timeOfTheGameEnd': '5',
            'isMinApp': '',
            'page': '1',
            'includeZeroValues': 'true',
            'numberOfPlayersToPick': ''
}
