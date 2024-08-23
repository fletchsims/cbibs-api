"""CBIBS Module"""
import requests

DEFAULT_DOMAIN = 'mw.buoybay.noaa.gov'


class CbibsModule:
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
        self.session=None
        return False
