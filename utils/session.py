import socket
import uuid
import requests


class SessionFactory(object):

    def build(self, headers: dict, proxy: bool=False, country_code: str=None) -> requests.Session:
        """Configures and returns a session object.
        :param headers: desired headers for the new session object
        :param proxy: set this to True if you want to use a proxy
                      if is True, country parameter also has to be passed
        :param country_code: two-letter iso code of desired proxy's origin, exp >> pl
        """
        if proxy:
            proxy_url = self._get_proxy_url(country_code)
            session = self._build(headers=headers, http_proxy=proxy_url, https_proxy=proxy_url)
        else:
            session =self._build(headers=headers)

        return session

    @staticmethod
    def _build(headers: dict, http_proxy: str=None, https_proxy: str=None) -> requests.Session:
        """Configures and returns a session object.
        :param http_proxy: the proxy to be used for http connections
        :param https_proxy: the proxy to be used for https connections
        :param headers: a dict of headers to be added to the every request
        :returns: a session object
        """
        proxies = {
            'http': http_proxy,
            'https': https_proxy
        }
        session = requests.Session()
        session.headers.update(headers)
        if http_proxy and https_proxy:
            session.proxies.update(proxies)
        return session

    @staticmethod
    def _get_proxy_url(country_code: str) -> str:
        """Returns a proxy url to the specified country.
        Example:
        get_proxy_url('gr')
        :param country_code: the country code
        :returns: url needed to connect to proxy
        """
        proxy_ip = socket.gethostbyname('servercountry-gb.zproxy.luminati.io')
        rand = str(uuid.uuid4()).replace('-', '')
        return 'http://your_proxy-' \
               'country-{0}-dns-remote-session-{1}:339d479bc57f@{2}:22225'.format(
            country_code, rand, proxy_ip)
