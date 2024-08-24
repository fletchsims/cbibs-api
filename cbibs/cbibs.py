"""CBIBS Module"""
import requests

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
        pass

    def _parse_request(self, query, params):
        if not isinstance(query, str):
            raise InvalidInputError(bad_value=query)
        data = {'q': query, 'key': self.key}
        data.update(params)
        return data
