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

    def add_players_data(self, players: list):
        """Add players extra data based on their role (Forward, Midfielder, Defender or Goalkeeper)
        :param players: players as objects model.Player retrieved from database
        """
        for player in players:
            if player['role'] == 'Defender':
                po = models.Defender(xp=player['xp'],
                                     apps=player['apps'],
                                     tackling=player['tackling'],
                                     interceptions=player['interceptions'],
                                     clearances=player['clearances'],
                                     crossesBlocked=player['crossesBlocked'],
                                     passesBlocked=player['passesBlocked'],
                                     aerial=player['aerial'],
                                     goals=player['goals'],
                                     setPieceGoals=player['setPieceGoals'],
                                     shortPassAccuracy=player['shortPassAccuracy'],
                                     longPassAccuracy=player['longPassAccuracy'],
                                     totalCrosses=player['totalCrosses'],
                                     crossAccuracy=player['crossAccuracy'],
                                     keyPasses=player['keyPasses'],
                                     assists=player['assists'])
                po.player = player['playerObj']
            elif player['role'] == 'Midfielder':
                po = models.Midfielder(xp=player['xp'],
                                       apps=player['apps'],
                                       shotsOnTarget=player['shotsOnTarget'],
                                       shotsOffTarget=player['shotsOffTarget'],
                                       shotsBlocked=player['shotsBlocked'],
                                       shotsPost=player['shotsPost'],
                                       dribbling=player['dribbling'],
                                       tackling=player['tackling'],
                                       interceptions=player['interceptions'],
                                       clearances=player['clearances'],
                                       crossesBlocked=player['crossesBlocked'],
                                       passesBlocked=player['passesBlocked'],
                                       aerial=player['aerial'],
                                       goals=player['goals'],
                                       setPieceGoals=player['setPieceGoals'],
                                       shortPassAccuracy=player['shortPassAccuracy'],
                                       longPassAccuracy=player['longPassAccuracy'],
                                       totalCrosses=player['totalCrosses'],
                                       crossAccuracy=player['crossAccuracy'],
                                       keyPasses=player['keyPasses'],
                                       assists=player['assists'])
                po.player = player['playerObj']
            elif player['role'] == 'Forward':
                po = models.Forward(xp=player['xp'],
                                    apps=player['apps'],
                                    shotsOnTarget=player['shotsOnTarget'],
                                    shotsOffTarget=player['shotsOffTarget'],
                                    shotsBlocked=player['shotsBlocked'],
                                    shotsPost=player['shotsPost'],
                                    dribbling=player['dribbling'],
                                    aerial=player['aerial'],
                                    goals=player['goals'],
                                    setPieceGoals=player['setPieceGoals'],
                                    shortPassAccuracy=player['shortPassAccuracy'],
                                    longPassAccuracy=player['longPassAccuracy'],
                                    totalCrosses=player['totalCrosses'],
                                    crossAccuracy=player['crossAccuracy'],
                                    keyPasses=player['keyPasses'],
                                    assists=player['assists'])
                po.player = player['playerObj']
            elif player['role'] == 'Goalkeeper':
                po = models.Goalkeeper(xp=player['xp'],
                                       apps=player['apps'],
                                       clearances=player['clearances'],
                                       savesOutOfBox=player['savesOutOfBox'],
                                       savesPenaltyArea=player['savesPenaltyArea'],
                                       savesSixYardBox=player['savesSixYardBox'],
                                       aerial=player['aerial'])
                po.player = player['playerObj']
            else:
                logger.error('player %s has no role assigned' % player['name'])
                raise SystemExit
            self._session.add(po)
        self._session.commit()

        logger.info('successfully added players\' extra data based on role to database %s' % (self._name))

    def get_teams(self):
        teams = self._session.query(models.Team).all()
        return teams

    def get_players(self):
        players = self._session.query(models.Player).all()
        return players
