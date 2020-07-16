import random
import string
import unittest
from unittest.mock import Mock

import popsgenie.resource
import popsgenie.tool


class PopsgeniePage(unittest.TestCase):
    def random_id(self):
        random_string = "".join(
            random.choices(string.ascii_lowercase + string.digits, k=32)
        )

        random_id = (
            f"{random_string[0:8]}-{random_string[8:12]}-"
            f"{random_string[12:16]}-{random_string[16:20]}-"
            f"{random_string[20:None]}"
        )

        return random_id

    def test_initialization(self):
        """iterating over page makes requests
        in the proper order
        """
        # Arrange
        session = Mock()
        response_1 = Mock()
        response_1.status_code = 200
        response_1.json.return_value = {
            "data": [
                {
                    "blocked": False,
                    "createdAt": "2019-04-14T16:22:44.947Z",
                    "fullName": "Bob McThornton",
                    "id": "cza5093-fbc7-4533-96e5-510f67b5025f",
                    "locale": "en_US",
                    "role": {"id": "User", "name": "User"},
                    "timeZone": "America/Chicago",
                    "userAddress": {
                        "city": "",
                        "country": "",
                        "line": "",
                        "state": "",
                        "zipCode": "",
                    },
                    "username": "bmcthornton@notreal.com",
                    "verified": True,
                },
                {
                    "blocked": False,
                    "createdAt": "2018-03-20T11:24:32.022Z",
                    "fullName": "Sarah Johnson",
                    "id": "87y9dg27-fbc7-4304-895c-1666d89851f0",
                    "locale": "en_US",
                    "role": {"id": "Admin", "name": "Admin"},
                    "timeZone": "America/Chicago",
                    "userAddress": {
                        "city": "",
                        "country": "",
                        "line": "",
                        "state": "",
                        "zipCode": "",
                    },
                    "username": "sjohnson@notreal.com",
                    "verified": True,
                },
            ],
            "paging": {
                "first": "https://api.opsgenie.com/v2/users?limit=2&offset=0&order=ASC&sort=username",
                "last": "https://api.opsgenie.com/v2/users?limit=2&offset=4&order=ASC&sort=username",
                "next": "https://api.opsgenie.com/v2/users?limit=2&offset=2&order=ASC&sort=username",
            },
            "requestId": "87y9dg27-0b6a-435f-ac49-6b25c9bb791f",
            "took": 0.023,
            "totalCount": 2,
        }
        response_2 = Mock()
        response_2.status_code = 200
        response_2.json.return_value = {
            "data": [
                {
                    "blocked": False,
                    "createdAt": "2019-04-14T16:22:44.947Z",
                    "fullName": "Bob McThornton",
                    "id": "cza5093-fbc7-4533-96e5-510f67b5025f",
                    "locale": "en_US",
                    "role": {"id": "User", "name": "User"},
                    "timeZone": "America/Chicago",
                    "userAddress": {
                        "city": "",
                        "country": "",
                        "line": "",
                        "state": "",
                        "zipCode": "",
                    },
                    "username": "bmcthornton@notreal.com",
                    "verified": True,
                },
                {
                    "blocked": False,
                    "createdAt": "2018-03-20T11:24:32.022Z",
                    "fullName": "Sarah Johnson",
                    "id": "87y9dg27-fbc7-4304-895c-1666d89851f0",
                    "locale": "en_US",
                    "role": {"id": "Admin", "name": "Admin"},
                    "timeZone": "America/Chicago",
                    "userAddress": {
                        "city": "",
                        "country": "",
                        "line": "",
                        "state": "",
                        "zipCode": "",
                    },
                    "username": "sjohnson@notreal.com",
                    "verified": True,
                },
            ],
            "paging": {
                "first": "https://api.opsgenie.com/v2/users?limit=2&offset=0&order=ASC&sort=username",
                "last": "https://api.opsgenie.com/v2/users?limit=2&offset=4&order=ASC&sort=username",
            },
            "requestId": "87y9dg27-0b6a-435f-ac49-6b25c9bb791f",
            "took": 0.023,
            "totalCount": 2,
        }
        session.get.side_effect = [
            response_1,
            response_2,
        ]

        pages = popsgenie.tool.Pages(
            session,
            "https://api.opsgenie.com/v2",
            "https://api.opsgenie.com/v2/users?limit=2&offset=2",
            popsgenie.resource.User,
        )

        users = [user for users in pages for user in users]

        # Assert
        self.assertEqual(session.get.call_count, 2)
        self.assertEqual(len(users), 4)

    def test_query_schedule_by_id(self):
        """Query for schedules by id returns one PopsgenieSchedule
        element in list
        """
        # Arrange
        schedule_id = self.random_id()
        session = Mock()
        response = session.get.return_value
        response.json.return_value = {
            "data": {
                "id": schedule_id,
                "name": "Team Name - On Call",
                "description": "",
                "timezone": "America/Chicago",
                "enabled": False,
                "ownerTeam": {"id": self.random_id(), "name": "Owner Team Name",},
                "rotations": [
                    {
                        "id": self.random_id(),
                        "name": "Team Rotation",
                        "startDate": "2020-06-05T13:00:00Z",
                        "type": "daily",
                        "length": 1,
                        "participants": [
                            {
                                "type": "user",
                                "id": self.random_id(),
                                "username": "mcgluck@notreal.net",
                            }
                        ],
                    }
                ],
            },
            "took": 0.037,
            "requestId": self.random_id(),
        }

        pages = popsgenie.tool.Pages(
            session,
            "https://api.opsgenie.com/v2",
            f"https://api.opsgenie.com/v2/schedules/{schedule_id}?offset=0&limit=20&identifierType=id",
            popsgenie.resource.Schedule,
        )

        schedules = []
        # Act
        for page in pages:
            schedules.extend(page)

        # Assert
        self.assertEqual(len(schedules), 1)
        self.assertEqual(schedules[0].id, schedule_id)
        self.assertIsInstance(schedules[0], popsgenie.resource.Schedule)
        self.assertEqual(session.get.call_count, 1)

    def test_query_teams_by_id(self):
        """Query for teams by id returns one PopsgenieTeam
        element in list
        """
        # Arrange
        team_id = self.random_id()
        session = Mock()
        response = session.get.return_value
        response.json.return_value = {
            "data": {
                "description": "random text field entry",
                "id": team_id,
                "links": {
                    "api": f"https://api.opsgenie.com/v2/teams/{team_id}",
                    "web": f"https://company.xyz.opsgenie.com/teams/dashboard/{team_id}/main",
                },
                "members": [
                    {
                        "role": "admin",
                        "user": {
                            "id": self.random_id(),
                            "username": "bubbamore@notreal.com",
                        },
                    },
                    {
                        "role": "admin",
                        "user": {
                            "id": self.random_id(),
                            "username": "jpants@notreal.com",
                        },
                    },
                ],
                "name": "Team - with a name",
            },
            "requestId": self.random_id(),
            "took": 0.158,
        }

        pages = popsgenie.tool.Pages(
            session,
            "https://api.opsgenie.com/v2",
            f"https://api.opsgenie.com/v2/teams/{team_id}?offset=0&limit=20&identifierType=id",
            popsgenie.resource.Team,
        )

        teams = []
        # Act
        for page in pages:
            teams.extend(page)

        # Assert
        self.assertEqual(len(teams), 1)
        self.assertEqual(teams[0].id, team_id)
        self.assertIsInstance(teams[0], popsgenie.resource.Team)
        self.assertEqual(session.get.call_count, 1)

    def test_query_users_by_id(self):
        """Query for users by id returns one PopsgenieUser
        element in list
        """
        # Arrange
        user_id = self.random_id()
        session = Mock()
        response = session.get.return_value
        response.json.return_value = {
            "data": {
                "blocked": False,
                "createdAt": "2020-01-07T19:34:00.281Z",
                "fullName": "Buddy McPantshat",
                "id": user_id,
                "locale": "en_US",
                "role": {"id": "Admin", "name": "Admin"},
                "timeZone": "America/Chicago",
                "userAddress": {
                    "city": "",
                    "country": "",
                    "line": "",
                    "state": "",
                    "zipCode": "",
                },
                "username": "bpantshat@notreal.com",
                "verified": True,
            },
            "expandable": ["contact"],
            "requestId": self.random_id(),
            "took": 0.011,
        }

        pages = popsgenie.tool.Pages(
            session,
            "https://api.opsgenie.com/v2",
            f"https://api.opsgenie.com/v2/users/{user_id}?offset=0&limit=20&identifierType=id",
            popsgenie.resource.User,
        )

        users = []
        # Act
        for page in pages:
            users.extend(page)

        # Assert
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].id, user_id)
        self.assertIsInstance(users[0], popsgenie.resource.User)
        self.assertEqual(session.get.call_count, 1)
