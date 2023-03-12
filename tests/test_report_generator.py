"""Unit-tests used in testing
all units of module vk_friends.report_generator
"""

import unittest
import unittest.mock

import vk_friends.report_generator

from vk_friends.report_generator import (
    ReportGenerator,
    ReportGeneratorFactory,
    CsvReportGenerator,
    TsvReportGenerator,
    JsonReportGenerator,
)
from vk_friends.constants import FORMATS_SUPPORTED
from vk_friends.exceptions import ApiParameterError


class TestReportGeneratorFactory(unittest.TestCase):
    """Test case for ReportGeneratorFactory class"""

    def test_get_report_generator_valid_args(self):
        """
        ReportGeneratorFactory.get_report_generator() is given valid
        arguments (FORMATS_SUPPORTED.CSV as report_format).
        report_generator.get_extension() should be equal to ".csv"
        """

        report_generator = ReportGeneratorFactory.get_report_generator(
            "", "", report_format=FORMATS_SUPPORTED.CSV, report_path=""
        )
        self.assertEqual(report_generator.get_extension(), ".csv")

    def test_get_report_generator_invalid_report_format(self):
        """
        ReportGeneratorFactory.get_report_generator() is given invalid
        report_format ("txt").
        report_generator.get_extension() should raise NotImplementedError
        """

        with self.assertRaises(NotImplementedError):
            _ = ReportGeneratorFactory.get_report_generator(
                "", "", report_format="txt", report_path=""
            )

    def test_get_report_generator_invalid_fields(self):
        """
        If any field in specified fields is incorrect,
        report_generator._prepare_item(
            api_response_item_without_invalid_field
        )
        should return handled item with invalid field equal to None
        """

        report_generator = ReportGeneratorFactory.get_report_generator(
            "",
            "",
            report_format=FORMATS_SUPPORTED.CSV,
            report_path="",
            fields=["test_field"],
        )
        api_response_item = {}
        prepared_item = report_generator._prepare_item(api_response_item)

        self.assertEqual(prepared_item, {"test_field": None})


class TestReportGenerator(unittest.TestCase):
    """Test case for ReportGenerator abstract class"""

    def test_call_report_generator_abstract_methods(self):
        """
        Call of abstract class ReportGenerator it's abstract
        methods should raise TypeError.
        """

        with self.assertRaises(TypeError):
            report_generator = ReportGenerator("", "")
            report_generator.get_extension()


