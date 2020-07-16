"""Represent data in Opsgenie with Popsgenie Classes"""
from abc import ABC
import datetime
import logging
from typing import Dict, List, Optional, Union

import requests


class Base(ABC):
    """Base class used to represent resources returned
    by the Opsgenie API https://docs.opsgenie.com/docs/api-overview
    At a minimum each subclass is required to implement
    self.lookup_attributes and skip_attributes as empty lists.
    The subclass's attributes reflect the resource's fields returned by
    Opsgenie *except* when the attribute is included in skip_attributes.
    If on initialization an instance of a subclass did not recieve data, for an attribute,
    data will be queried if the attribute's name is included in self.lookup_attributes.
    """
    def __init__(
            self,
            session: requests.sessions.Session,
            opsgenie_url: str,
            resource_name: str = None,
            **kwargs):
        """Abstract class for Opsgenie resources

        Args:
            session (requests.sessions.Session): an pre-authorized session object
            opsgenie_url (str): The base url for Opsgenie (I don't see this ever being required)
            resource (str, optional): The Opsgenie resource the class is representing.
                If the default value (None) is used an instance will throw an error if a resource is
                queried. In this case an instance of the class should contain all required data.
                Defaults to None.

            All other key word arguments are used to generate an instance's attributes.

        Raises:
            AttributeError: thrown when an attribute already exists and cannot be
                added during instance init.
        """
        self.__session = session
        self.opsgenie_url = opsgenie_url
        self.__resource_name: Optional[str] = resource_name


        # keep an updated list of object's attributes
        # this can get updated after a web request
        self._context = kwargs

        for key in kwargs:
            if key not in self.skip_attributes:
                try:
                    setattr(self, key, kwargs[key])
                except AttributeError as error:
                    raise AttributeError(f"{error}: {key}")

    def __repr__(self):
        return "%s(%r)" % (self.__class__, self.id)

    @property
    def lookup_attributes(self) -> List[str]:
        """list of object attributes that
        may not exist but can be queried from provider
        """
        return self.__lookup_attributes

    @lookup_attributes.setter
    def lookup_attributes(self, attribute_names: List[str]):
        """Declare a list of attributes that should be queried,
        from provider, and stored as object attributes
        """
        self.__lookup_attributes = attribute_names

    @property
    def skip_attributes(self) -> List[str]:
        """store list of attributes that should skipped
        when exposing attributes through self.attribute.
        This allows us to create a method/property with the
        same name as the attribute.
        """
        return self.__skip_attributes

    @skip_attributes.setter
    def skip_attributes(self, attribute_names: List[str]):
        """Declare a list of attributes that should skipped
        when exposing attributes through self.<attribute>.
        This allows us to create a method/property with the
        same name as the attribute.
        """
        self.__skip_attributes = attribute_names

    def __getattr__(self, key: str):
        """Some attributes are pre-set when the object is instantiated.
        Others aren't available on initialization and require a query.
        This method allows us to query only when the attribute is required.
        In some cases this can save us a web request.
        """
        if key in self.lookup_attributes:
            self.query_attributes(self.resource_url())

        return self.__getattribute__(key)

    @property
    def session(self) -> requests.sessions.Session:
        """Get a pre-authorized session object for repeated queries

        Returns:
            requests.sessions.Session -- a pre-authenticated session
            object used to query Opsgenie's API
        """
        return self.__session

    def query_attributes(self, context_url: str, **kwargs):
        """Used for importing data from Opsgenie to set an object's
        missing attribute values.

        Args:
            context_url (str): The Opsgenie API endpoint used
                to query data.

        Raises:
            AttributeError: If unable to set an attribute
                (more than likely because it exists as a property)
                throw the underlying error.
        """
        self.logger.debug("url=%s", context_url)

        response = self.session.get(context_url, **kwargs)
        json = response.json()

        # Update our context with the latest information
        self._context = json['data']

        for key in json['data'].keys():
            if key not in self.skip_attributes:
                try:
                    setattr(self, key, response.json()['data'][key])
                except AttributeError:
                    raise AttributeError(f"can't set attribute: {key}")

    def resource_url(self) -> str:
        """String declaring the resource's API endpoing

        Returns:
            str: value suitable for querying resource data
        """
        url = "/".join(
            [self.opsgenie_url, self.__resource_name, self.id]) # type: ignore

        return url


