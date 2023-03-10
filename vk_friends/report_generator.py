import json
import os
import typing as t
from abc import ABC, abstractmethod

from vk_friends.formats_supported import FORMATS_SUPPORTED


class ReportGenerator(ABC):
    def __init__(self, report_path: t.Union[str, os.PathLike] = "./report") -> None:
        self.report_path = report_path

    @abstractmethod
    def _serialize(self, data: dict) -> None:
        return NotImplemented

    @abstractmethod
    def generate_report(self) -> None:
        return NotImplemented


class ReportGeneratorFactory:
    @classmethod
    def get_report_generator(
        self, report_format: FORMATS_SUPPORTED, report_path: t.Union[str, os.PathLike]
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
            return CsvReportGenerator(report_path)
        elif report_format == FORMATS_SUPPORTED.TSV:
            return TsvReportGenerator(report_path)
        elif report_format == FORMATS_SUPPORTED.JSON:
            return JsonReportGenerator(report_path)
        else:
            raise NotImplementedError(
                f"No implementation for report generator of format: {report_format}"
            )


class CsvReportGenerator(ReportGenerator):
    def _serialize(self, data: dict) -> None:
        return f"Some csv data: {data}"

    def generate_report(self) -> None:
        ...
        # return "Generating report...", self._serialize(data)


class TsvReportGenerator(ReportGenerator):
    def _serialize(self, data: dict) -> None:
        return f"Some tsv data: {data}"

    def generate_report(self) -> None:
        ...
        # return "Generating report...", self._serialize(data)


class JsonReportGenerator(ReportGenerator):
    def _serialize(self, data: dict) -> None:
        return f"Some json data: {data}"

    def generate_report(self) -> t.Generator:
        fs = open(f"{self.report_path}.json", "wb")
        fs.write(b"{")
        while True:
            data = yield

            if not data:
                fs.write(b"}")
                fs.close()
                raise GeneratorExit

            fs.write(
                json.dumps(
                    data, indent=2, separators=(",", ": "), ensure_ascii=False
                ).encode("utf-8")
            )

        # return "Generating report...", self._serialize(data)
