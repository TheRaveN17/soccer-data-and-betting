from sqlalchemy import create_engine
from sqlalchemy.sql import select

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
        models.metadata.create_all(engine)
        self._connection = engine.connect()

        logger.info('successfully connected to database %s' % self._name)

    def add_players(self, players_list: list):
        """Add players to database
        :param players_list: dicts with players
        """
        ins = models.players.insert()
        result = self._connection.execute(ins, players_list)

        logger.info('successfully added players to database %s' % self._name)
        return result

    def add_teams(self, teams_list: list):
        """Add teams to database
        :param teams_list: dicts with teams
        """
        ins = models.teams.insert()
        result = self._connection.execute(ins, teams_list)

        logger.info('successfully added teams to database %s' % self._name)
        return result

    def get_players(self):
        slct = select([models.players])
        rp = self._connection.execute(slct)
        return list(rp)


if __name__ == '__main__':
    italy_db = SoccerDatabase(name='Italy')
    pl = italy_db.get_players()
    print(pl)