class Schedule(Base):
    """Class representing a Schedule in Opsgenie
    https://docs.opsgenie.com/docs/schedule-api
    """
    logger = logging.getLogger(__name__)
    resource_name = 'schedules'

    def __init__(self, *args, **kwargs):
        self.__team: Optional[Team] = None
        self.__on_calls: Optional[List['User']] = None
        self.__rotations: Optional[List[Rotation]] = None

        self.lookup_attributes = [
            'name',
            'description',
            'timezone',
            'enabled',
            'ownerTeam',
        ]
        self.skip_attributes = ['rotations']

        super().__init__(*args, resource_name=self.resource_name, **kwargs)

    @property
    def rotations(self) -> List['Rotation']:
        """Returns the raw data for a Opsgenie rotation
        associated with a schedule

        Returns:
            List[dict]: raw response from Opsgenie
        """
        if self.__rotations is None:
            self.query_attributes(self.resource_url())
            self.__rotations = [
                Rotation(self.session, self.opsgenie_url, **rotation_data)
                for rotation_data in self._context['rotations']
            ]

        return self.__rotations

    @property
    def team(self) -> 'Team':
        """Query Opsgenie for the team associated with a
        schedule and convert raw data to Team

        Returns:
            Team: an object representing a Team
                in Opsgenie
        """
        if self.__team is None:
            url = "/".join(
                [self.opsgenie_url, "teams", self.ownerTeam['id']]
            )

            self.logger.debug("url=%s", url)

            response = self.session.get(url)
            self.__team = Team(self.session, self.opsgenie_url, **response.json()['data'])

        return self.__team

    @property
    def on_calls(self) -> List['User']:
        """Retrieve users on call for a Schedule

        Returns:
            List[User]: Users on call in a schedule
        """
        if self.__on_calls is None:
            url = "/".join(
                [self.resource_url(), "on-calls"])

            self.logger.debug("url=%s", url)

            response = self.session.get(url)

            self.__on_calls = [
                User(self.session, self.opsgenie_url, **user_data)
                for user_data in response.json()['data']['onCallParticipants']
            ]

        return self.__on_calls


class Rotation(Base):
    """Class representing a schedule's rotation in Opsgenie
    https://docs.opsgenie.com/docs/schedule-api#section-schedule-rotation-fields

    This class makes no external queries
    """
    logger = logging.getLogger(__name__)

    def __init__(self, *args, **kwargs):
        self.__participants: Optional[List[Union['Team', 'User', dict]]] = None
        self.lookup_attributes = []
        self.skip_attributes = ['participants']

        super().__init__(*args, **kwargs)

    @property
    def participants(self) -> List[Union['Team', 'User', dict]]:
        """Retrive a list of Opsgenie Users associated
        with the rotation

        Returns:
            List[User]: List containing Opsgenie
            users
        """
        if self.__participants is None:
            self.__participants = []

            for participant in self._context.get('participants', []):
                if participant['type'] == 'user':
                    self.__participants.append(
                        User(self.session, self.opsgenie_url, **participant))
                elif participant['type'] == 'team':
                    self.__participants.append(
                        Team(self.session, self.opsgenie_url, **participant))
                else:
                    # Haven't witnessed participant['type'] == [escalation | none]
                    # For now, I have to punt and return the dict
                    self.__participants.append(participant)

        return self.__participants


class Team(Base):
    """Class representing a Team in Opsgenie
    https://docs.opsgenie.com/docs/team-api
    """
    logger = logging.getLogger(__name__)
    resource_name = 'teams'

    def __init__(self, *args, **kwargs):
        self.__members: Optional[List['User']] = None

        self.lookup_attributes = [
            'name',
            'description',
            'links',
            'members',
        ]
        self.skip_attributes = ['members']

        super().__init__(*args, resource_name=self.resource_name, **kwargs)

    @property
    def members(self) -> List['User']:
        """Retrive a list of Opsgenie Users associated
        with the team

        Returns:
            List[User]: List containing Opsgenie
            users associated with a team
        """
        if self.__members is None:
            self.query_attributes(self.resource_url())
            self.__members = [
                User(self.session, self.opsgenie_url, **member['user'])
                for member in self._context.get('members', [])
            ]

        return self.__members


class User(Base):
    """Class representing a User in in Opsgenie
    https://docs.opsgenie.com/docs/user-api
    """
    logger = logging.getLogger(__name__)
    resource_name = 'users'

    def __init__(self, *args, **kwargs):
        self.__role = None
        self.__contacts: Optional[dict] = None

        self.lookup_attributes = [
            'blocked',
            'createdAt',
            'details',
            'fullName',
            'locale',
            'timeZone',
            'userAddress',
            'username',
            'verified'
        ]
        self.skip_attributes = ['role']

        super().__init__(*args, resource_name=self.resource_name, **kwargs)

    @property
    def role(self) -> Dict[str, str]:
        """Role of usr.
        It may be one of Admin, User or the name of a custom role created.

        Returns:
            Dict[str, str]: id and name of the role as keys
        """
        if self.__role is None:
            self.query_attributes(self.resource_url(), params={'expand': 'contact'})

            self.__role = self._context['role']

        return self.__role

    @property
    def date_created(self) -> datetime.datetime:
        """Generate datetime object form createdAt
        field

        Returns:
            datetime.datetime: represents when the user
                was created in Opsgenie
        """
        date = datetime.datetime.strptime(
            self.createdAt.replace(
                'Z',
                '+0000'),
            '%Y-%m-%dT%H:%M:%S.%f%z')

        return date

    @property
    def contacts(self) -> dict:
        """Retrive a user's means of contact
        https://docs.opsgenie.com/docs/contact-api#list-contacts
        """
        if self.__contacts is None:
            url = "/".join(
                [self.resource_url(), "contacts"])

            self.logger.debug("url=%s", url)

            response = self.session.get(url)

            self.__contacts = response.json()['data']

        return self.__contacts
