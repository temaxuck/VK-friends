import json
import os
import typing as t
import requests
from requests.exceptions import (
    ConnectTimeout,
    HTTPError,
    ReadTimeout,
    Timeout,
    ConnectionError as RequestsConnectionError,
)

from vk_friends.formats_supported import FORMATS_SUPPORTED
from vk_friends.report_generator import ReportGeneratorFactory
from vk_friends.exceptions import ServerResponseError, ApiParameterError


class VKFriends:
    """The VKFriends object is used to generate reports of vk users
    that a specific user has as friends. Accessing information through
    public vk api.

    Attributes:

    """

    api_url = "https://api.vk.com"
    api_version = "5.131"
    request_timeout = 30
    fields = ["first_name", "last_name", "country", "city", "bdate", "sex"]

    def __init__(
        self,
        auth_token: str,
        user_id: str,
        report_format: FORMATS_SUPPORTED = FORMATS_SUPPORTED.CSV,
        report_path: t.Union[str, os.PathLike] = "./report",
        api_version: str = None,
        api_url: str = None,
        request_timeout: float = None,
    ) -> None:
        self.auth_token = auth_token
        self.user_id = user_id
        self.report_format = report_format
        self.report_path = report_path

        if api_version:
            self.api_version = api_version

        if api_url:
            self.api_url = api_url

        if request_timeout:
            self.request_timeout = request_timeout

    def generate_report(self) -> None:
        """Generates report with provided in app settings:
        Report format: self.report_format
        Report path: self.report_path

        Raises:
            ServerResponseError: Could not get successful HTTP response from server (self.api_url)
            ApiParameterError: Could not get successful HTTP response from vk API (self.api_url)
                because of wrong passed paramaters (self.auth_token, self.user_id)
        """
        report_generator = ReportGeneratorFactory.get_report_generator(
            self.report_format, self.report_path
        )

        fetch_response = self.fetch_friend_list()
        if fetch_response["status_code"] != 200:
            raise ServerResponseError(
                f"Could not get proper response from API. Status code: {fetch_response['status_code']}; Error: {fetch_response['error']}"
            )

        if "error" in fetch_response["data"]:
            raise ApiParameterError(
                f"Could not properly request API. Status code: {fetch_response['data']['error']['error_code']}; Error: {fetch_response['data']['error']['error_msg']}"
            )

        if "response" in fetch_response["data"]:
            report_gen = report_generator.generate_report()
            report_gen.send(None)
            report_gen.send(fetch_response["data"]["response"]["items"])
            try:
                report_gen.send({})
            except GeneratorExit:
                print("Report has been generated!")
                return

    def fetch_friend_list(self) -> tuple:
        """Get a list of friends of a user who's id is
        specified in self.user_id

        Returns:
            tuple: (
                int: response status code,
                dict: response itself(json format)
            )
        """

        try:
            response = requests.get(
                url=f"{self.api_url}/method/friends.get?user_id={self.user_id}&fields={','.join(self.fields)}&v={self.api_version}",
                headers={"Authorization": f"Bearer {self.auth_token}"},
                timeout=self.request_timeout,
            )
            print(response.encoding)
        except (
            ConnectTimeout,
            HTTPError,
            ReadTimeout,
            Timeout,
            RequestsConnectionError,
        ) as exception:
            raise ServerResponseError(exception) from exception

        return {
            "status_code": response.status_code,
            "error": response.reason,
            "data": response.json(),
        }
