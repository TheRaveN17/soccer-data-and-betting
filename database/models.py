from sqlalchemy import Column, Integer, Float, String, Unicode, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Player(Base):
    __tablename__ = 'players'
    player_id = Column('player_id', Integer(), primary_key=True)
    team_id = Column('team_id', ForeignKey('teams.team_id'))
    name = Column('name', Unicode(50))
    url = Column('url', Unicode(100))
    position = Column('position', String(15))
    played_positions = Column('played_positions', String(15))
    age = Column('age', Integer())
    height = Column('height', Integer())
    weight = Column('weight', Integer())
    rating = Column('rating', Float(precision=2))
    team = relationship('Team', backref=backref('players', order_by=player_id))

class Team(Base):
    __tablename__ = 'teams'
    team_id = Column('team_id', Integer(), primary_key=True)
    name = Column('name', Unicode(50))
    url = Column('url', Unicode(100))
