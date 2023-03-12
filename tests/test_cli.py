import unittest
import unittest.mock
import pathlib

from click.testing import CliRunner
from cli import run


class TestRun(unittest.TestCase):
    """Test case for cli:run"""

    runner = None
    test_api_response = {
        "response": {
            "count": 1,
            "items": [
                {
                    "id": 1,
                    "track_code": "test_track_code",
                    "first_name": "test_fname",
                    "last_name": "test_lname",
                    "can_access_closed": True,
                    "is_closed": False,
                }
            ],
        }
    }

    def setUp(self):
        self.runner = CliRunner()

    def test_data_fetcher(self):
        """
        Mock of function generator that yields data from
        Vk API
        """
        yield {"status_code": 200, "error": "OK", "data": self.test_api_response}

    def test_user_id_was_not_specified(self):
        """
        Check if Error appears if user_id was not specified
        """

        result = self.runner.invoke(run, input="test_token")
        self.assertEqual(result.exit_code, 2)

    def test_successful_run(self):
        """
        Check if run with only given user_id is
        successful
        """

        with self.runner.isolated_filesystem():
            with unittest.mock.patch(
                "vk_friends.app.VKFriends.fetch_friend_list",
                side_effect=self.test_data_fetcher,
            ):
                result = self.runner.invoke(run, ["-u 1"], input="test_token")
                self.assertEqual(result.exit_code, 0)
                with open("./report.csv", "r", encoding="utf-8") as file_stream:
                    data = file_stream.read()
                    self.assertEqual(
                        data,
                        "\ufeff# auth_token: test_token\n"
                        "# user_id: 1\n"
                        "first_name,last_name,country,city,bdate,sex\n"
                        "test_fname,test_lname,,,,\n",
                    )

    def test_report_format_specified(self):
        """
        Check whether data is written in correct format
        and in correct file when report_format is specified
        explicitly
        """

        with self.runner.isolated_filesystem():
            with unittest.mock.patch(
                "vk_friends.app.VKFriends.fetch_friend_list",
                side_effect=self.test_data_fetcher,
            ):
                self.runner.invoke(run, ["-u", "1", "-f", "json"], input="test_token")
                with open("./report.json", "r", encoding="utf-8") as file_stream:
                    data = file_stream.read()
                    self.assertEqual(
                        data,
                        "{\n"
                        '  "auth_token": "test_token",\n'
                        '  "user_id": "1",\n'
                        '  "friends": [\n'
                        "    {\n"
                        '      "first_name": "test_fname",\n'
                        '      "last_name": "test_lname",\n'
                        '      "country": null,\n'
                        '      "city": null,\n'
                        '      "bdate": null,\n'
                        '      "sex": null\n'
                        "    }\n"
                        "  ]\n"
                        "}",
                    )

    def test_report_path_specified(self):
        """
        Check whether file is being created when
        report_path is specified explicitly
        """

        with self.runner.isolated_filesystem():
            with unittest.mock.patch(
                "vk_friends.app.VKFriends.fetch_friend_list",
                side_effect=self.test_data_fetcher,
            ):
                path = "./fs_not_report.json"
                self.runner.invoke(
                    run, ["-u", "1", "-f", "json", "-p", path], input="test_token"
                )
                craeted_file = pathlib.Path(path)
                self.assertTrue(craeted_file.is_file())
