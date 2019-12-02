import pickle
import json
import time
import datetime
import random

def write_to_file(filename, data):
    '''
    :param filename: name of the file; created in current dir as filename
    :param data: data to be written to file
    :return: True if successful, False if not
    ???file can be opened with: with openFile(filename)
    '''
    try:
        with open('%s' % filename, 'wb') as outfile:
            pickle.dump(data, outfile)
    except Exception as err:
        print(err)
        return False

    return True

def open_file(filename):
    '''
    :param filename: file to be opened
    :return: same data as writeToFile(data)
    '''
    try:
        with open('%s' % filename, 'rb') as infile:
            data = pickle.load(infile)

        return data
    except Exception as err:
        print(err)
        return False

def plr_obj_to_dict(players: list) -> list:
    plrs_dicts = list()
    for player in players:
        plr = dict()
        plr['playerObj'] = player
        plr['url'] = player.url
        plr['role'] = player.role
        plr['name'] = player.name
        plrs_dicts.append(plr)

    return plrs_dicts

def players_objects_to_dicts(players: list) -> list:
    dicts = list()
    for player in players:
        nd1 = vars(player.player)
        nd2 = vars(player)
        nd = {**nd1, **nd2}
        nd.pop('_sa_instance_state')
        nd.pop('player')
        nd.pop('team_id')
        nd.pop('id')
        nd.pop('player_id')
        dicts.append(nd)

    return dicts

def players_to_json(players: list, filename: str):
    with open('%s.json' % filename, 'w') as fp:
        json.dump(players, fp, sort_keys=True, indent=4)

    return True

def str_to_ts(s, format='%d/%m/%Y %H:%M:%S'):
    return time.mktime(
        datetime.datetime.strptime(s, format).timetuple()
    )

def rand_stake(stake, limit, interval):
    """Randomizes stake between (stake, stake - 2) with 0.5 interval
    :param stake: float > 0
    :param limit: stake - limit -> lowest possible stake to be returned > zero
    :param interval: float representing the increments between stake and stake - limit
    :return: new stake to be used in placing bet
    """
    possible_stakes = list()
    max_possible_stakes = (stake - (stake - limit)) / interval
    while stake > 0:
        possible_stakes.append(stake)
        stake -= interval
        if len(possible_stakes) > max_possible_stakes:
            break
    return random.choice(possible_stakes)
