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

    def add_team_and_players(self, team: dict):
        """Add team and it's players to database
        :param team: team data, including current squad
        """
        to = models.Team(name=team['name'],
                         url=team['url'],
                         players=list())
        for player in team['players']:
            po = models.Player(name=player['name'],
                               url=player['url'],
                               role=player['role'],
                               played_positions=player['played_positions'],
                               age=player['age'],
                               height=player['height'],
                               weight=player['weight'])
            to.players.append(po)
            self._session.add(po)
        self._session.add(to)
        self._session.commit()

        logger.info('successfully added team %s and squad to database %s' % (team['name'], self._name))

    def get_teams(self):
        teams = self._session.query(models.Team).all()
        return teams

    def get_players(self):
        players = self._session.query(models.Player).all()
        return players


if __name__ == '__main__':
    italy_db = SoccerDatabase(name='Italy')
    teams = italy_db.get_teams()
    players = italy_db.get_players()
    print('wow')
