import random
import string
import unittest
from unittest.mock import Mock

import popsgenie.api_classes
import popsgenie.page


class PopsgeniePage(unittest.TestCase):
    def random_id(self):
        random_string = ''.join(
            random.choices(
                string.ascii_lowercase + string.digits, k=32))

        random_id = (
            f"{random_string[0:8]}-{random_string[8:12]}-"
            f"{random_string[12:16]}-{random_string[16:20]}-"
            f"{random_string[20:None]}")

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

        pages = popsgenie.page.PopsgeniePage(
            session,
            "https://api.opsgenie.com/v2/users",
            "https://api.opsgenie.com/v2/users?limit=2&offset=2",
            popsgenie.api_classes.PopsgenieUser,
        )

        users = [user for users in pages for user in users]

        # Assert
        self.assertEqual(session.get.call_count, 2)
        self.assertEqual(len(users), 4)

    def test_query_schedule_by_id(self):
        """Query for schedules by id returns one PopsgenieSchedule
        elment in list"""
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
                "ownerTeam": {
                    "id": self.random_id(),
                    "name": "Owner Team Name",
                },
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

        pages = popsgenie.page.PopsgeniePage(
            session,
            'https://api.opsgenie.com/v2',
            f"https://api.opsgenie.com/v2/schedules/{schedule_id}?offset=0&limit=20&identifierType=id",
            popsgenie.api_classes.PopsgenieSchedule,
        )

        # Act
        schedules = next(pages)

        # Assert
        self.assertEqual(len(schedules), 1)
        self.assertEqual(schedules[0].id, schedule_id)

    def test_query_schedules_does_not_make_more_than_one_request(self):
        """Query for schedules, by identifier, does not make
        more than one request to Opsgenie
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
                "ownerTeam": {
                    "id": self.random_id(),
                    "name": "Owner Team Name",
                },
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

        pages = popsgenie.page.PopsgeniePage(
            session,
            'https://api.opsgenie.com/v2',
            f"https://api.opsgenie.com/v2/schedules/{schedule_id}?offset=0&limit=20&identifierType=id",
            popsgenie.api_classes.PopsgenieSchedule,
        )

        # Act
        for page in pages:
            continue

        # Assert
        self.assertEqual(session.get.call_count, 1)

