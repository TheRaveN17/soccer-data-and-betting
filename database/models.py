from sqlalchemy import Column, Integer, Float, String, MetaData, Unicode, Table, ForeignKey

metadata = MetaData()

players = Table('players', metadata,
    Column('player_id', Integer(), primary_key=True),
    Column('team_id', ForeignKey('teams.team_id')),
    Column('name', Unicode(50)),
    Column('url', Unicode(100)),
    Column('position', String(15)),
    Column('playedPositions', String(15)),
    Column('age', Integer()),
    Column('height', Integer()),
    Column('weight', Integer()),
    Column('rating', Float(precision=2))
)

teams = Table('teams', metadata,
    Column('team_id', Integer(), primary_key=True),
    Column('name', Unicode(50)),
    Column('url', Unicode(100))
)
