'''Unibet related code'''

import random
import re
import datetime
import hashlib
import time

from utils import cons
from utils import session
from utils import fingerprint
from utils import log

logger = log.get_logger()

class BetClient(object):
    """Client for unibet"""

    def __init__(self, country_code, username, password, owner, max_bet=5, skip_over=8):

        self._username = username
        self._user_agent = self._get_user_agent()
        self._country_code = country_code
        self._session = self._new_session()
        self._password = password
        self._owner = owner
        self._max_bet = max_bet
        self._skip_over = skip_over

        if self._country_code == 'gb':
            self._domain = 'uk'
            self._url = 'www.unibet.co.uk'
            self._currency = 'GBP'
            self._kambi_domain = 'al'
        elif self._country_code == 'lt':
            self._domain = 'lt'
            self._url = 'lt.unibet-33.com'
            self._currency = 'EUR'
            self._kambi_domain = 'mt'
        elif self._country_code == 'ro':
            self._domain = 'ro'
            self._url = 'www.unibet.ro'
            self._currency = 'RON'
            self._kambi_domain = 'mt'
        elif self._country_code == 'it':
            self._url = 'www.unibet.it'
            self._currency = 'EUR'
            self._kambi_domain = 'mt'
            self._domain = 'it'
        elif self._country_code == 'at':
            self._url = 'de.unibet.com'
            self._currency = 'EUR'
            self._kambi_domain = 'mt'
            self._domain = 'de'
        else:
            self._domain = 'com'
            self._url = 'www.unibet.com'
            self._currency = 'EUR'
            self._kambi_domain = 'mt'

        self._market = None
        self._sid = None
        self._ticket = None
        self._jurisdiction = None
        self._id = None
        self._lang = None
        self._zero_bets = 0
        self._email = None
        self._fingerprint = fingerprint.newFingerprint(user_agent=self._user_agent, resolution=self._get_resolution(), country_code=self._country_code)

    @property
    def bookmaker_name(self):
        return 'unibet'

    @property
    def username(self):
        return self._username

    @property
    def email(self):
        return self._email

    @property
    def max_bet(self):
        return self._max_bet

    def _new_session(self):
        '''
        :return: a new session configured with proxy of country = self._country_code
        '''
        return session.SessionFactory().build(headers={cons.USER_AGENT_TAG: self._user_agent}, proxy=True, country_code=self._country_code)

    def login(self, retry=False):
        '''
        :param retry: if False and function fails, it will call itself with retry=True; self._new_session is called if this happens
        :return: True if account successfully logged in and all data was set properly, False otherwise
        '''

        logger.info('logging in ({0})...'.format(self._username))

        try:
            self._session.cookies.clear()
        except:
            pass
        self._set_cookies()

        url = 'https://{0}/login-api/methods/password'.format(self._url)
        headers = {
            'Referer': 'https://{0}/'.format(self._url),
            'Content-Type': 'application/json',
            'Host': self._url,
            'X-Requested-With': 'XMLHttpRequest'
        }
        data = {
            'brand': 'unibet',
            'captchaResponse': '',
            'captchaType': 'INVISIBLE',
            'channel': 'WEB',
            'client': 'polopoly',
            'clientVersion': 'desktop',
            'platform': 'desktop',
            'loginId': self._email if self._email else self._username,
            'loginSecret': self._password
        }
        try:
            resp = self._session.post(url=url, headers=headers, json=data)
            resp = resp.json()
            if 'challenge' in resp.keys():
                logger.error('CAPTCHA encountered: %s' % resp)
                return 'login failed'
            if 'message' in resp.keys() and resp['message'] == 'Authentication denied, invalid credentials':
                logger.error('invalid credentials: %s' % self._username)
                return 'login failed'
            if '.com' in self._username:
                self._email = self._username
                self._username = resp['userName']
            self._jurisdiction = resp['jurisdiction']
            self._lang = resp['locale']
        except Exception as err:
            if not retry:
                self._session = self._new_session()
                self.login(retry=True)
            logger.error('{0} login failed {1}'.format(self._username, err))
            return 'login failed'

        if not self._set_data():
            if not retry:
                self._session = self._new_session()
                self.login(retry=True)
            return False

        if not self._get_sessionID():
            if not retry:
                self._session = self._new_session()
                self.login(retry=True)
            return False

        logger.info('successfully logged in ({0})'.format(self._username))
        return True

    def _set_data(self):
        '''
        sets self._market, self._ticket, self._id
        :return: True if successful, False otherwise
        '''

        url = 'https://{0}/kambi-rest-api/gameLauncher2.json'.format(self._url)
        headers = {
            'Referer': 'https://{0}/betting'.format(self._url),
            'Host': self._url,
            'X-Requested-With': 'XMLHttpRequest'
        }
        params = {
            'useRealMoney': 'true',
            'locale': self._lang,
            'jurisdiction': self._jurisdiction,
            'brand': 'unibet',
            'currency': self._currency,
            'clientId': 'polopoly_desktop',
            'deviceGroup': 'desktop',
            'loadHTML5client': 'true',
            'deviceOs': '',
            'enablePoolBetting': 'false',
            'marketLocale': self._lang,
            '_': int(round(time.time() * 1000))
        }
        try:
            data = self._session.get(url=url, headers=headers, params=params)
            data = data.json()
            self._market = data['market']
            self._ticket = data['authtoken']
            self._id = data['offering']
        except Exception as err:
            logger.error('{0} could not set data: {1}'.format(self._username, err))
            return False

        return True

    def _set_cookies(self):

        url = 'https://{}/'.format(self._url)
        headers = {'Host': '{}'.format(self._url)}
        self._session.get(url=url, headers=headers)
        if self._domain == 'de':
            return True

        url = 'https://consent.cookiebot.com/logconsent.ashx'
        headers = {
            'Host': 'consent.cookiebot.com',
            'Referer': 'https://{0}/'.format(self._url)
        }
        params = {
            'action': 'accept',
            'cbid': 'b5b8a13f-3aeb-4f5d-8106-6e3807c93d7e',
            'clm': 'true',
            'clp': 'true',
            'cls': 'true',
            'dnt': 'false',
            'method': 'strict',
            'referer': 'https://{0}/'.format(self._url),
            'no-cache': int(round(time.time() * 1000))
        }
        resp = self._session.get(url=url, params=params, headers=headers)
        value = re.findall("{stamp:'(.*)=='.*", resp.text)
        cookieConsent = "{stamp:'"
        cookieConsent += value[0]
        cookieConsent += "==',necessary:true,preferences:true,statistics:true,marketing:true,ver:1}"
        now = datetime.datetime.now()
        expires = now + datetime.timedelta(days=365)
        expires = int(time.mktime(expires.timetuple()))
        self._session.cookies.set(name='CookieConsent',
                                  value=cookieConsent,
                                  domain='{0}'.format(self._url),
                                  expires=expires)

        return True

    def _get_sessionID(self):
        '''
        sets self._sid, the session id necessary for crawling and placing bets
        :return: True if successful, False otherwise
        '''

        data = {
            'attributes': {'fingerprintHash': self._fingerprint},
            'punterId': self._username + '@unibet',
            'streamingAllowed': True,
            'ticket': self._ticket,
            'market': self._market
        }
        params = {
            'settings': 'true',
            'lang': self._lang
        }
        url = 'https://{0}-auth.kambicdn.org/player/api/v2/{1}/punter/login.json'.format(self._kambi_domain, self._id)
        headers = {
            'Host': '{0}-auth.kambicdn.org'.format(self._kambi_domain),
            'Origin': 'https://{0}'.format(self._url),
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'content-type'
        }
        try:
            self._session.options(url=url, headers=headers, params=params)
            headers = {
                'Host': '{0}-auth.kambicdn.org'.format(self._kambi_domain),
                'Content-Type': 'application/json',
                'Origin': 'https://{0}'.format(self._url),
                'Referer': 'https://{0}/betting'.format(self._url)
            }
            resp = self._session.post(url=url, json=data, params=params, headers=headers)
            sID = resp.json()
            self._sid = sID['sessionId']
            return True
        except Exception as err:
            logger.error('Could not retrieve jsessionid ({0})'.format(err))
            return False

    def get_bet_history(self, start_date=None, end_date=None, days=None, bet_status=None):
        '''
        :param start_date: string format YYYY-MM-DD; end_date also has to be passed
        :param end_date: string format YYYY-MM-DD; start_date also has to be passed
        :param days: integer, last number of days to be crawled; if days is not None, start_date and end_date are overwritten
        :param bet_status: either settled for all settled bets, unsettled for all unsettled bets or None for all bets
        :return: list of dicts with converted bets (see self._bet_convert)
        '''

        if days is not None:
            end_date = datetime.datetime.now() + datetime.timedelta(days = 1)
            start_date = end_date - datetime.timedelta(days = days + 1)

            end_date = end_date.strftime('%Y-%m-%d')

        else:
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')

        bets = list()
        self._crawl_bets(end_date, start_date, bet_status, bets)

        bets_sorted = list()
        for bet in bets:
            bet_date = bet['placedDate'][:10]
            bet_date = datetime.datetime.strptime(bet_date, '%Y-%m-%d')
            if bet_date >= start_date:
                bets_sorted.append(self._bet_convert(bet))
            else:
                pass

        return bets_sorted

    def _crawl_bets(self, end_date, start_date, bet_status, bets, count=0):
        '''
        recursive function used by self.get_bet_history()
        :return: list of dicts with unprocessed bets
        '''

        url = 'https://{0}-auth.kambicdn.org/player/api/v2/{1}/coupon/summary.json'.format(self._kambi_domain, self._id)
        url = url + ';jsessionid=' + self._sid
        range_start = 50 * count
        params = {
            'lang': self._lang,
            'market': self._market,
            'client_id': 2,
            'channel_id': 1,
            'ncid': int(round(time.time() * 1000)),
            'range_size': 50,
            'range_start': range_start,
            'toDate': end_date,
            'status': bet_status
        }
        headers = {
            'Origin': 'https://{0}'.format(self._url),
            'Host': '{0}-auth.kambicdn.org'.format(self._kambi_domain),
            'Referer': 'https://{0}/betting'.format(self._url)
        }
        r = self._session.get(url=url, params=params, headers=headers)
        if r.status_code == 404:
            return bets
        history = r.json()
        history = history['historySummaryCoupons']
        last_date = history[-1]['placedDate']
        last_date = last_date[:10]
        last_date = datetime.datetime.strptime(last_date, '%Y-%m-%d')
        bets += history

        if last_date >= start_date:
            count += 1
            self._crawl_bets(end_date, start_date, bet_status, bets, count)
        else:
            return bets

    def _bet_convert(self, bet):
        '''
        :param bet: dict with unprocessed bet info
        :return: dict with the converted bet to be stocked in database
        '''

        cbet = dict()
        cbet['ts'] = bet['placedDate'][8:10] + '/' + bet['placedDate'][5:7] + '/' + bet['placedDate'][0:4] + ' ' + bet['placedDate'][11:19]
        cbet['ts'] = self._str_to_ts(cbet['ts'])
        cbet['bookmaker'] = self.bookmaker_name
        if not self._email:
            cbet['username'] = self._username
        else:
            cbet['username'] = self._email
        cbet['stake'] = float(bet['stake']) / 1000
        cbet['event'] = bet['outcomes'][0]['eventName']
        try:
            cbet['id'] = hashlib.md5(self._username.encode('utf-8') + str(bet['singleBetId']).encode('utf-8')).hexdigest()
        except:
            cbet['id'] = hashlib.md5(self._username.encode('utf-8') + str(bet['bets'][0]['betId']).encode('utf-8')).hexdigest()
        cbet['database_id'] = self._owner
        if bet['bets'][0]['betStatus'] == 1:
            cbet['odds'] = float(bet['bets'][0]['betOdds']) / 1000
            cbet['result'] = None
        elif bet['bets'][0]['betStatus'] == 2:
            cbet['odds'] = float(bet['bets'][0]['betOdds']) / 1000
            cbet['result'] = float(bet['payout']) / 1000
        elif bet['bets'][0]['betStatus'] == 3:
            cbet['odds'] = float(bet['outcomes'][0]['playedOdds']) / 1000
            cbet['result'] = 0
        else:
            cbet['odds'] = float(bet['outcomes'][0]['playedOdds']) / 1000
            cbet['result'] = cbet['stake']
        return cbet

    @staticmethod
    def _str_to_ts(s, format='%d/%m/%Y %H:%M:%S'):
        return time.mktime(datetime.datetime.strptime(s, format).timetuple())

    def get_balance(self, retry=False):
        '''
        :param retry: if False and function fails, it will call itself with retry=True
        :return: the current account balance, as float; returns 0 if function failed twice
        '''

        url = 'https://{0}/wallitt/mainbalance'.format(self._url)
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Host': self._url,
            'Referer': 'https://{0}/betting'.format(self._url)
        }
        try:
            resp = self._session.get(url=url, headers=headers)
            balance = resp.json()
            balance = balance['balance']['cash']
            return float(balance)
        except Exception as err:
            if not retry:
                self.get_balance(retry=True)
            logger.error('{0} failed to retrieve balance, error: {1}'.format(self._username, err))
            return 0

    def is_logged_in(self, retry=False):
        '''
        :param retry: if False and function fails, it will call itself with retry=True
        :return: True if account currently logged in, False otherwise
        '''

        url = 'https://xns.unibet.com/xns-service/secure/authenticate'
        host = 'xns.unibet.com'
        if self._domain == 'lt':
            url = 'https://xns.unibet-33.com/xns-service/secure/authenticate'
            host = 'xns.unibet-33.com'
        elif self._domain == 'uk':
            url = 'https://xns.unibet.co.uk/xns-service/secure/authenticate'
            host = 'xns.unibet.co.uk'
        elif self._domain == 'ro':
            url = 'https://xns.unibet.ro/xns-service/secure/authenticate'
            host = 'xns.unibet.ro'
        elif self._domain == 'it':
            url = 'https://xns.unibet.it/xns-service/secure/authenticate'
            host = 'xns.unibet.it'
        message = self._username + '@unibet is authenticated'
        headers = {
            'Host': host,
            'Referer': 'https://{0}/'.format(self._url),
            'Origin': 'https://{0}'.format(self._url)
        }
        try:
            r = self._session.get(url=url, headers=headers, timeout=10)
            if r.content.decode('utf-8').lower() == message.lower():
                return True
            else:
                return False
        except Exception as err:
            if not retry:
                self.is_logged_in(retry=True)
            logger.error('{0} could not check if logged in: {1}'.format(self._username, err))
            return False

    def _get_user_agent(self):
        '''
        :return: fake user_agent to be used with account; see fingerprint.py
        '''

        s = 0
        for c in self._username:
            s += ord(c)
        s = str(s)
        user_agents = fingerprint.user_agents

        index = int(s) % 13
        return user_agents[index]

    def _get_resolution(self):
        '''
        :return: fake screen resolution to be used with account; see fingerprint.py
        '''

        resolutions = fingerprint.resolutions
        s = 0
        for c in self._username:
            s += ord(c)

        return resolutions[s % 4]

    def crawl_deposits(self, from_date):
        '''
        :param from_date: format='%d/%m/%Y %H:%M:%S'
        :return: list of deposits made
        '''

        url = 'https://{0}/myaccount/mygamingactivity/accounthistory'.format(self._url)
        headers = {
            'Referer': 'https://{0}/'.format(self._url),
            'Host': self._url
        }
        self._session.get(url=url, headers=headers)

        url = 'https://{0}/payment-history/external-api/transaction/list'.format(self._url)
        headers = {
            'Referer': 'https://{0}/myaccount/mygamingactivity/accounthistory'.format(self._url),
            'Content-Type': 'application/json',
            'Host': self._url,
            'Origin': 'https://{0}'.format(self._url)
        }
        today_ts = int(round(time.mktime(datetime.datetime.strptime(
                str(datetime.datetime.today()).split('.')[0],'%Y-%m-%d %H:%M:%S').timetuple()) * 1000))
        fromDate_ts = int(round(self._str_to_ts(from_date, '%d/%m/%Y') * 1000))
        params = {
            'fromDate': fromDate_ts,
            'pageIndex': 0,
            'pageSize': 20,
            'sysName': 'CMS',
            'toDate': today_ts,
            'type': 'DEPOSIT'
        }
        resp = self._session.get(url=url, headers=headers, params=params)
        resp = resp.json()

        return resp['transactions']

    def crawl_withdrawals(self, from_date):
        '''
        :param from_date: format='%d/%m/%Y %H:%M:%S'
        :return: list of withdrawals made
        '''

        url = 'https://{0}/myaccount/mygamingactivity/accounthistory'.format(self._url)
        headers = {
            'Referer': 'https://{0}/'.format(self._url),
            'Host': self._url
        }
        self._session.get(url=url, headers=headers)

        url = 'https://{0}/payment-history/external-api/transaction/list'.format(self._url)
        headers = {
            'Referer': 'https://{0}/myaccount/mygamingactivity/accounthistory'.format(self._url),
            'Content-Type': 'application/json',
            'Host': self._url,
            'Origin': 'https://{0}'.format(self._url)
        }
        today_ts = int(round(time.mktime(datetime.datetime.strptime(
                str(datetime.datetime.today()).split('.')[0],'%Y-%m-%d %H:%M:%S').timetuple()) * 1000))
        fromDate_ts = int(round(self._str_to_ts(from_date, '%d/%m/%Y') * 1000))
        params = {
            'fromDate': fromDate_ts,
            'pageIndex': 0,
            'pageSize': 20,
            'sysName': 'CMS',
            'toDate': today_ts,
            'type': 'WITHDRAWAL'
        }
        resp = self._session.get(url=url, headers=headers, params=params)
        resp = resp.json()

        return resp['transactions']

    def random_bet(self, min_options, max_options, min_quote, max_quote, stake):
        '''
        :param min_options: min number of options to be used; integer
        :param max_options: max number of options to be used; integer
        :param min_quote: the minimum quote chosen for options; float
        :param max_quote: the maximum quote chosen for options; float
        :param stake: stake used for placing the bet; float
        :return: place a random soccer combination bet
        '''
        min_quote = min_quote * 1000
        max_quote = max_quote * 1000
        stake = stake * 1000

        url = 'https://eu-offering.kambicdn.org/offering/api/v3/{0}/listView/football.json'.format(self._id)
        params = {
            'lang': self._lang,
            'market': self._market,
            'client_id': 2,
            'channel_id': 1,
            'ncid': int(round(time.time() * 1000)),
            'categoryGroup': 'COMBINED',
            'displayDefault': 'true'
        }
        headers = {
            'Origin': 'https://{0}'.format(self._url),
            'Host': 'eu-offering.kambicdn.org',
            'Referer': 'https://{0}/betting'.format(self._url)
        }
        resp = self._session.get(url=url, params=params, headers=headers)
        resp = resp.json()
        all_events = resp['events'] #events is a list of dicts
        prematch_events = list()
        for event in all_events:
            if 'liveData' not in list(event.keys()):
                prematch_events.append(event)

        nr_options = random.randint(min_options, max_options)
        options = list()
        quotes = list()
        i = 0
        while i < nr_options:
            index = random.randint(0, len(prematch_events) - 1)
            option, quote = self._get_option(event=prematch_events[index], min_quote=min_quote, max_quote=max_quote)
            if option:
                options.append(option)
                quotes.append(quote)
                i += 1
            del prematch_events[index]

        return self.place_bet(odds=quotes, options=options, stake=stake, rand_bet=True)

    @staticmethod
    def _get_option(event, min_quote, max_quote):
        '''
        :param event: dict with info about soccer event
        :param min_quote: the minimum quote acceptable
        :param max_quote: the maximum quote acceptable
        :return: tuple with option id and option quote if any option fits the criteria, None otherwise
        '''

        for offer in event['betOffers']:
            for option in offer['outcomes']:
                if (option['odds'] >= max_quote) or (option['odds'] <= min_quote):
                    pass
                else:
                    return option['id'], option['odds']

        return None

    @staticmethod
    def _get_betslip_data(info, odds, options):
        '''
        :return: data to be used when simulating betslip
        '''

        big_data = []
        for index in range (0, len(info['events'])):
            path = []
            for i in info['events'][index]['path']:
                path.append(i['id'])
            data = {
                'live': False,
                'odds': odds[index],
                'eventId': info['events'][index]['id'],
                'eventStartTime': info['events'][index]['start'],
                'outcomeId': options[index],
                'criterionId': info['betoffers'][index]['criterion']['id'],
                'eventGroupIdPath': path
            }
            big_data.append(data)

        return big_data

    def _approve_bet(self, data):

        url = 'https://{0}-auth.kambicdn.com/player/api/v2/{1}/coupon/approval.json'.format(self._kambi_domain, self._id)
        url = url + ';jsessionid=' + self._sid
        params = {
            'lang': self._lang,
            'market': self._market,
            'channel_id': 1,
            'client_id': 2,
            'ncid': int(round(time.time() * 1000))
        }
        data['alternativeUri'] = '/coupon/approval.json'
        data['requestCoupon']['wholeStakeSentToPBA'] = True

        headers = {
            'Origin': 'https://{0}'.format(self._url),
            'Host': '{0}-auth.kambicdn.com'.format(self._kambi_domain),
            'Access-Control-Request-Method': 'PUT',
            'Access-Control-Request-Headers': 'content-type'
        }
        self._session.options(url=url, params=params, headers=headers)

        headers = {
            'Origin': 'https://{0}'.format(self._url),
            'Host': '{0}-auth.kambicdn.com'.format(self._kambi_domain),
            'Referer': 'https://{0}/betting'.format(self._url),
            'Content-Type': 'application/json'
        }
        resp = self._session.put(url=url, json=data, params=params, headers=headers)

        if resp.status_code == 202:
            return resp.content
        else:
            return False

    def _prepare_bet(self, odds, options, index=0, retry=False):
        '''
        :return: simulates the creation of a betslip to reduce bot detection
        '''

        url = 'https://eu-offering.kambicdn.org/offering/api/v2/{0}/betoffer/outcome.json'.format(self._id)
        params = {
            'lang': self._lang,
            'market': self._market,
            'client_id': 2,
            'channel_id': 1,
            'ncid': int(round(time.time() * 1000)),
            'includeLive': 'true',
            'id': options[index]
        }
        headers = {
            'Origin': 'https://{0}'.format(self._url),
            'Host': 'eu-offering.kambicdn.org',
            'Referer': 'https://{0}/betting'.format(self._url)
        }
        self._session.get(url=url, params=params, headers=headers)
        params['ncid'] = int(round(time.time() * 1000))
        if index == 0:
            pass
        else:
            params['id'] = list()
            for i in range (0, index):
                params['id'].append(options[i])

        resp = self._session.get(url=url, params=params, headers=headers)
        info = resp.json()
        big_data = self._get_betslip_data(info=info, odds=odds, options=options)

        url = 'https://{0}-auth.kambicdn.org/player/api/v2/{1}/coupon/validate.json'.format(self._kambi_domain, self._id)
        url = url + ';jsessionid=' + self._sid
        params = {
            'lang': self._lang,
            'market': self._market,
            'client_id': 2,
            'channel_id': 1,
            'ncid': int(round(time.time() * 1000))
        }
        data = {'requestCoupon':
            {
                'type': 'RCT_SYSTEM',
                'odds': [],
                'outcomeIds': [],
                'betsPattern': '',
                'selections': []
            },
            'validRewardsRequest': {'couponRows': big_data}
        }
        for i in range (0, index + 1):
            lista = list()
            lista.append(options[i])
            data['requestCoupon']['odds'].append(odds[i])
            data['requestCoupon']['outcomeIds'].append(lista)
            data['requestCoupon']['selections'].append('')
        data['requestCoupon']['betsPattern'] = '1' * (pow(2, index + 1) - 1)

        headers = {
            'Origin': 'https://{0}'.format(self._url),
            'Host': '{0}-auth.kambicdn.org'.format(self._kambi_domain),
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'content-type'
        }
        self._session.options(url=url, params=params, headers=headers)

        headers = {
            'Origin': 'https://{0}'.format(self._url),
            'Host': '{0}-auth.kambicdn.org'.format(self._kambi_domain),
            'Referer': 'https://{0}/betting'.format(self._url),
            'Content-Type': 'application/json'
        }
        try:
            self._session.post(url=url, params=params, json=data, headers=headers)
        except Exception as err:
            if not retry:
                self._prepare_bet(odds, options, retry=True)
            logger.error('{0} failed to prepare bet {1}'.format(self._username, err))
            return False

        if index + 1 >= len(options):
            return True
        else:
            index += 1
            self._prepare_bet(odds=odds, options=options, index=index)

    def place_bet(self, odds, options, stake=None, bet_prepared=False, skipped=True, rand_bet=False):
        '''
        :param odds: odds associated to options
        :param options: the options identification numbers
        :param stake: stake used to place bet; if None, self._max_bet is used
        :param bet_prepared: False if betslip was not simulated, True otherwise
        :param skipped: if True, there is a self._sip_over percent chance that placing current bet is skipped
        :param rand_bet: True if place_bet was called by self.random_bet(), False otherwise
        :return: dict with placed bet info if bet placed successfully, False otherwise
        '''

        if not isinstance(options, list):
            lista = list()
            lista.append(options)
            options = lista
        if not isinstance(odds, list):
            lista = list()
            lista.append(odds)
            odds = lista

        if skipped and not rand_bet:
            rand = random.randint(0, 100)
            if rand >= self._skip_over:
               pass
            else:
                logger.info('skipped over this bet: {0}'.format(options))
                return False

        if not stake:
            stake = self._max_bet * 1000
            if (stake - 2000) > 0:
                rand = random.randint(0, 2)
                stake -= rand * 1000
            elif (stake - 1000) > 0:
                rand = random.randint(0, 1)
                stake -= rand * 1000
        if stake < 2000 and self._domain == 'it':
            stake = 2000

        if not self.is_logged_in():
            if self.login() == 'login failed':
                return 'login failed'
            return self.place_bet(odds=odds, stake=stake, options=options, skipped=False)

        if not bet_prepared:
            self._prepare_bet(odds=odds, options=options)

        url = 'https://{0}-auth.kambicdn.org/player/api/v2/{1}/coupon.json'.format(self._kambi_domain, self._id)
        url = url + ';jsessionid=' + self._sid
        params = {
            'lang': self._lang,
            'market': self._market,
            'channel_id': 1,
            'client_id': 2,
            'ncid': int(round(time.time() * 1000))
        }
        data = {
            'id': 1,
            'requestCoupon': {
                'type': '',
                'allowOddsChange': 'AOCT_NO',  # adica nu
                'odds': [],
                'stakes': [stake],  # 1000 e unu
                'outcomeIds': [],
                'couponRewards': [],
                'selection': []
            }
        }
        if len(options) == 1:
            data['requestCoupon']['type'] = 'RCT_SINGLE' # adica fara combinatii
            data['requestCoupon']['eachWayFraction'] = [-1]
            data['requestCoupon']['eachWayPlaceLimit'] = [-1]
        else:
            data['requestCoupon']['type'] = 'RCT_COMBINATION'
        for i in range (0, len(options)):
            lista = list()
            lista.append(options[i])
            data['requestCoupon']['odds'].append(odds[i])
            data['requestCoupon']['outcomeIds'].append(lista)
            data['requestCoupon']['selection'].append(None)

        headers = {
            'Origin': 'https://{0}'.format(self._url),
            'Host': '{0}-auth.kambicdn.org'.format(self._kambi_domain),
            'Access-Control-Request-Method': 'PUT',
            'Access-Control-Request-Headers': 'content-type'
        }
        self._session.options(url=url, params=params, headers=headers)

        headers = {
            'Origin': 'https://{0}'.format(self._url),
            'Host': '{0}-auth.kambicdn.org'.format(self._kambi_domain),
            'Referer': 'https://{0}/betting'.format(self._url),
            'Content-Type': 'application/json'
        }
        r = self._session.put(url=url, json=data, params=params, headers=headers)

        try:
            resp = r.json()
        except:
            logger.info('can not convert the bet response to json\nthe response is: %s' % r)
            if r.status_code == 409:
                logger.info('odds have changed')
                return False
            else:
                return {'responseCoupon': {'historyCoupon': {'stake': stake}}}
        if r.status_code != 201:
            if r.status_code == 409:
                if resp['responseCoupon']['betErrors'][0]['errors'][0]['type'] == 'VET_STAKE_TOO_HIGH':
                    self._zero_bets += 1
                    if self._zero_bets >= 3:
                        msg = '{0} is limited to ZERO'.format(self._username)
                        logger.error(msg)
                        return 'account is limited'
                    else:
                        logger.info('{0} limit is ZERO for {1} bet'.format(self._username, options))
                    return False
                logger.info('odds have changed')
                return False
            elif r.status_code == 300:
                if data['requestCoupon']['type'] == 'RCT_COMBINATION':
                    return self._approve_bet(data=data)
                else:
                    pass
                stake = int(float(resp['responseCoupon']['betErrors'][0]['errors'][0]['arguments'][0]) / 1000)
                stake = stake * 1000
                if stake == 0:
                    logger.info('can not place bet with ZERO stake')
                    return False
                else:
                    return self.place_bet(odds=odds, stake=stake, options=options, bet_prepared=True, skipped=False)
            elif resp['error']['message'] == 'Unauthorized':
                if self.login() == 'login failed':
                    return 'login failed'
                return self.place_bet(odds=odds, stake=stake, options=options, skipped=False)

        self._zero_bets = 0
        if not rand_bet:
            rn = random.randint(1, 100)
            if rn >= 90: #in 10% of cases, after placing a normal bet, place a random bet
                self.random_bet(min_options=2, max_options=4, min_quote=1.5, max_quote=3, stake=1)

        return resp
