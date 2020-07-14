"""Represent data in Opsgenie with Popsgenie Classes"""
import datetime
import logging
from typing import Dict, List, Optional

import requests


class PopsgenieBase():
    """Base class used to represent datatypes returned
    by the Opsgenie API https://docs.opsgenie.com/docs/api-overview
    At a minimum each inheriting object needs to implement
    self.lookup_attributes and skip_attributes as empty lists.
    The child object's attributes reflect the fields returned by
    Opsgenie *except* when the attribute is included in skip_attributes.
    If on initialization the child object did not recieve data, for an attribute,
    it will be queried if the attribute's name is included in self.lookup_attributes.
    """
    def __init__(self, session: requests.sessions.Session, opsgenie_url: str, **kwargs):
        self.__session = session
        self.opsgenie_url = opsgenie_url


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
            self.query_attributes(self._context_url)

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


class PopsgenieSchedule(PopsgenieBase):
    """Class representing a Schedule in Opsgenie
    https://docs.opsgenie.com/docs/schedule-api
    """
    logger = logging.getLogger(__name__)

    def __init__(self, *args, **kwargs):
        self.__team: Optional[PopsgenieTeam] = None
        self.__on_calls: Optional[List['PopsgenieUser']] = None
        self.__rotations: Optional[List[dict]] = None
        self.lookup_attributes = [
            'name',
            'description',
            'timezone',
            'enabled',
            'ownerTeam',
        ]
        self.skip_attributes = ['rotations']

        super().__init__(*args, **kwargs)

        self._context_url = "/".join(
            [self.opsgenie_url, "schedules", self.id])

    @property
    def rotations(self) -> List[dict]:
        """Returns the raw data for a Opsgenie rotation
        associated with a schedule

        Returns:
            List[dict]: raw response from Opsgenie
        """
        if self.__rotations is None:
            self.query_attributes(self._context_url)
            self.__rotations = [
                PopsgenieRotation(self.session, self.opsgenie_url, **rotation_data)
                for rotation_data in self._context['rotations']
            ]

        return self.__rotations

    @property
    def team(self) -> 'PopsgenieTeam':
        """Query Opsgenie for the team associated with a
        schedule and convert raw data to PopsgenieTeam

        Returns:
            PopsgenieTeam: an object representing a Team
                in Opsgenie
        """
        if self.__team is None:
            url = "/".join(
                [self.opsgenie_url, "teams", self.ownerTeam['id']]
            )

            self.logger.debug("url=%s", url)

            response = self.session.get(url)
            self.__team = PopsgenieTeam(self.session, self.opsgenie_url, **response.json()['data'])

        return self.__team

    @property
    def on_calls(self) -> List['PopsgenieUser']:
        """Retrieve users on call for a Schedule

        Returns:
            List[PopsgenieUser]: Users on call in a schedule
        """
        if self.__on_calls is None:
            url = "/".join(
                [self._context_url, "on-calls"])

            self.logger.debug("url=%s", url)

            response = self.session.get(url)

            self.__on_calls = [
                PopsgenieUser(self.session, self.opsgenie_url, **user_data)
                for user_data in response.json()['data']['onCallParticipants']
            ]

        return self.__on_calls


class PopsgenieRotation(PopsgenieBase):
    """Class representing a schedule's rotation in Opsgenie
    https://docs.opsgenie.com/docs/schedule-api#section-schedule-rotation-fields
    """
    logger = logging.getLogger(__name__)

    def __init__(self, *args, **kwargs):
        self.__participants: Optional[List[PopsgenieUser]] = None
        self.lookup_attributes = []
        self.skip_attributes = ['participants']

        super().__init__(*args, **kwargs)

    @property
    def participants(self) -> List['PopsgenieUser']:
        """Retrive a list of Opsgenie Users associated
        with the rotation

        Returns:
            List[PopsgenieUser]: List containing Opsgenie
            users
        """
        if self.__participants is None:
            self.__participants = []

            for participant in self._context.get('participants', []):
                if participant['type'] == 'user':
                    self.__participants.append(
                        PopsgenieUser(self.session, self.opsgenie_url, **participant))
                elif participant['type'] == 'team':
                    self.__participants.append(
                        PopsgenieTeam(self.session, self.opsgenie_url, **participant))
                else:
                    # Haven't witnessed participant['type'] == [escalation | none]
                    # so I'm punting
                    self.__participants.append(participant)

        return self.__participants


class PopsgenieTeam(PopsgenieBase):
    """Class representing a Team in Opsgenie
    https://docs.opsgenie.com/docs/team-api
    """
    logger = logging.getLogger(__name__)

    def __init__(self, *args, **kwargs):
        self.__members: Optional[List['PopsgenieUser']] = None
        self.lookup_attributes = [
            'name',
            'description',
            'links',
            'members',
        ]
        self.skip_attributes = ['members']

        super().__init__(*args, **kwargs)

        self._context_url = "/".join(
            [self.opsgenie_url, "teams", self.id])

    @property
    def members(self) -> List['PopsgenieUser']:
        """Retrive a list of Opsgenie Users associated
        with the team

        Returns:
            List[PopsgenieUser]: List containing Opsgenie
            users associated with a team
        """
        if self.__members is None:
            self.query_attributes(self._context_url)
            self.__members = [
                PopsgenieUser(self.session, self.opsgenie_url, **member['user'])
                for member in self._context.get('members', [])
            ]

        return self.__members


class PopsgenieUser(PopsgenieBase):
    """Class representing a User in in Opsgenie
    https://docs.opsgenie.com/docs/user-api
    """
    logger = logging.getLogger(__name__)

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

        super().__init__(*args, **kwargs)

        self._context_url = "/".join(
            [self.opsgenie_url, "users", self.id])

    @property
    def role(self) -> Dict[str, str]:
        """Role of usr.
        It may be one of Admin, User or the name of a custom role created.

        Returns:
            Dict[str, str]: id and name of the role as keys
        """
        if self.__role is None:
            self.query_attributes(self._context_url, params={'expand': 'contact'})

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
                [self._context_url, "contacts"])

            self.logger.debug("url=%s", url)

            response = self.session.get(url)

            self.__contacts = response.json()['data']

        return self.__contacts
