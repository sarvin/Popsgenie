import unittest
from unittest.mock import Mock

import popsgenie.api_classes
import popsgenie.page


class PopsgeniePage(unittest.TestCase):
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
                "next": "https://api.opsgenie.com/v2/users?limit=2&offset=2&order=ASC&sort=username",
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
            'https://api.opsgenie.com/v2/users',
            'https://api.opsgenie.com/v2/users?limit=2&offset=2',
            popsgenie.api_classes.PopsgenieUser)

        users = [user for users in pages for user in users]

        # Assert

        self.assertEqual(len(users), 4)
