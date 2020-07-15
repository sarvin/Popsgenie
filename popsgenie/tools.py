"""Generate an iterator for "paging" through list calls"""
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

        self.logger.debug("url_next=%s", self.url_next)

        response = self.session.get(self.url_next)
        json = response.json()

        self.url_next = json.get('paging', {}).get('next', None)

        api_objects = []
        if isinstance(json['data'], dict):
            api_objects = [
                self.api_class(
                    session=self.session,
                    opsgenie_url=self.url_base,
                    **json['data'])]
        else:
            api_objects = [
                self.api_class(
                    session=self.session,
                    opsgenie_url=self.url_base,
                    **api_data)
                for api_data in json['data']]

        return api_objects
