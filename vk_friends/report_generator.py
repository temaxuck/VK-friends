import csv
import json
import os
import typing as t
from abc import ABC, abstractmethod

from vk_friends.exceptions import ApiParameterError, ServerResponseError
from vk_friends.constants import FORMATS_SUPPORTED, VK_GENDERS
from vk_friends.field_handlers import bdate_handler


class ReportGenerator(ABC):
    indent = 2
    fields = ["first_name", "last_name", "bdate"]
    fields_handlers = {
        "country": lambda value: value if not value else value.get("title"),
        "city": lambda value: value if not value else value.get("title"),
        "sex": lambda value: VK_GENDERS[value],
        "bdate": bdate_handler
    }

    def __init__(
        self,
        auth_token: str,
        user_id: str,
        report_path: t.Union[str, os.PathLike] = "./report",
        fields: t.List[str] = None,
    ) -> None:
        self.auth_token = auth_token
        self.user_id = user_id

        # path handling
        if os.path.isdir(report_path):
            self.report_path = os.path.join(
                report_path, "report" + self.get_extension()
            )
        else:
            filename, file_extension = os.path.splitext(report_path)
            if file_extension:
                self.report_path = report_path
            else:
                self.report_path = filename + self.get_extension()

        if fields:
            self.fields = fields

    def check_for_exceptions(self, fetch_response: dict) -> None:
        if fetch_response["status_code"] != 200:
            raise ServerResponseError(
                f"Could not get proper response from API. Status code: {fetch_response['status_code']}; Error: {fetch_response['error']}"
            )

        if "error" in fetch_response["data"]:
            raise ApiParameterError(
                f"Could not properly request API. Status code: {fetch_response['data']['error']['error_code']}; Error: {fetch_response['data']['error']['error_msg']}"
            )

    def handle_field(self, field: "str", value: t.Any) -> t.Any:
        try:
            return self.fields_handlers[field](value)
        except KeyError:
            return value

    @abstractmethod
    def get_extension(self) -> str:
        return NotImplemented

    @abstractmethod
    def _initialize_document(self) -> str:
        return NotImplemented

    @abstractmethod
    def _prepare_item(self, item: dict) -> t.Any:
        return NotImplemented

    @abstractmethod
    def _conclude_document(self) -> str:
        return NotImplemented

    @abstractmethod
    def generate_report(self, data_fetcher: t.Generator) -> None:
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
    def get_extension(self) -> str:
        return ".csv"

    def _initialize_document(self) -> str:
        return NotImplemented

    def _prepare_item(self, item) -> dict:
        return {
            field: self.handle_field(field, item.get(field)) for field in self.fields
        }

    def _conclude_document(self) -> str:
        return NotImplemented

    def generate_report(self, data_fetcher) -> None:
        with open(
            self.report_path, "w", newline="", encoding="utf-8-sig"
        ) as file_stream:
            writer = csv.DictWriter(file_stream, fieldnames=self.fields)
            writer.writeheader()

            for fetch_response in data_fetcher:
                self.check_for_exceptions(fetch_response)

                if "response" in fetch_response["data"]:
                    for friend in fetch_response["data"]["response"]["items"]:
                        writer.writerow(self._prepare_item(friend))


class TsvReportGenerator(ReportGenerator):
    def get_extension(self) -> str:
        return ".tsv"

    def _initialize_document(self) -> str:
        return NotImplemented

    def _prepare_item(self, item: dict) -> dict:
        return {
            field: self.handle_field(field, item.get(field)) for field in self.fields
        }

    def _conclude_document(self) -> str:
        return NotImplemented

    def generate_report(self, data_fetcher: t.Generator) -> None:
        with open(
            self.report_path, "w", newline="", encoding="utf-8-sig"
        ) as file_stream:
            writer = csv.DictWriter(file_stream, fieldnames=self.fields, delimiter="\t")
            writer.writeheader()

            for fetch_response in data_fetcher:
                self.check_for_exceptions(fetch_response)

                if "response" in fetch_response["data"]:
                    for friend in fetch_response["data"]["response"]["items"]:
                        writer.writerow(self._prepare_item(friend))


class JsonReportGenerator(ReportGenerator):
    def get_extension(self) -> str:
        return ".json"

    def _initialize_document(self) -> str:
        return "\n".join(
            [
                "{",
                f'  "auth_token": "{self.auth_token}",',
                f'  "user_id": "{self.user_id}",',
                '  "friends": [\n',
            ]
        )

    def _prepare_item(self, item: dict) -> dict:
        level = 2
        item_to_proceed = {
            field: self.handle_field(field, item.get(field)) for field in self.fields
        }
        json_string = json.dumps(
            item_to_proceed,
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

    def generate_report(self, data_fetcher: t.Generator) -> None:
        file_stream = open(f"{self.report_path}", "wb")
        file_stream.write(bytes(self._initialize_document(), "utf-8"))

        for fetch_response in data_fetcher:
            self.check_for_exceptions(fetch_response)

            if "response" in fetch_response["data"]:
                for friend in fetch_response["data"]["response"]["items"]:
                    file_stream.write(bytes(self._prepare_item(friend), "utf-8"))

        file_stream.seek(-2, os.SEEK_END)
        file_stream.truncate()
        file_stream.write(bytes(self._conclude_document(), "utf-8"))
        file_stream.close()
