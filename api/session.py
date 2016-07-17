"""
"""

from urllib.parse import urlencode
from urllib.request import urlopen
from xml.etree.ElementTree import fromstring
from xml.etree.ElementTree import Element
from api.exceptions import NCApiError


URLS = {
    'production': 'https://api.namecheap.com/xml.response?',
    'sandbox': 'https://api.sandbox.namecheap.com/xml.response?'
}

NAMESPACE = 'http://api.namecheap.com/xml.response'


class Session:
    """Session class.

    Defines the basic connection parameters and has several methods to
    process the information received via API.
    """

    def __init__(self, api_user: str, api_key: str, username: str,
                 client_ip: str, sandbox: bool = True,
                 coupon: str = None) -> None:
        """API initialization.

        Arguments:
            api_user -- NC API username.
            api_key -- NC API key.
            username -- your Namecheap username (in most cases).
            client_ip -- public IP address of the machine making API
                calls (MUST be whitelisted in your Namecheap account).
            sandbox -- optional argument. Should be set to True for
                testing and False on production.
            coupon -- coupon code, if you wish to use one. None by
                default.

        """
        self.api_user = api_user
        self.api_key = api_key
        self.username = username
        self.client_ip = client_ip
        self.url = URLS['sandbox' if sandbox else 'production']
        self.errors = []
        self.coupon = coupon

    @property
    def _base_params(self) -> dict:

        return {
            'ApiUser': self.api_user,
            'ApiKey': self.api_key,
            'Username': self.username,
            'ClientIp': self.client_ip,
        }

    def _form_url(self, command: str, query: dict) -> str:

        return self.url + urlencode({
            **self._base_params,
            "Command": command,
            **query
        })

    def _call(self, command: str, query: dict = {},
              raw: bool = False)-> Element:
        """Send GET request with the API call

        Arguments:
            command -- NC API command
            query -- key/value pairs for GET request
            raw -- used in raw_query method. Makes the method return a
                raw XML string

        Returns:
            raw=False -- ElementTree.Element object in CommandResponse
                namespace
            raw=True -- full XML response string

        Raises:
            NCApiError if response Status equals to 'ERROR'.
        """

        url = self._form_url(command, query)
        print(url)  # debug

        raw_xml = urlopen(url).read().decode('utf-8')

        if raw:
            return raw_xml
        else:
            xml = fromstring(raw_xml)

        if xml.attrib['Status'] == 'ERROR':
            self._log_error(xml)
            raise NCApiError(self.errors[-1])
        else:
            return xml.find(self._tag('CommandResponse'))

    def _tag(self, tag: str) -> str:
        """Create tag to navigate through ElementTree.Element object.
        """
        return '{{{}}}{}'.format(NAMESPACE, tag)

    def _log_error(self, xml: Element) -> None:
        """Log an API error.

        Adds errors and warnings to session.errors list.
        """

        data = {
            'Errors': [],
            'Warnings': []
        }

        for error in xml.find(self._tag('Errors')).findall(self._tag('Error')):
            data['Errors'].append({
                'Number': error.attrib['Number'],
                'Text': error.text
            })

        for warning in xml.find(self._tag('Warnings')).findall(
                self._tag('Warning')):
            data['Warnings'].append({
                'Number': warning.attrib['Number'],
                'Text': warning.text
            })

        command = xml.find(self._tag('RequestedCommand'))
        data['RequestedCommand'] = command.text

        server = xml.find(self._tag('Server'))
        data['Server'] = server.text

        exectime = xml.find(self._tag('ExecutionTime'))
        data['ExecutionTime'] = float(exectime.text)

        self.errors.append(data)

    def raw_query(self, command: str = '', query: dict = {}) -> str:
        """Create a custom query.

        Base parameters (API key, API user, etc.) are included by
        default.

        Arguments:
            command -- NC API command, separate from the rest of the
                query.
            query -- dict with key/value pairs for GET request.

        Returns:
            raw XML string.
        """
        return self._call(command, query, raw=True)