class TestCsvReportGenerator(unittest.TestCase):
    """
    Test case for CsvReportGenerator class - implementation
    of abstract class ReportGenerator
    """

    report_generator = None
    all_fields_item = None
    few_fields_item = None

    def setUp(self):
        self.report_generator = CsvReportGenerator(
            "test_token",
            "test_user_id",
            report_path="./report.csv",
            fields=[
                "first_name",
                "last_name",
                "country",
                "city",
                "bdate",
                "sex",
            ],
        )

        self.all_fields_item = {
            "id": "test_id",
            "bdate": "2.7.1998",
            "country": {"id": 1, "title": "test_country_name"},
            "city": {"id": 1, "title": "test_city_name"},
            "track_code": "test_track_code",
            "sex": 2,
            "first_name": "test_fname",
            "last_name": "test_lname",
            "can_access_closed": True,
            "is_closed": False,
        }

        self.few_fields_item = {
            "id": "test_id",
            "track_code": "test_track_code",
            "sex": 2,
            "first_name": "test_fname",
            "last_name": "test_lname",
            "can_access_closed": True,
            "is_closed": False,
        }

    def test_get_extension(self):
        """
        return value of self.report_generator.get_extension() should be
        equal to ".csv"
        """
        self.assertEqual(self.report_generator.get_extension(), ".csv")

    def test_initialize_document(self):
        """
        return value of self.report_generator._initialize_document() should be
        equal to "# auth_token: test_token\n# user_id: test_user_id\n"
        """
        self.assertEqual(
            self.report_generator._initialize_document(),
            "# auth_token: test_token\n# user_id: test_user_id\n",
        )

    def test_prepare_item_all_fields_item(self):
        """
        return value of self.report_generator._prepare_item(self.all_fields_item) should be
        equal to {'first_name': 'test_fname', 'last_name': 'test_lname', 'country':
        'test_country_name', 'city': 'test_country_name', 'bdate': '1998-07-02T00:00:00.000',
        'sex': 'Мужской'}
        """
        self.assertEqual(
            self.report_generator._prepare_item(self.all_fields_item),
            {
                "first_name": "test_fname",
                "last_name": "test_lname",
                "country": "test_country_name",
                "city": "test_city_name",
                "bdate": "1998-07-02T00:00:00.000",
                "sex": "Мужской",
            },
        )

    def test_prepare_item_few_fields_item(self):
        """
        return value of self.report_generator._prepare_item(self.few_fields_item) should be
        equal to {'first_name': 'test_fname', 'last_name': 'test_lname', 'country':
        None, 'city': None, 'bdate': None, 'sex': 'Мужской'}
        """
        self.assertEqual(
            self.report_generator._prepare_item(self.few_fields_item),
            {
                "first_name": "test_fname",
                "last_name": "test_lname",
                "country": None,
                "city": None,
                "bdate": None,
                "sex": "Мужской",
            },
        )

    def test_conclude_document(self):
        """
        return value of self.report_generator._conclude_document() should be
        equal to NotImplemented
        """
        self.assertEqual(self.report_generator._conclude_document(), NotImplemented)

    def test_generate_report(self):
        """
        self.report_generator.generate_report(data_fetcher()) should
        write to file: "# auth_token: test_token\n# user_id: test_user_id\r\n"
        (skipping this), "first_name,last_name,country,city,bdate,sex\r\n",
        "test_fname,test_lname,test_country_name,test_city_name,1998-07-02T00:00:00.000,Мужской\r\n"
        """
        open_mock = unittest.mock.mock_open()

        def data_fetcher():
            open_mock.return_value.write.assert_called_with(
                "first_name,last_name,country,city,bdate,sex\r\n"
            )
            yield {
                "status_code": 200,
                "error": "OK",
                "data": {
                    "response": {
                        "count": 57,
                        "items": [self.all_fields_item],
                    }
                },
            }
            open_mock.return_value.write.assert_called_with(
                "test_fname,test_lname,test_country_name,test_city_name,"
                "1998-07-02T00:00:00.000,Мужской\r\n"
            )

        with unittest.mock.patch(
            "vk_friends.report_generator.open", open_mock, create=True
        ):
            self.report_generator.generate_report(data_fetcher())

        open_mock.assert_called_with(
            "./report.csv", "w", newline="", encoding="utf-8-sig"
        )


class TestTsvReportGenerator(unittest.TestCase):
    """
    Test case for TsvReportGenerator class - implementation
    of abstract class ReportGenerator. Some tests are omitted,
    whereas TsvReportGenerator is almost identical to
    CsvReportGenerator.
    """

    report_generator = None
    all_fields_item = None
    few_fields_item = None

    def setUp(self):
        self.report_generator = TsvReportGenerator(
            "test_token",
            "test_user_id",
            report_path="./report.tsv",
            fields=[
                "first_name",
                "last_name",
                "country",
                "city",
                "bdate",
                "sex",
            ],
        )

        self.all_fields_item = {
            "id": "test_id",
            "bdate": "2.7.1998",
            "country": {"id": 1, "title": "test_country_name"},
            "city": {"id": 1, "title": "test_city_name"},
            "track_code": "test_track_code",
            "sex": 2,
            "first_name": "test_fname",
            "last_name": "test_lname",
            "can_access_closed": True,
            "is_closed": False,
        }

    def test_get_extension(self):
        """
        return value of self.report_generator.get_extension() should be
        equal to ".tsv"
        """
        self.assertEqual(self.report_generator.get_extension(), ".tsv")

    def test_generate_report(self):
        """
        self.report_generator.generate_report(data_fetcher()) should
        write to file: "# auth_token: test_token\n# user_id: test_user_id\r\n"
        (skipping this), "first_name\tlast_name\tcountry\tcity\tbdate\tsex\r\n",
        "test_fname\ttest_lname\ttest_country_name\ttest_city_name\t"
        "1998-07-02T00:00:00.000\tМужской\r\n"
        """
        open_mock = unittest.mock.mock_open()

        def data_fetcher():
            open_mock.return_value.write.assert_called_with(
                "first_name\tlast_name\tcountry\tcity\tbdate\tsex\r\n"
            )
            yield {
                "status_code": 200,
                "error": "OK",
                "data": {
                    "response": {
                        "count": 57,
                        "items": [self.all_fields_item],
                    }
                },
            }
            open_mock.return_value.write.assert_called_with(
                "test_fname\ttest_lname\ttest_country_name\ttest_city_name\t"
                "1998-07-02T00:00:00.000\tМужской\r\n"
            )

        with unittest.mock.patch(
            "vk_friends.report_generator.open", open_mock, create=True
        ):
            self.report_generator.generate_report(data_fetcher())

        open_mock.assert_called_with(
            "./report.tsv", "w", newline="", encoding="utf-8-sig"
        )


