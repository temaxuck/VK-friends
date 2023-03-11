import unittest

from vk_friends.report_generator import ReportGeneratorFactory
from vk_friends.constants import FORMATS_SUPPORTED


class TestReportGeneratorFactory(unittest.TestCase):
    def test_csv_format(self):
        """format is being sent as enum 'FORMATS_SUPPORTED'"""

        report_generator = ReportGeneratorFactory.get_report_generator(
            "", "", report_format=FORMATS_SUPPORTED.CSV, report_path=""
        )
        self.assertEqual(report_generator.get_extension(), ".csv")

    def test_csv_format(self):
        """format is being sent as str"""
        report_generator = ReportGeneratorFactory.get_report_generator(
            "", "", report_format="CSV", report_path=""
        )
        self.assertEqual(report_generator.get_extension(), ".csv")

    # with unittest.mock.patch('platform.system') as pl:
    #     pl.return_value = 'Windows'
    #     os.environ['APPDATA'] = 'balls'
    #     cdir, data_dir = config.find_config_dir('zzzz')

    #     self.assertEqual(
    #         os.path.expandvars(os.path.join('$APPDATA', 'zzzz')),
    #         cdir)
