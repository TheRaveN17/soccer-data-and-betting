"""Run script with the region name you want the premier league's teams and players database built for
exp: region = Italy will create a database named Italy.db in database directory"""

region = 'Italy'

from crawlers import whoscored_crawler
from database import db

def main():
    crawler = whoscored_crawler.WhoScoredCrawler(country_code='gb')
    dbo = db.SoccerDatabase(name=region)
    leagues = crawler.get_leagues()
    leagues = crawler.select_leagues_by_region(leagues=leagues, region_name=region)
    premier_league = crawler.add_data(leagues=[leagues[0]])
    for team in premier_league[0]['teams']:
        team['players'] = crawler.get_basic_player_info(players=team['players'])
        dbo.add_team_and_players(team)
    print('database %s successfully created' % region)

if __name__ == '__main__':
    main()
