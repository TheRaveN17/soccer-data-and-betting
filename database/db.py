from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from utils import log
from database import models


logger = log.get_logger(logging_file='db.log')


class SoccerDatabase(object):

    def __init__(self, name: str):
        """Initializes a database object for storing teams and players
        :param name: name of the database
        """
        super().__init__()

        self._name = name
        engine = create_engine('sqlite:///../database/%s.db' % self._name)
        models.Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self._session = Session()

        logger.info('successfully initialized database %s' % self._name)

    def add_players(self, players: list):
        """Add players to database
        :param players_list: dicts with players
        """
        players_objs = list()
        for player in players:
            po = models.Player(team_id=player['team_id'],
                                   name=player['name'],
                                   url=player['url'],
                                   position=player['position'],
                                   played_positions=player['played_positions'],
                                   age=player['age'],
                                   height=player['height'],
                                   weight=player['weight'],
                                   rating=player['rating'])
            players_objs.append(po)
        self._session.bulk_save_objects(players_objs)
        self._session.commit()

        logger.info('successfully added players to database %s' % self._name)

    def add_team(self, team: dict):
        """Add teams to database
        :param teams_list: dicts with teams
        """
        to = models.Team(name=team['name'],
                             url=team['url'])
        self._session.add(to)
        self._session.commit()

        logger.info('successfully added teams to database %s' % self._name)

    def get_players(self):
        players = self._session.query(models.Player).all()
        return players

    def get_teams(self):
        teams = self._session.query(models.Team).all()
        return teams


if __name__ == '__main__':
    italy_db = SoccerDatabase(name='Italy')
    pl = italy_db.get_players()
    tl = italy_db.get_teams()
    print(pl)
    print(tl)