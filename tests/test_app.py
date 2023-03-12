"""Unit-tests used in testing
all units of module vk_friends.app
"""
import unittest
import unittest.mock

from requests.exceptions import ConnectionError as RequestsConnectionError
from requests.exceptions import ConnectTimeout, HTTPError, ReadTimeout, Timeout
from vk_friends import VKFriends
from vk_friends.exceptions import ApiParameterError, ServerResponseError


class TestVKFriends(unittest.TestCase):
    """Test case for VKFriends class"""

    def setUp(self):
        self.response_items = [
            {
                "id": 1,
                "track_code": "test_track_code1",
                "first_name": "test_user_name1",
                "can_access_closed": True,
                "is_closed": False,
            },
            {
                "id": 2,
                "track_code": "test_track_code2",
                "first_name": "test_user_name2",
                "can_access_closed": True,
                "is_closed": False,
            },
            {
                "id": 3,
                "track_code": "test_track_code3",
                "first_name": "test_user_name3",
                "can_access_closed": True,
                "is_closed": False,
            },
            {
                "id": 4,
                "track_code": "test_track_code4",
                "first_name": "test_user_name4",
                "can_access_closed": True,
                "is_closed": False,
            },
            {
                "id": 5,
                "track_code": "test_track_code5",
                "first_name": "test_user_name5",
                "can_access_closed": True,
                "is_closed": False,
            },
        ]
        return

    def test_count_gt_limit(self):
        """
        If count is greater than limit, count should
        be assigned limit value
        """
        limit = 40
        count = 50

        app = VKFriends(
            auth_token="test_token", user_id="test_user_id", limit=limit, count=count
        )

        self.assertEqual(app.count, limit)

    def test_fetch_friend_list_raises_ServerResponseError(self):
        """
        If requests.get raises one of ConnectTimeout, HTTPError,
        ReadTimeout, Timeout, ConnectionError errors app.fetch_friend_list
        should raise ServerResponseError
        """
        app = VKFriends(auth_token="test_token", user_id="test_user_id")

        def assert_friend_list_raises_ServerResponseError():
            """Call app's method fetch_friend_list and assert it
            raises ServerResponseError
            """
            app.fetch_friend_list()
            self.assertRaises(ServerResponseError)

        with unittest.mock.patch("requests.get") as requests_get:
            for error in (
                RequestsConnectionError,
                HTTPError,
                ReadTimeout,
                Timeout,
                ConnectTimeout,
            ):
                requests_get.return_value.raiseError.side_effect = error()
                assert_friend_list_raises_ServerResponseError()

    def test_fetch_friend_list_raises_ApiParameterError(self):
        """
        If requests.get does not raise any error, but API response
        raises error, then app.fetch_friend_list should raise ApiParameterError
        """
        app = VKFriends(auth_token="test_token", user_id="test_user_id")

        class MockResponse:
            """Class similar to instance that requests.get
            would return"""

            def __init__(self) -> None:
                self.status_code = 200
                self.json = lambda self: {
                    "error": {
                        "error_code": 5,
                        "error_msg": "User authorization failed: invalid access_token (4).",
                        "request_params": [
                            {"key": "offset", "value": "0"},
                            {"key": "count", "value": "100"},
                            {"key": "order", "value": "name"},
                            {"key": "user_id", "value": "test_user_id"},
                            {
                                "key": "fields",
                                "value": "first_name,last_name,country,city,bdate,sex",
                            },
                            {"key": "v", "value": "5.131"},
                            {"key": "method", "value": "friends.get"},
                            {"key": "oauth", "value": "1"},
                        ],
                    }
                }

        with unittest.mock.patch("requests.get") as requests_get:
            requests_get.return_value = MockResponse()
            app.fetch_friend_list()
            self.assertRaises(ApiParameterError)
