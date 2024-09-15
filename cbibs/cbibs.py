"""CBIBS Module"""
import sys

import requests
import requests.packages

from version import __version__

DEFAULT_DOMAIN = 'mw.buoybay.noaa.gov'


class CbibsApiError(Exception):
    """Base class for all errors/exceptions"""


class InvalidInputError(CbibsApiError):
    """
    There was a problem with the input you provided.

    :var bad_value: The value that caused the problem
    """

    def __init__(self, bad_value):
        super().__init__()
        self.bad_value = bad_value

    def __unicode__(self):
        return "Input must be a unicode string, not " + repr(self.bad_value)[:100]

    __str__ = __unicode__


class UnknownError(CbibsApiError):
    """There is a problem with CBIBS server."""


class CbibsModule:
    session = None

    def __init__(self, key, protocol='https'):
        self.key = key
        if protocol and protocol not in ('http', 'https'):
            protocol = 'https'
        self.url = protocol + "://" + DEFAULT_DOMAIN + '/api/v1/'

    def __enter__(self):
        self.session = requests.Session()
        return self

    def __exit__(self, *args):
        self.session.close()
        self.session = None
        return False

    def cbibs(self, query, **kwargs):
        raw_response = kwargs.pop('raw_response', False)
        request = self._parse_request(query, kwargs)
        response = self._cbibs_request(request)
        if raw_response:
            return response

    def _parse_request(self, query, params):
        if not isinstance(query, str):
            raise InvalidInputError(bad_value=query)
        data = {'q': query, 'key': self.key}
        data.update(params)
        return data

    def _cbibs_request(self, params):
        response = requests.get(self.url, params=params, headers=self._cbibs_headers('requests'))
        try:
            response_json = response.json()
        except ValueError as excinfo:
            raise UnknownError("Non-JSON result from server") from excinfo
        return response_json

    def _cbibs_headers(self, client):
        if client == 'requests':
            client_version = requests.__version__

        return {
            'User-Agent': 'cbibs-python/%s Python/%s %s/%s' % (
                __version__,
                '.'.join(str(x) for x in sys.version_info[0:3]),
                client,
                client_version
            )
        }


class CbibsAdapter:
    def __init__(self, api_key: str = '', protocol: str = 'https', ver: str = 'v1'):
        self._api_key = api_key
        if protocol and protocol not in ('http', 'https'):
            protocol = 'https'
        self.url = protocol + "://" + DEFAULT_DOMAIN + '/api/' + ver + '/'

    def __enter__(self):
        self.session = requests.Session()
        return self

    def __exit__(self, *args):
        self.session.close()
        self.session = None
        return False
