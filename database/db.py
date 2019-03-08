from sqlalchemy import Column, Integer, Float, String, MetaData, Unicode, Table, create_engine
from sqlalchemy.sql import select

from utils import util


metadata = MetaData()

players = Table('players', metadata,
    Column('db_id', Integer(), primary_key=True),
    Column('id', Integer()),
    Column('name', Unicode(50)),
    Column('url', Unicode(100)),
    Column('position', String(15)),
    Column('age', Integer()),
    Column('height', Integer()),
    Column('weight', Integer()),
    Column('rating', Float(precision=2))
)

def init_db():
    eng = create_engine('sqlite:///players.db')
    metadata.create_all(eng)
    return eng

def add_players(con, players_list: list):
    ins = players.insert()
    result = con.execute(ins, players_list)
    return result

def get_players(con):
    slct = select([players.c.name, players.c.rating]).order_by(players.c.rating)
    rp = con.execute(slct)
    return rp


if __name__ == '__main__':
    engine = init_db()
    connection = engine.connect()
    # it_players = util.open_file('..//crawlers/italy_players')
    # add_players(con=connection, players_list=it_players)
    print(get_players(con=connection))