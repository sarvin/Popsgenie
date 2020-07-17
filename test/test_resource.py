import unittest
from unittest.mock import Mock

import popsgenie.tool
import popsgenie.resource


class PopsgenieSchedule(unittest.TestCase):
    def test_initialization_with_list_data(self):
        """Data, from list schedules,
        can properly instantiate a Schedule object
        """
        # Arrange

        session = Mock()
        connection = popsgenie.tool.Connection(session, 'xyz')

        schedule_data = {
            "id": "0d4w397f-10j7-k8ht-zx92-06796bc00cbd",
            "name": "Some On Call",
            "description": "",
            "timezone": "America/Chicago",
            "enabled": False,
            "ownerTeam": {
                "id": "m7gs6hv0-x1k0-6lpo-54hq-l0kk1j6f901b6",
                "name": "A Team Name",
            },
            "rotations": [],
        }

        # Act
        schedule = popsgenie.resource.Schedule(
            connection, **schedule_data
        )

        # Assert
        self.assertIsInstance(schedule, popsgenie.resource.Schedule)


class PopsgenieRotation(unittest.TestCase):
    def test_initialization_with_schedules_rotation_data(self):
        """Data, from schedule's rotation query,
        can properly instantiate a Rotation object
        """
        # Arrange
        session = Mock()
        connection = popsgenie.tool.Connection(session, 'xyz')

        data = {
            "id": "0d4w397f-10j7-k8ht-zx92-06796bc00cbd",
            "name": "Some on Call Rotation",
            "startDate": "2020-06-05T13:00:00Z",
            "type": "daily",
            "length": 1,
            "participants": [
                {
                    "type": "user",
                    "id": "m7gs6hv0-x1k0-6lpo-54hq-l0kk1j6f901b6",
                    "username": "kurthymurthy@notrealemail.com",
                }
            ],
        }

        # Act
        rotation = popsgenie.resource.Rotation(connection, **data)

        # Assert
        self.assertIsInstance(rotation, popsgenie.resource.Rotation)


class PopsgenieTeam(unittest.TestCase):
    def test_initialization_with_list_data(self):
        """Data, from list team query,
        can properly instantiate a Team object
        """
        # Arrange
        session = Mock()
        connection = popsgenie.tool.Connection(session, 'xyz')

        data = {
            "id": "0d4w397f-10j7-k8ht-zx92-06796bc00cbd",
            "name": "Some Team Name",
            "description": "",
            "links": {
                "web": "https://company.opsgenie.com/teams/dashboard/0d4w397f-10j7-k8ht-zx92-06796bc00cbd/main",
                "api": "https://api.opsgenie.com/v2/teams/0d4w397f-10j7-k8ht-zx92-06796bc00cbd",
            },
        }

        # Act
        team = popsgenie.resource.Team(connection, **data)

        # Assert
        self.assertIsInstance(team, popsgenie.resource.Team)


class PopsgenieUser(unittest.TestCase):
    def test_initialization_with_list_data(self):
        """Data, from list user query,
        can properly instantiate a User object
        """
        # Arrange
        session = Mock()
        connection = popsgenie.tool.Connection(session, 'xyz')

        data = {
            "blocked": False,
            "verified": True,
            "id": "0d4w397f-10j7-k8ht-zx92-06796bc00cbd",
            "username": "bfultherfrump@notrealthings.com",
            "fullName": "Bubby Fultherfrump",
            "role": {"id": "Admin", "name": "Admin"},
            "timeZone": "America/Chicago",
            "locale": "en_US",
            "userAddress": {
                "country": "",
                "state": "",
                "city": "",
                "line": "",
                "zipCode": "",
            },
            "createdAt": "2020-01-07T19:34:00.281Z",
        }

        # Act
        team = popsgenie.resource.Team(connection, **data)

        # Assert
        self.assertIsInstance(team, popsgenie.resource.Team)
