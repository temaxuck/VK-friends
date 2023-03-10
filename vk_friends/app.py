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
    limit = 50

    def __init__(
        self,
        auth_token: str,
        user_id: str,
        report_format: FORMATS_SUPPORTED = FORMATS_SUPPORTED.CSV,
        report_path: t.Union[str, os.PathLike] = "./report",
        api_version: str = None,
        api_url: str = None,
        request_timeout: float = None,
        limit: int = None,
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
        """Get a list of friends of a user who's id is
        specified in self.user_id

        Returns:
            tuple: (
                int: response status code,
                dict: response itself(json format)
            )
        """
        current_page = 0
        while True:
            try:
                params = {
                    "user_id": self.user_id,
                    "offset": current_page * self.limit,
                    "count": self.limit,
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
