"""Unit-tests used in testing
all units of module vk_friends.field_handlers
"""
import unittest
import unittest.mock

from vk_friends.field_handlers import bdate_handler


class TestFieldHandlers(unittest.TestCase):
    """Test case for field_handlers module"""

    def test_bdate_handler(self):
        """If value contains year, ISO format should contain year,
        If value doesn't contain year, ISO format should put
        "-" instead of year
        If value is None, return value should be None
        """
        self.assertAlmostEqual(bdate_handler("5.9.2000"), "2000-09-05T00:00:00.000")
        self.assertAlmostEqual(bdate_handler("5.9"), "--09-05T00:00:00.000")
        self.assertAlmostEqual(bdate_handler(None), None)
