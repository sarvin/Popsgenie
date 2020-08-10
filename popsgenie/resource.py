"""Represent data in Opsgenie with Popsgenie Classes"""
from abc import ABC
import datetime
import logging
from typing import Dict, List, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    import tool


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
            connection: 'tool.Connection',
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
        self.connection = connection
        self.__resource_name: Optional[str] = resource_name


        # keep an updated list of object's attributes
        # this can get updated after a web request
        self._context = kwargs

        for key, value in kwargs.items():
            try:
                setattr(self, key, value)
            except AttributeError as error:
                if key in dir(self):
                    pass
                else:
                    raise AttributeError(f"{error}: {key}")

    def __repr__(self):
        return "%s(%r)" % (self.__class__, self.id)

    def __getattr__(self, key: str):
        """Some attributes are pre-set when the object is instantiated.
        Others aren't available on initialization and require a query.
        This method allows us to query only when the attribute is required.
        In some cases this can save us a web request.
        """
        if key in self.lookup_attributes:
            self.query_attributes(self.resource_url())

        return self.__getattribute__(key)

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

        response = self.connection.session.get(context_url, **kwargs)
        json = response.json()

        # Update our context with the latest information
        self._context = json['data']

        for key, value in json['data'].items():
            try:
                setattr(self, key, value)
            except AttributeError as error:
                if key in dir(self):
                    pass
                else:
                    raise AttributeError(f"{error}: {key}")

    def resource_url(self) -> str:
        """String declaring the resource's API endpoing

        Returns:
            str: value suitable for querying resource data
        """
        url = "/".join(
            [self.connection.url_base, self.__resource_name, self.id]) # type: ignore

        return url


class Alert(Base):
    """Class representing a Alert in Opsgenie
    https://docs.opsgenie.com/docs/alert-api
    """
    logger = logging.getLogger(__name__)
    resource_name = 'alerts'

    def __init__(self, *args, **kwargs):
        self.__responders: Optional[List[Union['Schedule', 'Team', 'User', dict]]] = None

        self.lookup_attributes = ['responders']

        super().__init__(*args, resource_name=self.resource_name, **kwargs)

    @property
    def responders(self) -> List[Union['Schedule', 'Team', 'User', dict]]:
        """Teams, users, escalations and schedules
        that the alert will be routed to send notifications.

        Returns:
            List[Union['Schedule', 'Team', 'User', dict]]: A list of Popsgenie resources
                or a dict if responder is of type escalation
        """
        if self.__responders is None:
            self.__responders = []

            for responder in self._context.get('responders', []):
                if responder['type'] == 'user':
                    responder.pop("type")

                    self.__responders.append(
                        User(self.connection, **responder))
                elif responder['type'] == 'team':
                    responder.pop("type")

                    self.__responders.append(
                        Team(self.connection, **responder))
                elif responder['type'] == 'schedule':
                    responder.pop("type")

                    self.__responders.append(
                        Schedule(self.connection, **responder))
                else:
                    # Haven't witnessed responder['type'] == [escalation]
                    # For now, I have to punt and return the dict
                    self.__responders.append(responder)

        return self.__responders


class Escalation(Base):
    """Class representing a Escalation in Opsgenie
    https://docs.opsgenie.com/docs/escalation-api
    """
    logger = logging.getLogger(__name__)
    resource_name = 'escalations'

    def __init__(self, *args, **kwargs):
        self.__rules: List[dict] = None
        self.__owner_team = None

        self.lookup_attributes = [
            'name',
            'description',
        ]

        super().__init__(*args, resource_name=self.resource_name, **kwargs)

    @property
    def rules(self) -> List[dict]:
        """Dictionary of data describing an escalation's rules.
        rule's recipient is replaced with a corresponding Popsgenie resource

        Returns:
            List[dict]: dictionary describing Opsgenie rules
        """
        if self.__rules is None:
            self.__rules = []

            for rule in self._context.get('rules', {}):
                if rule['recipient']['type'] == 'schedule':
                    rule['recipient'].pop("type")

                    rule['recipient'] = Schedule(self.connection, **rule['recipient'])

                    self.__rules.append(rule)
                elif rule['recipient']['type'] == 'user':
                    rule['recipient'].pop("type")

                    rule['recipient'] = User(self.connection, **rule['recipient'])

                    self.__rules.append(rule)
                elif rule['recipient']['type'] == 'team':
                    rule['recipient'].pop("type")

                    rule['recipient'] = Team(self.connection, **rule['recipient'])

                    self.__rules.append(rule)
                else:
                    # For now, I have to punt and return the dict
                    self.__rules.append(rule)

        return self.__rules

    @property
    def owner_team(self) -> 'Team':
        """Property representing a escalation's owning team

        Returns:
            [Team]: A team owning the escalation policy
        """
        if self.__owner_team is None and self._context.get('ownerTeam'):
            self.__owner_team = Team(self.connection, **self._context['ownerTeam'])

        return self.__owner_team


class Incident(Base):
    """Class representing a incident in Opsgenie
    https://docs.opsgenie.com/docs/incident-api#get-incident

    This class makes no external queries
    """
    logger = logging.getLogger(__name__)

    def __init__(self, *args, **kwargs):
        self.__responders: Optional[List[Union['User', 'Team']]] = None

        super().__init__(*args, **kwargs)

    @property
    def responders(self) -> List[Union['User', 'Team']]:
        """Users, teams that the incident will be routed to send notifications.

        Returns:
            List[Union['User', 'Team']]: A list of Popsgenie resources
        """
        if self.__responders is None:
            self.__responders = []

            for responder in self._context.get('responders', []):
                if responder['type'] == 'user':
                    responder.pop("type")

                    self.__responders.append(
                        User(self.connection, **responder))
                elif responder['type'] == 'team':
                    responder.pop("type")

                    self.__responders.append(
                        Team(self.connection, **responder))

        return self.__responders


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
                        User(self.connection, **participant))
                elif participant['type'] == 'team':
                    self.__participants.append(
                        Team(self.connection, **participant))
                else:
                    # Haven't witnessed participant['type'] == [escalation | none]
                    # For now, I have to punt and return the dict
                    self.__participants.append(participant)

        return self.__participants


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
                Rotation(self.connection, **rotation_data)
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
                [self.connection.url_base, "teams", self.ownerTeam['id']]
            )

            self.logger.debug("url=%s", url)

            response = self.connection.session.get(url)
            self.__team = Team(self.connection, **response.json()['data'])

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

            response = self.connection.session.get(url)

            self.__on_calls = [
                User(self.connection, **user_data)
                for user_data in response.json()['data']['onCallParticipants']
            ]

        return self.__on_calls


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
                User(self.connection, **member['user'])
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

            response = self.connection.session.get(url)

            self.__contacts = response.json()['data']

        return self.__contacts
