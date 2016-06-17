from urllib.parse import urlencode
from urllib.request import urlopen
from xml.etree.ElementTree import fromstring


URLS = {
    'production': 'https://api.namecheap.com/xml.response?',
    'sandbox': 'https://api.sandbox.namecheap.com/xml.response?'
}


class Session:

    def __init__(self, api_user: str, api_key: str, username: str,
                 client_ip: str, sandbox: bool = True) -> None:
        self.api_user = api_user
        self.api_key = api_key
        self.username = username
        self.client_ip = client_ip
        self.url = URLS['sandbox' if sandbox else 'production']

    @property
    def _base_params(self) -> dict:
        return {
            'ApiUser': self.api_user,
            'ApiKey': self.api_key,
            'Username': self.username,
            'ClientIp': self.client_ip,
        }

    def _call(self, command: str, query: dict = {}) -> str:
        url = self.url + urlencode({
            **self._base_params,
            "Command": command,
            **query
        })
        print(url)
        return urlopen(url).read().decode('utf-8')

    def _parse_xml(self):
        pass
