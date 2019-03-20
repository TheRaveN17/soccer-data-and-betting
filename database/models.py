from sqlalchemy import Column, Integer, String, Unicode, ForeignKey
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
