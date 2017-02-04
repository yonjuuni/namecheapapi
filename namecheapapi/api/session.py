"""
"""
import re
from datetime import datetime
from urllib.parse import urlencode
from urllib.request import urlopen, Request
from xml.etree.ElementTree import fromstring
from xml.etree.ElementTree import tostring
from xml.etree.ElementTree import Element
from namecheapapi.api.exceptions import NCApiError


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
        self.warnings = []
        self.coupon = coupon
        self.gmt_offset = None

    @property
    def _base_params(self) -> dict:

        return {
            'ApiUser': self.api_user,
            'ApiKey': self.api_key,
            'Username': self.username,
            'ClientIp': self.client_ip,
        }

    def _get_gmt_offset(self) -> None:
        if not self.gmt_offset:
            xml = fromstring(self.raw_query())
            self.gmt_offset = int(re.findall(
                r'-?\d+', xml.find(self._tag('GMTTimeDifference')).text)[0])
        return self.gmt_offset

    def _form_query(self, command: str, query: dict) -> str:

        return urlencode({
            **self._base_params,
            "Command": command,
            **query
        })

    def _call(self, command: str, query: dict = {},
              raw: bool = False, post: bool = False) -> Element:
        """Send GET or POST request with the API call

        Arguments:
            command -- NC API command
            query -- key/value pairs for GET request
            raw -- used in raw_query method. Makes the method return a
                raw XML string
            post -- setting to True sends a POST requests instead of GET

        Returns:
            raw=False -- ElementTree.Element object in CommandResponse
                namespace
            raw=True -- full XML response string

        Raises:
            NCApiError if response Status equals to 'ERROR'.
        """

        if post:
            url = self.url
            data = self._form_query(command, query).encode('ascii')
            raw_xml = urlopen(Request(url, data)).read().decode('utf-8')
        else:
            url = self.url + self._form_query(command, query)
            raw_xml = urlopen(url).read().decode('utf-8')

        xml = fromstring(raw_xml)

        if xml.get('Status') == 'ERROR':
            self._log_error(xml, url)
            error_message = ', '.join(
                ["Error {}: '{}'".format(item['Number'], item['Text'])
                 for item in self.errors[-1]['Errors']])
            raise NCApiError(error_message)

        if xml.find(self._tag('Warnings')).findall(self._tag('Warning')):
            self._log_warning(xml, url)

        if raw:
            return raw_xml

        return xml.find(self._tag('CommandResponse'))

    def _tag(self, tag: str) -> str:
        """Create tag to navigate through ElementTree.Element object.
        """
        return '{{{}}}{}'.format(NAMESPACE, tag)

    def _log_error(self, xml: Element, url: str) -> None:
        """Log an API error.

        Adds errors to session.errors list.
        """

        data = {
            'URL': url,
            'XML': tostring(xml, encoding='unicode'),
            'Time': datetime.now(),
            'Errors': [],
        }

        for error in xml.find(self._tag('Errors')).findall(self._tag('Error')):
            data['Errors'].append({
                'Number': error.get('Number'),
                'Text': error.text
            })

        command = xml.find(self._tag('RequestedCommand'))
        data['RequestedCommand'] = command.text

        server = xml.find(self._tag('Server'))
        data['Server'] = server.text

        exectime = xml.find(self._tag('ExecutionTime'))
        data['ExecutionTime'] = float(exectime.text)

        self.errors.append(data)

    def _log_warning(self, xml: Element, url: str) -> None:
        """Log an API warning.

        Adds warnings to session.warnings list.
        """

        data = {
            'URL': url,
            'XML': tostring(xml, encoding='unicode'),
            'Time': datetime.now(),
            'Warnings': []
        }

        for warning in xml.find(self._tag('Warnings')).findall(
                self._tag('Warning')):
            data['Warnings'].append({
                'Number': warning.get('Number'),
                'Text': warning.text
            })

        command = xml.find(self._tag('RequestedCommand'))
        data['RequestedCommand'] = command.text

        server = xml.find(self._tag('Server'))
        data['Server'] = server.text

        exectime = xml.find(self._tag('ExecutionTime'))
        data['ExecutionTime'] = float(exectime.text)

        self.warnings.append(data)

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
