"""Unibet related code"""

import random
import re
import datetime
import hashlib
import time
import traceback

from utils import session
from utils import fingerprint
from utils import log
from utils import cons
from utils import util

logger = log.get_logger()


class BetClient(object):
    """Client for unibet"""

    def __init__(self, country_code, username, password, owner, max_bet=5, skip_over=8):

        self._username = username
        self._country_code = country_code
        self._session = self._new_session()
        self._password = password
        self._owner = owner
        self._max_bet = max_bet
        self._skip_over = skip_over

        if self._country_code == 'gb':
            self._domain = 'uk'
            self._url = 'www.unibet.co.uk'
        elif self._country_code == 'lt':
            self._domain = 'lt'
            self._url = 'lt.unibet-33.com'
        elif self._country_code == 'ro':
            self._domain = 'ro'
            self._url = 'www.unibet.ro'
        elif self._country_code == 'it':
            self._url = 'www.unibet.it'
            self._domain = 'it'
        elif self._country_code == 'at':
            self._url = 'de.unibet.com'
            self._domain = 'de'
        elif self._country_code == 'gr':
            self._url = 'gr.unibet-3.com'
            self._domain = 'gr'
        else:
            self._domain = 'com'
            self._url = 'www.unibet.com'

        self._market = None
        self._sid = None
        self._ticket = None
        self._jurisdiction = None
        self._id = None
        self._lang = None
        self._zero_bets = 0
        self._email = None
        self._currency = None
        self._kambi_domain = None
        self._fingerprint = fingerprint.newFingerprint(user_agent=cons.USER_AGENT_NT,
                                                       resolution=fingerprint.get_resolution(self.username), country_code=self._country_code)

    @property
    def bookmaker_name(self):
        return 'unibet'

    @property
    def username(self):
        return self._email if self._email else self._username

    @property
    def max_bet(self):
        return self._max_bet

    def _new_session(self):
        """Creates a request.Session() to be used by client for all requests
        :return: a new session configured with proxy of country = self._country_code if Proxy=True
        """
        headers = {
            cons.USER_AGENT_TAG: cons.USER_AGENT_NT,
            'Pragma': 'no-cache',
            'DNT': '1',
            'Cache-Control': 'no-cache'
        }
        ses = session.SessionFactory().build(headers=headers, country_code=self._country_code)

        return ses

    def login(self, retry=False):
        """
        :param retry: if False and function fails, it will call itself with retry=True; self._new_session is called if this happens
        :return: True if account successfully logged in and all data was set properly, False otherwise
        """
        logger.info('%s logging in...' % self.username)
        try:
            self._set_cookies()
        except Exception as err:
            logger.debug(err)
            logger.error('%s failed to set cookies' % self._username)
            if not retry:
                logger.info('%s recreating session' % self._username)
                self._session = self._new_session()
                return self.login(retry=True)
            else:
                logger.error('{0} login failed {1}'.format(self.username, err))
                return False

        url = 'https://%s/login-api/methods/password' % self._url
        headers = {
            'Content-Type': 'application/json',
            'Host': self._url,
            'X-Requested-With': 'XMLHttpRequest',
            'TE': 'Trailers'
        }
        data = {
            'brand': 'unibet',
            'captchaResponse': '',
            'captchaType': 'INVISIBLE',
            'channel': 'WEB',
            'client': 'polopoly',
            'clientVersion': 'desktop',
            'platform': 'desktop',
            'loginId': self.username,
            'loginSecret': self._password
        }
        try:
            resp = self._session.post(url=url, headers=headers, json=data)
            resp = resp.json()
            if 'challenge' in resp.keys():
                logger.error('%s encountered CAPTCHA: %s' % self.username, resp)
                return 'login failed'
            if 'message' in resp.keys():
                if resp['message'] == 'Authentication denied, invalid credentials':
                    logger.error('invalid credentials: %s' % self.username)
                elif resp['message'] == 'Authentication denied, customer is blocked':
                    logger.error('account blocked: %s' % self.username)
                else:
                    logger.error('unknown login failure: %s' % self.username)
                return 'login failed'
            if '.com' in self._username or '.at' in self._username or '.de' in self._username or '.eu' in self._username:
                self._email = self._username
                self._username = resp['userName']
        except Exception as err:
            if not retry:
                self._session = self._new_session()
                return self.login(retry=True)
            else:
                logger.error('{0} login failed {1}'.format(self.username, err))
                return False

        if not self._set_data():
            if not retry:
                self._session = self._new_session()
                return self.login(retry=True)
            else:
                return False

        if not self._get_kambi_session():
            if not retry:
                self._session = self._new_session()
                return self.login(retry=True)
            else:
                return False

        logger.info('successfully logged in ({0})'.format(self.username))
        return True

    def _set_data(self):
        """Sets self._market, self._ticket, self._id
        :return: True if successful, False otherwise
        """
        url = 'https://{0}/kambi-rest-api/gameLauncher2.json'.format(self._url)
        headers = {
            'Host': self._url,
            'TE': 'Trailers'
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
            self._kambi_domain = data['jurisdiction']
        except Exception as err:
            logger.error('{0} could not set data: {1}'.format(self.username, err))
            return False

        return True

    def _set_cookies(self):
        """Sets all cookies necessary for login"""
        resp = self._session.get(url='https://%s/betting/sports/home' % self._url)
        res = resp.content.decode('utf-8')
        res = res.split('cms.site')[1]
        self._lang = re.findall('countryCode: \'(.*)\',\n', res)[0]
        self._jurisdiction = re.findall('jurisdiction: \'(.*)\',\n', res)[0]
        self._currency = re.findall('code: \'(.*)\',\n', res)[0]
        url = 'https://%s/kambi-rest-api/gameLauncher2.json' % self._url
        headers = {
            'Host': self._url,
            'TE': 'Trailers'
        }
        params = {
            'useRealMoney': 'false',
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
        self._session.get(url=url, headers=headers, params=params)
        self._session.cookies.set(name='rememberMeName',
                                  value=self.username,
                                  domain=self._url)
        self._session.cookies.set(name='unibet.lang',
                                  value=self._lang,
                                  domain=self._url)

    def _get_kambi_session(self):
        """Sets the kambi session id necessary for using their api
        :return True if successful, False otherwise
        """
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
            'Host': '%s-auth.kambicdn.org' % self._kambi_domain,
            'Origin': 'https://%s' % self._url,
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'content-type',
            'Referer': 'https://%s/betting/sports/home' % self._url
        }
        try:
            self._session.options(url=url, headers=headers, params=params)
            del headers['Access-Control-Request-Method']
            del headers['Access-Control-Request-Headers']
            headers['Content-Type'] = 'application/json'
            resp = self._session.post(url=url, json=data, params=params, headers=headers)
            sID = resp.json()
            self._sid = sID['sessionId']
            return True
        except Exception as err:
            logger.error('{0} could not set kambi session: {1}'.format(self.username, err))
            return False

    def get_bet_history(self, start_date=None, end_date=None, days=None, bet_status=None):
        """Crawls betting history
        :param start_date: string format YYYY-MM-DD
        :param end_date: string format YYYY-MM-DD
        :param days: integer --> how many days to go back from current time
        :param bet_status: 'settled' or 'unsettled'
        :return: list of dicts, empty list if there are no bets
        """
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
        """Recursive function used by self.get_bet_history()
        :return: list of dicts with unprocessed bets
        """
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
            'toDate': end_date
        }
        if bet_status:
            params['status'] = bet_status
        now = datetime.datetime.now()
        headers = {
            'Origin': 'https://%s' % self._url,
            'Host': '%s-auth.kambicdn.org' % self._kambi_domain,
            'Referer': 'https://{}/betting/sports/bethistory/{}'.format(self._url, now.date())
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
        """
        :param bet: dict with unprocessed bet info
        :return: dict with the converted bet to be stocked in database
        """
        cbet = dict()
        cbet['ts'] = bet['placedDate'][8:10] + '/' + bet['placedDate'][5:7] + '/' + bet['placedDate'][0:4] + ' ' + bet['placedDate'][11:19]
        cbet['ts'] = util.str_to_ts(cbet['ts'])
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

    def get_balance(self, retry=False):
        """
        :param retry: if False and function fails, it will call itself with retry=True
        :return: the current account balance, as float; returns 0 if function failed twice
        """
        url = 'https://%s/wallitt/mainbalance' % self._url
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Host': self._url,
            'Referer': 'https://%s/betting/sports/home' % self._url,
            'TE': 'Trailers'
        }
        try:
            resp = self._session.get(url=url, headers=headers)
            res = resp.json()
            balance = res['balance']['cash']
            return float(balance)
        except Exception as err:
            if not retry:
                return self.get_balance(retry=True)
            else:
                logger.error('{0} failed to retrieve balance, error: {1}'.format(self._username, err))
                return 0

    def is_logged_in(self, retry=False):
        """
        :param retry: if False and function fails, it will call itself with retry=True
        :return: True if account currently logged in, False otherwise
        """
        url = 'https://xns.unibet.com/xns-service/secure/authenticate'
        if self._domain == 'lt':
            url = 'https://xns.unibet-33.com/xns-service/secure/authenticate'
        elif self._domain == 'uk':
            url = 'https://xns.unibet.co.uk/xns-service/secure/authenticate'
        elif self._domain == 'ro':
            url = 'https://xns.unibet.ro/xns-service/secure/authenticate'
        elif self._domain == 'it':
            url = 'https://xns.unibet.it/xns-service/secure/authenticate'
        message = self._username + '@unibet is authenticated'
        headers = {
            'Referer': 'https://%s/betting/sports/home' % self._url,
            'Origin': 'https://%s' % self._url,
            'TE': 'Trailers'
        }
        try:
            r = self._session.get(url=url, headers=headers, timeout=10)
            if r.content.decode('utf-8').lower() == message.lower():
                return True
            else:
                return False
        except Exception as err:
            if not retry:
                return self.is_logged_in(retry=True)
            else:
                logger.error('{0} could not check if logged in: {1}'.format(self.username, err))
                return False

    def crawl_deposits(self, from_date):
        """
        :param from_date: format='%d/%m/%Y %H:%M:%S'
        :return: list of deposits made
        """
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
        fromDate_ts = int(round(util.str_to_ts(from_date, '%d/%m/%Y') * 1000))
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
        """
        :param from_date: format='%d/%m/%Y %H:%M:%S'
        :return: list of withdrawals made
        """
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
        fromDate_ts = int(round(util.str_to_ts(from_date, '%d/%m/%Y') * 1000))
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
        """
        :param min_options: min number of options to be used; integer
        :param max_options: max number of options to be used; integer
        :param min_quote: the minimum quote chosen for options; float
        :param max_quote: the maximum quote chosen for options; float
        :param stake: stake used for placing the bet; float
        :return: place a random soccer combination bet
        """
        min_quote = min_quote * 1000
        max_quote = max_quote * 1000
        stake = stake * 1000
        if not self.is_logged_in():
            ret = self.login()
            if ret == 'login failed':
                return 'login failed'
            elif not ret:
                return False

        url = 'https://eu-offering.kambicdn.org/offering/v2018/%s/listView/football.json' % self._id
        params = {
            'lang': self._lang,
            'market': self._market,
            'client_id': 2,
            'channel_id': 1,
            'ncid': int(round(time.time() * 1000)),
            'useCombined': 'true'
        }
        headers = {
            'Origin': 'https://%s' % self._url,
            'Host': 'eu-offering.kambicdn.org',
            'Referer': 'https://%s/betting/sports/filter/football' % self._url
        }
        resp = self._session.get(url=url, params=params, headers=headers)
        resp = resp.json()
        all_events = resp['events']  # events is a list of dicts
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
            ret = self._get_option(event=prematch_events[index], min_quote=min_quote, max_quote=max_quote)
            if not ret:
                continue
            else:
                option, quote = ret
            if option:
                options.append(option)
                quotes.append(quote)
                i += 1
            del prematch_events[index]

        return self.place_bet(odds=quotes, options=options, stake=stake, is_rand_bet=True)

    @staticmethod
    def _get_option(event, min_quote, max_quote):
        """
        :param event: dict with info about soccer event
        :param min_quote: the minimum quote acceptable
        :param max_quote: the maximum quote acceptable
        :return: tuple with option id and option quote if any option fits the criteria, None otherwise
        """
        for offer in event['betOffers']:
            for option in offer['outcomes']:
                if (option['odds'] >= max_quote) or (option['odds'] <= min_quote):
                    pass
                else:
                    return option['id'], option['odds']

        return None

    @staticmethod
    def _create_betslip(offer, options, odds):
        """Called by self._prepare_bet()
        :param offer: resp with bet offers as list of dicts
        :param options: desired selections
        :param odds: quotes of the desired selections
        :return: betslip necessary for placing bet
        """
        betslip = list()
        index = 0
        for option, quote in zip(options, odds):
            outcome = dict()
            outcome['eachWayApproved'] = True
            outcome['fromBetBuilder'] = False
            outcome['isPrematchBetoffer'] = True
            outcome['oddsApproved'] = True
            outcome['isLiveBetoffer'] = False
            outcome['source'] = 'Event List View'
            outcome['betofferId'] = offer[index]['id']
            outcome['eventId'] = offer[index]['eventId']
            outcome['outcomeId'] = option
            outcome['id'] = option
            outcome['approvedOdds'] = quote
            betslip.append(outcome)

        return betslip

    def _prepare_bet(self, odds, options, index=0, retry=False):
        """Called by self.place_bet()
        :return: betslip data necessary for placing bet or None if function failed
        """
        url = 'https://eu-offering.kambicdn.org/offering/v2018/%s/betoffer/outcome.json' % self._id
        params = {
            'lang': self._lang,
            'market': self._market,
            'client_id': 2,
            'channel_id': 1,
            'ncid': int(round(time.time() * 1000)),
            'id': options[index]
        }
        headers = {
            'Origin': 'https://%s' % self._url,
            'Host': 'eu-offering.kambicdn.org'
        }
        try:
            self._session.get(url=url, params=params, headers=headers)
            params['ncid'] = int(round(time.time() * 1000))
            if index:
                params['id'] = list()
                for i in range(0, index):
                    params['id'].append(options[i])
            resp = self._session.get(url=url, params=params, headers=headers)
        except Exception as err:
            if not retry:
                return self._prepare_bet(odds=odds, options=options, index=index, retry=True)
            else:
                logger.error(traceback.print_tb(err.__traceback__))
                logger.error('%s failed to prepare betslip' % self._username)
                return None

        url = 'https://{}-auth.kambicdn.org/player/api/v2/{}/coupon/validate.json'.format(self._kambi_domain, self._id)
        url = url + ';jsessionid=' + self._sid
        params = {
            'lang': self._lang,
            'market': self._market,
            'client_id': 2,
            'channel_id': 1,
            'ncid': int(round(time.time() * 1000))
        }
        data = {'requestCoupon': {
                'type': 'RCT_SYSTEM',
                'odds': [],
                'outcomeIds': [],
                'betsPattern': '',
                'selection': []
            }
        }
        for i in range (0, index + 1):
            lista = list()
            lista.append(options[i])
            data['requestCoupon']['odds'].append(odds[i])
            data['requestCoupon']['outcomeIds'].append(lista)
            data['requestCoupon']['selection'].append(list())
        data['requestCoupon']['betsPattern'] = '1' * (pow(2, index + 1) - 1)
        headers = {
            'Origin': 'https://%s' % self._url,
            'Host': '%s-auth.kambicdn.org' % self._kambi_domain,
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'content-type'
        }
        try:
            self._session.options(url=url, params=params, headers=headers)
            del headers['Access-Control-Request-Method']
            del headers['Access-Control-Request-Headers']
            headers['Content-Type'] = 'application/json'
            self._session.post(url=url, params=params, json=data, headers=headers)
        except Exception as err:
            if not retry:
                return self._prepare_bet(odds=odds, options=options, index=index, retry=True)
            else:
                logger.error(traceback.print_tb(err.__traceback__))
                logger.error('%s failed to validate betslip' % self._username)
                return None

        if index + 1 == len(options):
            try:
                resp = resp.json()
                offer = resp['betOffers']
                return self._create_betslip(offer=offer, options=options, odds=odds)
            except Exception as err:
                logger.error(traceback.print_tb(err.__traceback__))
                logger.error('%s failed to create betslip' % self._username)
                return None
        else:
            index += 1
            return self._prepare_bet(odds=odds, options=options, index=index, retry=False)

    def place_bet(self, odds, options, stake=None, betslip=None, skipped=True, is_rand_bet=False):
        """
        :param odds: odds associated to options
        :param options: the options identification numbers
        :param stake: stake used to place bet; if None, self._max_bet is used
        :param betslip: returned by self._prepare_bet()
        :param skipped: if True, there is a self._sip_over percent chance that placing current bet is skipped
        :param is_rand_bet: True if place_bet was called by self.random_bet(), False otherwise
        :return: dict with placed bet info if bet placed successfully, False otherwise
        """
        if not isinstance(options, list):
            options = [options]
        if not isinstance(odds, list):
            odds = [odds]

        if skipped and not is_rand_bet:
            rand = random.randint(0, 100)
            if rand >= self._skip_over:
                pass
            else:
                logger.info('{} skipped over this bet: {}'.format(self.username, options))
                return None

        if not stake:
            if self._max_bet > 1:
                stake = util.rand_stake(stake=self._max_bet, limit=3, interval=1)
            else:
                stake = self._max_bet
            stake *= 1000
        if stake < 2000 and self._domain == 'it':
            stake = 2000

        if not self.is_logged_in():
            ret = self.login()
            if ret == 'login failed':
                return 'login failed'
            elif not ret:
                return None

        if not betslip:
            betslip = self._prepare_bet(odds=odds, options=options)
            if not betslip:
                return None

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
                'type': 'RCT_SINGLE' if len(options) == 1 else 'RCT_COMBINATION',
                'allowOddsChange': 'AOCT_NO',
                'odds': [],
                'stakes': [stake],
                'outcomeIds': [],
                'couponRewards': [],
                'selection': []
            },
            'trackingData': {
                'hasTeaser': False,
                'isBetBuilderCombination': False,
                'selectedOutcomes': betslip
            }
        }
        for i in range(0, len(options)):
            lista = list()
            lista.append(options[i])
            data['requestCoupon']['odds'].append(odds[i])
            data['requestCoupon']['outcomeIds'].append(lista)
            data['requestCoupon']['selection'].append(list())

        headers = {
            'Origin': 'https://{0}'.format(self._url),
            'Host': '{0}-auth.kambicdn.org'.format(self._kambi_domain),
            'Access-Control-Request-Method': 'PUT',
            'Access-Control-Request-Headers': 'content-type'
        }
        try:
            self._session.options(url=url, params=params, headers=headers)
            del headers['Access-Control-Request-Method']
            del headers['Access-Control-Request-Headers']
            headers['Content-Type'] = 'application/json'
            r = self._session.put(url=url, json=data, params=params, headers=headers)
        except Exception as err:
            logger.error(traceback.print_tb(err.__traceback__))
            logger.error('{0} failed to place bet {1}'.format(self._username, options))
            return None

        try:
            resp = r.json()
        except:
            logger.info('can not convert the bet response to json\nthe response is: %s' % r)
            if r.status_code == 409:
                logger.info('odds have changed')
                return None
            else:
                return stake / 1000
        if r.status_code != 201:
            if r.status_code == 409:
                if resp['responseCoupon']['betErrors'][0]['errors'][0]['type'] == 'VET_STAKE_TOO_HIGH':
                    self._zero_bets += 1
                    if self._zero_bets >= 3:
                        msg = 'unibet: {0} is limited to ZERO'.format(self._username)
                        logger.error(msg)
                        return 'account is limited'
                    else:
                        logger.info('{0} limit is ZERO for {1} bet'.format(self._username, options))
                        return None
                else:
                    logger.info('%s odds have changed' % self.username)
                    return None
            elif r.status_code == 300:
                stake = int(float(resp['responseCoupon']['betErrors'][0]['errors'][0]['arguments'][0]) / 1000)
                stake = stake * 1000
                if stake == 0:
                    logger.info('%s can not place bet with ZERO stake' % self.username)
                    return None
                else:
                    return self.place_bet(odds=odds, stake=stake, options=options, betslip=betslip, skipped=False)
            elif resp['error']['message'] == 'Unauthorized':
                ret = self.login()
                if ret == 'login failed':
                    return 'login failed'
                elif not ret:
                    return None
                else:
                    return self.place_bet(odds=odds, stake=stake, options=options, betslip=betslip, skipped=False)

        self._zero_bets = 0
        return stake / 1000
