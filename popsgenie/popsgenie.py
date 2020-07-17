"""Module containing classes used to query Opsgenie APIs"""
import logging
from urllib import parse

import requests

from . import resource, tool

#logger = logging.getLogger('popsgenie')


class Popsgenie():
    """Class for querying Opsgenie at API level"""
    logger = logging.getLogger(__name__)

    def __init__(self, api_key: str, opsgenie_url: str = 'https://api.opsgenie.com/v2'):
        session = requests.Session()
        session.headers.update(
            {"Authorization": api_key}
        )

        self.connection = tool.Connection(session=session, url_base=opsgenie_url)

    def schedules(
            self,
            identifier: str = None,
            identifier_type: str = None,
            offset: int = 0,
            limit: int = 20) -> tool.Pages:
        """List opsgenie schedules in the form of Schedule objects

        Args:
            identifier (str, optional): The name or id of a schedule. Defaults to None.
            identifier_type (str, optional): The type of identifier used.
                Values are either 'name' or 'id'. Defaults to None.
            offset (int, optional): offset for pagination. Defaults to 0.
            limit (int, optional): limit for pagination. Defaults to 20.

        Returns:
            page.PopsgeniePage: iterable that returns lists of Schedule objects
        """
        url_parts = [self.connection.url_base, "schedules"]
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

        pages = tool.Pages(
            connection=self.connection,
            url=url,
            PopsgenieClass=resource.Schedule)

        return pages

    def teams(
            self,
            identifier: str = None,
            identifier_type: str = None,
            offset: int = 0,
            limit: int = 20) -> tool.Pages:
        """List opsgenie teams in the form of Team objects

        Args:
            identifier (str, optional): The name or id of a team. Defaults to None.
            identifier_type (str, optional): The type of identifier used.
                Values are either 'name' or 'id'. Defaults to None.
            offset (int, optional): offset for pagination. Defaults to 0.
            limit (int, optional): limit for pagination. Defaults to 20.

        Returns:
            page.PopsgeniePage: iterable that returns lists of Team objects
        """
        url_parts = [self.connection.url_base, "teams"]
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

        pages = tool.Pages(
            connection=self.connection,
            url=url,
            PopsgenieClass=resource.Team)

        return pages

    def users(
            self,
            identifier: str = None,
            identifier_type: str = None,
            offset: int = 0,
            limit: int = 20) -> tool.Pages:
        """List opsgenie users in the form of User objects

        Args:
            identifier (str, optional): The name or id of a user. Defaults to None.
            identifier_type (str, optional): The type of identifier used.
                Values are either 'username' or 'id'. Defaults to None.
            offset (int, optional): offset for pagination. Defaults to 0.
            limit (int, optional): limit for pagination. Defaults to 20.

        Returns:
            page.PopsgeniePage: iterable that returns lists of User objects
        """
        url_parts = [self.connection.url_base, "users"]
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

        pages = tool.Pages(
            connection=self.connection.session,
            url=url,
            PopsgenieClass=resource.User)

        return pages
