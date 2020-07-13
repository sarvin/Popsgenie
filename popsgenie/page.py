import logging

import requests

class PopsgeniePage():
    """Class for paging over Opsgenie data"""
    logger = logging.getLogger(__name__)

    def __init__(self, session: requests.sessions.Session, url_base: str, url: str, PopsgenieClass):
        self.session = session
        self.url_base = url_base
        self.url_start = url
        self.url_next = url
        self.api_class = PopsgenieClass

    def __iter__(self):
        return self

    def __next__(self):
        if self.url_next is None:
            self.url_next = self.url_start
            raise StopIteration

        self.logger.debug("url=%s", self.url_next)

        response = self.session.get(self.url_next)
        json = response.json()

        if json.get('paging', {}).get('next'):
            self.url_next = json.get('paging', {}).get('next')

        else:
            self.url_next = None

        api_objects = [
            self.api_class(self.session, self.url_base, **api_data)
            for api_data in json['data']]

        return api_objects

