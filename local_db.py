import uuid
import time

import cons

from datetime import datetime


class Sportsbook(object):

    def __init__(self):

        #self.logs = client.evo.logs
        self.db = dict()

    def update_odds(self, event_id, line, bookmaker, odds, fractional_odds=None, _id=None, f=None):

        assert (isinstance(odds, float))

        self.db[event_id]['{0}.{1}_odds'.format(line, bookmaker)] = odds
        self.db[event_id]['{0}.{1}_ts'.format(line, bookmaker)] = time.time()
        self.db[event_id]['{0}.{1}_fractional_odds'.format(line, bookmaker)] = fractional_odds
        if _id is None and f is None:
            # we have only updates
            pass
        else:
            # first time when we populate with _id and f
            self.db[event_id]['{0}.{1}_id'.format(line, bookmaker)] = _id
            self.db[event_id]['{0}.{1}_f'.format(line, bookmaker)] = f

        log_line = '{0},{1},{2},{3}'.format(datetime.utcnow(), line, odds, bookmaker)
        #self.update_logs(event_id=event_id, log=log_line)

    def get_event_data(self, event_id):

        return self.db[event_id]

    def get_id(self, player_1, player_2, sport=None):
        player_1 = player_1.strip()
        player_2 = player_2.strip()
        comb1 = '{} v {}'.format(player_1, player_2)
        for event in self.db.keys():
            comb2 = '{} v {}'.format(self.db[event][cons.HOME_TEAM], self.db[event][cons.AWAY_TEAM])
            if fuzz.ratio(comb1, comb2) > cons.FUZZY_RATIO:
                if cons.SPORT not in self.db[event] and sport is not None:
                    self.db[event][cons.SPORT] = sport
                return event
        event_id = uuid.uuid4().hex
        self.db[event_id] = dict()
        self.db[event_id][cons.HOME_TEAM] =
        self.db[event_id][cons.AWAY_TEAM] = player_2
        self.db[event_id][cons.SPORT] = sport

        return event_id
