import json
import os
import typing as t
from abc import ABC, abstractmethod

from vk_friends.formats_supported import FORMATS_SUPPORTED
from vk_friends.exceptions import ServerResponseError, ApiParameterError


class ReportGenerator(ABC):
    indent = 2

    def __init__(
        self,
        auth_token: str,
        user_id: str,
        report_path: t.Union[str, os.PathLike] = "./report",
        fields: t.List[str] = ["first_name", "last_name", "bdate"],
    ) -> None:
        self.auth_token = auth_token
        self.user_id = user_id
        self.report_path = report_path
        self.fields = fields

    @abstractmethod
    def _initialize_document(self) -> str:
        return NotImplemented

    @abstractmethod
    def _prepare_item(self) -> str:
        return NotImplemented

    @abstractmethod
    def _conclude_document(self) -> str:
        return NotImplemented

    @abstractmethod
    def generate_report(self) -> None:
        return NotImplemented


class ReportGeneratorFactory:
    @classmethod
    def get_report_generator(
        self,
        auth_token: str,
        user_id: str,
        report_format: FORMATS_SUPPORTED,
        report_path: t.Union[str, os.PathLike],
        fields: t.List[str] = ["first_name", "last_name", "bdate"],
    ) -> ReportGenerator:
        """Get ReportGenerator instance according to provided
        report_format.

        Args:
            report_format (FORMATS_SUPPORTED): supported report format
                (to see all supported formats check out FORMATS_SUPPORTED)
            report_path (t.Union[str, os.PathLike]): path to save report to

        Raises:
            NotImplementedError: specified report_format is not supported
            by this app yet.


        Returns:
            ReportGenerator: implementation of abstract class ReportGenerator
        """
        if report_format == FORMATS_SUPPORTED.CSV:
            return CsvReportGenerator(auth_token, user_id, report_path, fields)
        elif report_format == FORMATS_SUPPORTED.TSV:
            return TsvReportGenerator(auth_token, user_id, report_path, fields)
        elif report_format == FORMATS_SUPPORTED.JSON:
            return JsonReportGenerator(auth_token, user_id, report_path, fields)
        else:
            raise NotImplementedError(
                f"No implementation for report generator of format: {report_format}"
            )


class CsvReportGenerator(ReportGenerator):
    def _initialize_document(self) -> str:
        return ""

    def _prepare_item(self) -> str:
        return ""

    def _conclude_document(self) -> str:
        return ""

    def generate_report(self) -> None:
        ...


class TsvReportGenerator(ReportGenerator):
    def _initialize_document(self) -> str:
        return ""

    def _prepare_item(self) -> str:
        return ""

    def _conclude_document(self) -> str:
        return ""

    def generate_report(self) -> None:
        ...


class JsonReportGenerator(ReportGenerator):
    def _initialize_document(self) -> str:
        return "\n".join(
            [
                "{",
                f'  "auth_token": "{self.auth_token}",',
                f'  "user_id": "{self.user_id}",',
                '  "friends": [\n',
            ]
        )

    def _prepare_item(self, item):
        level = 2
        json_string = json.dumps(
            item,
            indent=self.indent + level * self.indent,
            separators=(",", ": "),
            ensure_ascii=False,
        )
        return (
            (level * self.indent * " ")
            + f"{json_string[:-1]}"
            + (level * self.indent * " " + "},\n")
        )

    def _conclude_document(self) -> str:
        return "\n".join(["\n  ]", "}"])

    def generate_report(self, data_fetcher) -> None:
        file_stream = open(f"{self.report_path}.json", "wb")
        file_stream.write(bytes(self._initialize_document(), "utf-8"))
        for fetch_response in data_fetcher:
            if fetch_response["status_code"] != 200:
                raise ServerResponseError(
                    f"Could not get proper response from API. Status code: {fetch_response['status_code']}; Error: {fetch_response['error']}"
                )

            if "error" in fetch_response["data"]:
                raise ApiParameterError(
                    f"Could not properly request API. Status code: {fetch_response['data']['error']['error_code']}; Error: {fetch_response['data']['error']['error_msg']}"
                )

            if "response" in fetch_response["data"]:
                for friend in fetch_response["data"]["response"]["items"]:
                    file_stream.write(bytes(self._prepare_item(friend), "utf-8"))

        file_stream.seek(-2, os.SEEK_END)
        file_stream.truncate()
        file_stream.write(bytes(self._conclude_document(), "utf-8"))
        file_stream.close()
