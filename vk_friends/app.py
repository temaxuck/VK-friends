""" VKFriends application module"""

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

from vk_friends.constants import FORMATS_SUPPORTED
from vk_friends.report_generator import ReportGeneratorFactory
from vk_friends.exceptions import ServerResponseError, ApiParameterError


class VKFriends:
    """The VKFriends object is used to generate reports of vk users
    that a specific user has as friends. Accessing information through
    public vk API.
    """

    api_url = "https://api.vk.com"
    api_version = "5.131"
    request_timeout = 30
    fields = [
        "first_name",
        "last_name",
        "country",
        "city",
        "bdate",
        "sex",
    ]  # specific values to fetch from API
    limit = 100

    def __init__(
        self,
        auth_token: str,
        user_id: str,
        report_format: t.Union[str, FORMATS_SUPPORTED] = FORMATS_SUPPORTED.CSV,
        report_path: t.Union[str, os.PathLike] = "./report",
        api_version: str = None,
        api_url: str = None,
        request_timeout: float = None,
        limit: int = None,
    ) -> None:
        """
        Initialize VKFriends app

        Args:
            auth_token (str): authentication token (see dev.vk.com, how to get one)
            user_id (str): id of the user whose friends we want to see through
            report_format (FORMATS_SUPPORTED): format of the report (supported formats
                specified in enumeration class FORMATS SUPPORTED)
            report_path (t.Union[str, os.PathLike]): path to save report file. Can be
                directory (in this case the report file will be saved in provided
                directory with name report.{extension}) or full path (for example, /home/
                reports/report.{extension}) ('./report' by default)
            api_version (str): vk API version (5.131 by default)
            request_timeout (float): time (in seconds) in which app will stop
                trying to request API server (30 by default)
            limit (int): number of items to fetch from API per one request (100
                by default)
        """
        self.auth_token = auth_token
        self.user_id = user_id
        self.report_format = (
            FORMATS_SUPPORTED(report_format)
            if isinstance(report_format, str)
            else report_format
        )
        self.report_path = report_path

        if api_version:
            self.api_version = api_version

        if api_url:
            self.api_url = api_url

        if request_timeout:
            self.request_timeout = request_timeout

        if limit:
            self.limit = limit

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
            self.auth_token,
            self.user_id,
            self.report_format,
            self.report_path,
            self.fields,
        )

        fetcher = self.fetch_friend_list()
        report_generator.generate_report(fetcher)

    def fetch_friend_list(self) -> t.Generator:
        """Fetch vk api to get a list of friends of a user
        who's id is specified in self.user_id. The response is
        getting broken to chunks (getting `self.limit` friends per
        request). Once recieved list of friends is empty the
        generator stops trying to fetch

        Raises:
            ServerResponseError: Could not establish connection
                with API host (self.api_url)

        Returns:
            t.Generator: generator-function

        Yields:
            dict: {
                "status_code": (int) response status code,
                "error": (str) response error reason,
                "data": (dict) response itself (json format)
            }
        """
        current_page = 0
        while True:
            try:
                params = {
                    "offset": current_page * self.limit,
                    "count": self.limit,
                    "order": "name",
                    "user_id": self.user_id,
                    "fields": ",".join(self.fields),
                    "v": self.api_version,
                }

                response = requests.get(
                    url=f"{self.api_url}/method/friends.get",
                    params=params,
                    headers={"Authorization": f"Bearer {self.auth_token}"},
                    timeout=self.request_timeout,
                )
            except (
                ConnectTimeout,
                HTTPError,
                ReadTimeout,
                Timeout,
                RequestsConnectionError,
            ) as exception:
                raise ServerResponseError(exception) from exception

            data = response.json()
            try:
                if not data["response"]["items"]:
                    break
            except KeyError:
                yield {
                    "status_code": response.status_code,
                    "error": response.reason,
                    "data": response.json(),
                }
                break
            yield {
                "status_code": response.status_code,
                "error": response.reason,
                "data": response.json(),
            }

            current_page += 1
