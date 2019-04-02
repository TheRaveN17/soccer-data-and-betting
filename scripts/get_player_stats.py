"""Run script with the name of the database you want player stats collected for"""

db_name = 'Italy'

from crawlers import whoscored_crawler
from database import db
from utils import util

def main():
    crawler = whoscored_crawler.WhoScoredCrawler(country_code='gb')
    dbo = db.SoccerDatabase(name=db_name)
    players_obj = dbo.get_players()
    players_dict = util.plr_obj_to_dict(players=players_obj)
    players = crawler.update_players(players=players_dict)
    dbo.add_players_data(players=players)
    print('database %s successfully updated' % db_name)

if __name__ == '__main__':
    main()
