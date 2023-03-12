"""report_generator.py
Module contains logic used in generating reports.
You may create ReportGenerator instance using this 
example:
    from vk_friends.report_generator import ReportGeneratorFactory
    
    ReportGeneratorFactory.get_report_generator(
        auth_token="token",
        user_id="user_id",
        report_format=(
            FORMATS_SUPPORTED.CSV
        ), # from vk_friends.constants import FORMATS_SUPPORTED
        report_path="."
    )
"""

import csv
import json
import os
import typing as t
from abc import ABC, abstractmethod
from pathlib import Path

from vk_friends.exceptions import ApiParameterError, ServerResponseError
from vk_friends.constants import FORMATS_SUPPORTED, VK_GENDERS
from vk_friends.field_handlers import bdate_handler


class ReportGenerator(ABC):
    """Abstract class for all report report generators.

    Methods:
        check_for_exceptions(self, fetch_response: dict) -> None:
            checks whether response from API server is valid
        handle_field(self, field: str, value: t.Any) -> t.Any:
            adapts field of item for report. Returns adapted value.

    Abstract methods:
        get_extension(self) -> str:
            returns report file's extension
        _initialize_document(self) -> str:
            returns string to write in the beginning of file
        _prepare_item(self, item: dict) -> dict:
            returns prepared item for writing it in the report file
        _conclude_document(self) -> str:
            returns string to write in the end of file
        generate_report(self, data_fetcher: t.Generator) -> None:
            writes report in the file

    Args:
        indent (int): number of spaces used in indent
        fields (List[str]): fields to fetch from API
        fields_handlers (dict): handlers for each field (see fields)


    Raises:
        ServerResponseError: _description_
        ApiParameterError: _description_

    Returns:
        _type_: _description_
    """

    indent = 2
    fields = ["first_name", "last_name", "bdate"]
    fields_handlers = {
        "country": lambda value: value if not value else value.get("title"),
        "city": lambda value: value if not value else value.get("title"),
        "sex": lambda value: VK_GENDERS[value],
        "bdate": bdate_handler,
    }

    def __init__(
        self,
        auth_token: str,
        user_id: str,
        report_path: t.Union[str, os.PathLike] = "./report",
        fields: t.List[str] = None,
    ) -> None:
        """Initialize object

        Args:
            auth_token (str): authentication token (see dev.vk.com, how to get one)
            user_id (str): id of the user whose friends we want to see through
            report_path (t.Union[sreport_path (t.Union[str, os.PathLike]): path to save
                report file. Can be directory (in this case the report file will be saved
                in provided directory with name report.{extension}) or full path (for
                example, /home/reports/report.{extension}) ('./report' by default)
            fields (t.List[str], optional): fields to fetch from API (None by default).
        """
        self.auth_token = auth_token
        self.user_id = user_id

        # report_path handling
        if os.path.isdir(report_path):
            # if report_path is directory report full path is
            # report_path + default name + extension
            self.report_path = os.path.join(
                report_path, "report" + self.get_extension()
            )
        else:
            # else checking whether file's extension provided in
            # report_path
            filename, file_extension = os.path.splitext(report_path)
            if file_extension:
                self.report_path = report_path
            else:
                self.report_path = filename + self.get_extension()

        if fields:
            self.fields = fields

    def check_for_exceptions(self, fetch_response: dict) -> None:
        """Checks whether response from API server is valid.
        Else raise error.

        Args:
            fetch_response (dict): response from API server

        Raises:
            ServerResponseError: Response status is not OK
            ApiParameterError: API responded with error
        """
        if fetch_response["status_code"] != 200:
            # Response status is not OK
            raise ServerResponseError(
                "Could not get proper response from API. Status code:"
                f"{fetch_response['status_code']};"
                f"Error: {fetch_response['error']}"
            )

        if "error" in fetch_response["data"]:
            # API responded with error
            raise ApiParameterError(
                "Could not properly request API. Status code:"
                f"{fetch_response['data']['error']['error_code']};"
                f"Error: {fetch_response['data']['error']['error_msg']}"
            )

    def handle_field(self, field: str, value: t.Any) -> t.Any:
        """Returns value valid for writing in report file for
        specified field. For each field uses handler specified
        in self.fields_handlers[field]. If no handler found (
        KeyError raised) returns value as is.

        Args:
            field (str): field to be handled
            value (t.Any): value that item.get('field') returns
        """
        try:
            return self.fields_handlers[field](value)
        except KeyError:
            return value

    def generate_report(self, data_fetcher: t.Generator) -> None:
        """Wrapper around self._generate_report.

        Args:
            data_fetcher (t.Generator): generator function that
                incrementally fetches data from API.
        """
        path = Path(self.report_path)
        print(f"Creating file {path.absolute()}")

        self._generate_report(data_fetcher)

        print(f"Saving report into {path.absolute()}")

    @abstractmethod
    def get_extension(self) -> str:
        """Get report file's extension

        Returns:
            str: report file's extension
        """
        return NotImplemented

    @abstractmethod
    def _initialize_document(self) -> str:
        """Get string to write in the beginning of file

        Returns:
            str: string to write in the beginning of file
        """
        return NotImplemented

    @abstractmethod
    def _prepare_item(self, item: dict) -> t.Any:
        """Get prepared item for writing it in the report file.
        Usually handle_field method is used to extract values valid
        for writing in report file from each field of item.

        Args:
            item (dict): `user` object that is to be prepared
                for writing in report file

        Returns:
            dict: valid item for writing in report file
        """
        return NotImplemented

    @abstractmethod
    def _conclude_document(self) -> str:
        """Get string to write in the end of file

        Returns:
            str: string to write in the end of file
        """
        return NotImplemented

    @abstractmethod
    def _generate_report(self, data_fetcher: t.Generator) -> None:
        """Write report in the file. Gets data from data_fetcher.
        data_fetcher shall be generator function that incrementally
        fetches data from API.

        Args:
            data_fetcher (t.Generator): generator function that
                incrementally fetches data from API.
        """
        return NotImplemented