class TestJsonReportGenerator(unittest.TestCase):
    """
    Test case for JsonReportGenerator class - implementation
    of abstract class ReportGenerator
    """

    report_generator = None
    all_fields_item = None
    few_fields_item = None

    def setUp(self):
        self.report_generator = JsonReportGenerator(
            "test_token",
            "test_user_id",
            report_path="./report.json",
            fields=[
                "first_name",
                "last_name",
                "country",
                "city",
                "bdate",
                "sex",
            ],
        )

        self.all_fields_item = {
            "id": "test_id",
            "bdate": "2.7.1998",
            "country": {"id": 1, "title": "test_country_name"},
            "city": {"id": 1, "title": "test_city_name"},
            "track_code": "test_track_code",
            "sex": 2,
            "first_name": "test_fname",
            "last_name": "test_lname",
            "can_access_closed": True,
            "is_closed": False,
        }

        self.few_fields_item = {
            "id": "test_id",
            "track_code": "test_track_code",
            "sex": 2,
            "first_name": "test_fname",
            "last_name": "test_lname",
            "can_access_closed": True,
            "is_closed": False,
        }

    def test_get_extension(self):
        """
        return value of self.report_generator.get_extension() should be
        equal to ".csv"
        """
        self.assertEqual(self.report_generator.get_extension(), ".json")

    def test_initialize_document(self):
        """
        return value of self.report_generator._initialize_document() should be
        equal to "# auth_token: test_token\n# user_id: test_user_id\n"
        """
        self.assertEqual(
            self.report_generator._initialize_document(),
            "{\n"
            '  "auth_token": "test_token",\n'
            '  "user_id": "test_user_id",\n'
            '  "friends": [\n',
        )

    def test_prepare_item_all_fields_item(self):
        """
        testing whether return value of
        self.report_generator._prepare_item(self.all_fields_item) is valid
        """
        self.assertEqual(
            self.report_generator._prepare_item(self.all_fields_item),
            "    {\n"
            '      "first_name": "test_fname",\n'
            '      "last_name": "test_lname",\n'
            '      "country": "test_country_name",\n'
            '      "city": "test_city_name",\n'
            '      "bdate": "1998-07-02T00:00:00.000",\n'
            '      "sex": "Мужской"\n'
            "    },\n",
        )

    def test_prepare_item_few_fields_item(self):
        """
        testing whether return value of
        self.report_generator._prepare_item(self.few_fields_item) is valid
        """
        self.assertEqual(
            self.report_generator._prepare_item(self.few_fields_item),
            "    {\n"
            '      "first_name": "test_fname",\n'
            '      "last_name": "test_lname",\n'
            '      "country": null,\n'
            '      "city": null,\n'
            '      "bdate": null,\n'
            '      "sex": "Мужской"\n'
            "    },\n",
        )

    def test_conclude_document(self):
        """
        return value of self.report_generator._conclude_document() should be
        equal to NotImplemented
        """
        self.assertEqual(self.report_generator._conclude_document(), "\n  ]\n}")

    def test_generate_report(self):
        """
        testing whether report generator writing valid file with
        self.report_generator.generate_report(data_fetcher())
        """
        open_mock = unittest.mock.mock_open()

        def data_fetcher():
            open_mock.return_value.write.assert_called_with(
                b"{\n"
                b'  "auth_token": "test_token",\n'
                b'  "user_id": "test_user_id",\n'
                b'  "friends": [\n'
            )
            yield {
                "status_code": 200,
                "error": "OK",
                "data": {
                    "response": {
                        "count": 57,
                        "items": [self.all_fields_item],
                    }
                },
            }
            open_mock.return_value.write.assert_called_with(
                b"    {\n"
                b'      "first_name": "test_fname",\n'
                b'      "last_name": "test_lname",\n'
                b'      "country": "test_country_name",\n'
                b'      "city": "test_city_name",\n'
                b'      "bdate": "1998-07-02T00:00:00.000",\n'
                b'      "sex": "\xd0\x9c\xd1\x83\xd0\xb6\xd1\x81\xd0\xba\xd0\xbe\xd0\xb9"\n'
                b"    },\n"
            )

        with unittest.mock.patch(
            "vk_friends.report_generator.open", open_mock, create=True
        ):
            self.report_generator.generate_report(data_fetcher())
            open_mock.return_value.write.assert_called_with(b"\n  ]\n}")

        open_mock.assert_called_with("./report.json", "wb")
