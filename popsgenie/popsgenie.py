"""Module containing classes used to query Opsgenie APIs"""
from abc import ABC
import logging
from urllib import parse

import requests

from . import api_classes, page


class Popsgenie(ABC):
    """Class for querying Opsgenie at API level"""
    logger = logging.getLogger(__name__)

    def __init__(self, api_key: str, opsgenie_url: str = 'https://api.opsgenie.com/v2'):
        session = requests.Session()
        session.headers.update(
            {"Authorization": api_key}
        )

        self.__session = session

        self.url_base = opsgenie_url

    @property
    def session(self) -> requests.sessions.Session:
        """Get a pre-authorized session object for repeated queries

        Returns:
            requests.sessions.Session -- a pre-authenticated session
            object used to query Opsgenie's API
        """
        return self.__session

    def schedules(
            self,
            identifier: str = None,
            identifier_type: str = None,
            offset: int = 0,
            limit: int = 20) -> page.PopsgeniePage:
        """List opsgenie schedules in the form of PopsgenieSchedule objects

        Args:
            identifier (str, optional): The name or id of a schedule. Defaults to None.
            identifier_type (str, optional): The type of identifier used.
                Values are either 'name' or 'id'. Defaults to None.
            offset (int, optional): offset for pagination. Defaults to 0.
            limit (int, optional): limit for pagination. Defaults to 20.

        Returns:
            page.PopsgeniePage: iterable that returns lists of PopsgenieSchedule objects
        """
        url_parts = [self.url_base, "schedules"]
        parameters: dict = {
            "offset": offset,
            "limit": limit}

        if identifier_type in ['id', 'name']:
            parameters['identifierType'] = identifier_type
        if identifier:
            url_parts.append(parse.quote(identifier))

        query_string = parse.urlencode(parameters)

        url = "/".join(url_parts)
        url = url + '?' + query_string

        pages = page.PopsgeniePage(
            self.session,
            self.url_base,
            url,
            api_classes.PopsgenieSchedule)

        return pages

    def teams(
            self,
            identifier: str = None,
            identifier_type: str = None,
            offset: int = 0,
            limit: int = 20) -> page.PopsgeniePage:
        """List opsgenie teams in the form of PopsgenieTeam objects

        Args:
            identifier (str, optional): The name or id of a team. Defaults to None.
            identifier_type (str, optional): The type of identifier used.
                Values are either 'name' or 'id'. Defaults to None.
            offset (int, optional): offset for pagination. Defaults to 0.
            limit (int, optional): limit for pagination. Defaults to 20.

        Returns:
            page.PopsgeniePage: iterable that returns lists of PopsgenieTeam objects
        """
        url_parts = [self.url_base, "teams"]
        parameters: dict = {
            "offset": offset,
            "limit": limit}

        if identifier_type in ['id', 'name']:
            parameters['identifierType'] = identifier_type
        if identifier:
            url_parts.append(parse.quote(identifier))

        query_string = parse.urlencode(parameters)

        url = "/".join(url_parts)
        url = url + '?' + query_string

        pages = page.PopsgeniePage(
            self.session,
            self.url_base,
            url,
            api_classes.PopsgenieTeam)

        return pages

    def users(
            self,
            identifier: str = None,
            identifier_type: str = None,
            offset: int = 0,
            limit: int = 20) -> page.PopsgeniePage:
        """List opsgenie users in the form of PopsgenieUser objects

        Args:
            identifier (str, optional): The name or id of a user. Defaults to None.
            identifier_type (str, optional): The type of identifier used.
                Values are either 'username' or 'id'. Defaults to None.
            offset (int, optional): offset for pagination. Defaults to 0.
            limit (int, optional): limit for pagination. Defaults to 20.

        Returns:
            page.PopsgeniePage: iterable that returns lists of PopsgenieUser objects
        """
        url_parts = [self.url_base, "users"]
        parameters: dict = {
            "offset": offset,
            "limit": limit}

        if identifier_type in ['id', 'username']:
            parameters['identifierType'] = identifier_type
        if identifier:
            url_parts.append(parse.quote(identifier))

        query_string = parse.urlencode(parameters)

        url = "/".join(url_parts)
        url = url + '?' + query_string

        pages = page.PopsgeniePage(
            self.session,
            self.url_base,
            url,
            api_classes.PopsgenieUser)

        return pages