class ReportGeneratorFactory:
    """Factory that is used to create needed ReportGenerator
    instance according to what report_format provided.
    """

    @classmethod
    def get_report_generator(
        cls,
        auth_token: str,
        user_id: str,
        report_format: FORMATS_SUPPORTED,
        report_path: t.Union[str, os.PathLike],
        fields: t.List[str] = None,
    ) -> ReportGenerator:
        """Get ReportGenerator instance according to provided
        report_format.

        Args:
            auth_token (str): authentication token (see dev.vk.com, how to get one)
            user_id (str): id of the user whose friends we want to see through
            fields: t.List[str] = ["first_name", "last_name", "bdate"],
            report_format (FORMATS_SUPPORTED): supported report format
                (to see all supported formats check out FORMATS_SUPPORTED)
            report_path (t.Union[str, os.PathLike]): path to save report to

        Raises:
            NotImplementedError: specified report_format is not supported
            by this factory yet.


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
    """ReportGenerator for csv format."""

    def get_extension(self) -> str:
        return ".csv"

    def _initialize_document(self) -> str:
        return "\n".join(
            [f"# auth_token: {self.auth_token}", f"# user_id: {self.user_id}\n"]
        )

    def _prepare_item(self, item: dict) -> dict:
        return {
            field: self.handle_field(field, item.get(field)) for field in self.fields
        }

    def _conclude_document(self) -> str:
        return NotImplemented

    def _generate_report(self, data_fetcher: t.Generator) -> None:
        with open(
            self.report_path, "w", newline="", encoding="utf-8-sig"
        ) as file_stream:
            file_stream.write(self._initialize_document())
            writer = csv.DictWriter(file_stream, fieldnames=self.fields)
            writer.writeheader()

            for fetch_response in data_fetcher:
                self.check_for_exceptions(fetch_response)

                if "response" in fetch_response["data"]:
                    for friend in fetch_response["data"]["response"]["items"]:
                        writer.writerow(self._prepare_item(friend))


class TsvReportGenerator(ReportGenerator):
    """ReportGenerator for tsv format."""

    def get_extension(self) -> str:
        return ".tsv"

    def _initialize_document(self) -> str:
        return "\n".join(
            [f"# auth_token: {self.auth_token}", f"# user_id: {self.user_id}\n"]
        )

    def _prepare_item(self, item: dict) -> dict:
        return {
            field: self.handle_field(field, item.get(field)) for field in self.fields
        }

    def _conclude_document(self) -> str:
        return NotImplemented

    def _generate_report(self, data_fetcher: t.Generator) -> None:
        # same implementation as csv but use tab as delimiter
        with open(
            self.report_path, "w", newline="", encoding="utf-8-sig"
        ) as file_stream:
            file_stream.write(self._initialize_document())
            writer = csv.DictWriter(
                file_stream,
                fieldnames=self.fields,
                delimiter="\t",  # use tab as delimiter
            )
            writer.writeheader()

            for fetch_response in data_fetcher:
                self.check_for_exceptions(fetch_response)

                if "response" in fetch_response["data"]:
                    for friend in fetch_response["data"]["response"]["items"]:
                        writer.writerow(self._prepare_item(friend))


class JsonReportGenerator(ReportGenerator):
    """ReportGenerator for json format."""

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

    def _prepare_item(self, item: dict) -> str:
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
            + f"{json_string[:-1]}"  # json string without closing bracket
            + (level * self.indent * " " + "},\n")  # adding indent and closing bracket
        )

    def _conclude_document(self) -> str:
        return "\n".join(["\n  ]", "}"])

    def _generate_report(self, data_fetcher: t.Generator) -> None:
        file_stream = open(f"{self.report_path}", "wb")
        file_stream.write(bytes(self._initialize_document(), "utf-8"))

        data_was_fetched = False

        for fetch_response in data_fetcher:
            self.check_for_exceptions(fetch_response)

            if "response" in fetch_response["data"]:
                for friend in fetch_response["data"]["response"]["items"]:
                    file_stream.write(bytes(self._prepare_item(friend), "utf-8"))

            data_was_fetched = True

        if data_was_fetched:
            file_stream.seek(-2, os.SEEK_END)
        file_stream.truncate()
        file_stream.write(bytes(self._conclude_document(), "utf-8"))
        file_stream.close()
