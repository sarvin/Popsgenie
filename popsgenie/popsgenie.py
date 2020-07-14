"""Module containing classes used to query Opsgenie APIs"""
import logging
import urllib

import requests

#import popsgenie.api_classes
#import popsgenie.page

from . import api_classes
from . import page

class Popsgenie():
    """Class for querying Opsgenie at API level"""
    logger = logging.getLogger(__name__)

    def __init__(self, opsgenie_url: str, api_key: str):
        self.session = api_key
        self.url_base = opsgenie_url # 'https://api.opsgenie.com/v2'

    @property
    def session(self) -> requests.sessions.Session:
        """Get a pre-authorized session object for repeated queries

        Returns:
            requests.sessions.Session -- a pre-authenticated session
            object used to query Opsgenie's API
        """
        return self.__session

    @session.setter
    def session(self, api_key: str) -> None:
        """Accept a valid Opsgenie API key and pre-authorize a
        session object with it. Useful for repeated queries against Opsgenie

        Arguments:
            api_key {str} -- A valid Opsgenie API key.
                See https://docs.opsgenie.com/docs/api-key-management
        """
        session = requests.Session()
        session.headers.update(
            {"Authorization": api_key}
        )

        self.__session = session

    def schedules(self, offset: int = 0, limit: int = 20) -> requests.models.Response:
        """used to get a list of opsgenie schedules

        Keyword Arguments:
            offset {int} -- offset for pagination (default: {0})
            limit {int} -- limit for pagination (default: {20})

        Returns:
            requests.models.Response -- object with .json() method
        """
        query_string = urllib.parse.urlencode({
            "offset": offset,
            "limit": limit})

        url = "/".join([self.url_base, "schedules"])
        url = url + '?' + query_string

        pages = page.PopsgeniePage(
            self.session,
            self.url_base,
            url,
            api_classes.PopsgenieSchedule)

        return pages

    def teams(self, offset: int = 0, limit: int = 20) -> requests.models.Response:
        """used to get a list of opsgenie users

        Keyword Arguments:
            offset {int} -- offset for pagination (default: {0})
            limit {int} -- limit for pagination (default: {20})

        Returns:
            requests.models.Response -- object with .json() method
        """
        query_string = urllib.parse.urlencode({
            "offset": offset,
            "limit": limit})

        url = "/".join([self.url_base, "teams"])
        url = url + '?' + query_string

        pages = page.PopsgeniePage(
            self.session,
            self.url_base,
            url,
            api_classes.PopsgenieTeam)

        return pages

    def users(self, offset: int = 0, limit: int = 20) -> requests.models.Response:
        """used to get a list of opsgenie users

        Keyword Arguments:
            offset {int} -- offset for pagination (default: {0})
            limit {int} -- limit for pagination (default: {20})

        Returns:
            requests.models.Response -- object with .json() method
        """
        query_string = urllib.parse.urlencode({
            "offset": offset,
            "limit": limit})

        url = "/".join([self.url_base, "users"])
        url = url + '?' + query_string

        pages = page.PopsgeniePage(
            self.session,
            self.url_base,
            url,
            api_classes.PopsgenieUser)

        return pages
