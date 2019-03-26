from sqlalchemy import Column, Integer, String, Unicode, ForeignKey, Float
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Player(Base):
    __tablename__ = 'player'
    id = Column('id', Integer(), primary_key=True)
    team_id = Column('team_id', ForeignKey('team.id'))
    name = Column('name', Unicode(50))
    url = Column('url', Unicode(100))
    role = Column('position', String(15))
    played_positions = Column('played_positions', String(15))
    age = Column('age', Integer())
    height = Column('height', Integer())
    weight = Column('weight', Integer())

class Team(Base):
    __tablename__ = 'team'
    id = Column('id', Integer(), primary_key=True)
    name = Column('name', Unicode(50))
    url = Column('url', Unicode(100))
    players = relationship(Player, backref=backref('team'))

class Defender(Base):
    __tablename__ = 'defender'
    xp = Column('xp', Integer())
    apps = Column('apps', Integer())
    tackling = Column('tackling', Float(precision=2))
    interceptions = Column('interceptions', Integer())
    clearances = Column('clearances', Integer())
    crossesBlocked = Column('crossesBlocked', Integer())
    passesBlocked = Column('passesBlocked', Integer())
    aerial = Column('aerial', Float(precision=2))
    goals = Column('goals', Integer())
    setPieceGoals = Column('setPieceGoals', Integer())
    shortPassAccuracy = Column('shortPassAccuracy', Float(precision=2))
    longPassAccuracy = Column('longPassAccuracy', Float(precision=2))
    totalCrosses = Column('totalCrosses', Integer())
    crossAccuracy = Column('crossAccuracy', Float(precision=2))
    keyPasses = ('keyPasses', Integer())
    assists = Column('assists', Integer())
    player = relationship(Player, backref=backref('defender', uselist=False))

class Midfielder(Base):
    __tablename__ = 'midfielder'
    xp = Column('xp', Integer())
    apps = Column('apps', Integer())
    shotsOnTarget = Column('shotsOnTarget', Integer())
    shotsOffTarget = Column('shotsOffTarget', Integer())
    shotsBlocked = Column('shotsBlocked', Integer())
    shotsPost = Column('shotsPost', Integer())
    dribbling = Column('dribbling', Float(precision=2))
    tackling = Column('tackling', Float(precision=2))
    interceptions = Column('interceptions', Integer())
    clearances = Column('clearances', Integer())
    crossesBlocked = Column('crossesBlocked', Integer())
    passesBlocked = Column('passesBlocked', Integer())
    aerial = Column('aerial', Float(precision=2))
    goals = Column('goals', Integer())
    setPieceGoals = Column('setPieceGoals', Integer())
    shortPassAccuracy = Column('shortPassAccuracy', Float(precision=2))
    longPassAccuracy = Column('longPassAccuracy', Float(precision=2))
    totalCrosses = Column('totalCrosses', Integer())
    crossAccuracy = Column('crossAccuracy', Float(precision=2))
    keyPasses = ('keyPasses', Integer())
    assists = Column('assists', Integer())
    player = relationship(Player, backref=backref('midfielder', uselist=False))

class Forward(Base):
    __tablename__ = 'forward'
    xp = Column('xp', Integer())
    apps = Column('apps', Integer())
    shotsOnTarget = Column('shotsOnTarget', Integer())
    shotsOffTarget = Column('shotsOffTarget', Integer())
    shotsBlocked = Column('shotsBlocked', Integer())
    shotsPost = Column('shotsPost', Integer())
    dribbling = Column('dribbling', Float(precision=2))
    aerial = Column('aerial', Float(precision=2))
    goals = Column('goals', Integer())
    setPieceGoals = Column('setPieceGoals', Integer())
    shortPassAccuracy = Column('shortPassAccuracy', Float(precision=2))
    longPassAccuracy = Column('longPassAccuracy', Float(precision=2))
    totalCrosses = Column('totalCrosses', Integer())
    crossAccuracy = Column('crossAccuracy', Float(precision=2))
    keyPasses = ('keyPasses', Integer())
    assists = Column('assists', Integer())
    player = relationship(Player, backref=backref('forward', uselist=False))
