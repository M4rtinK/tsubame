import unittest

from core.base import TsubameBase

class BaseClassTest(unittest.TestCase):

    def base_class_test(self):
        """Test base class functionality functionality"""
        base = TsubameBase()
        # log prefix should be the class name by default,
        # until overridden by a sub-class
        self.assertEquals(base.log_prefix, TsubameBase.__name__)
        # the dictionary returned by to_dict() should be empty by default
        self.assertEquals(base.to_dict(), dict())
        # json file path should be None
        self.assertIsNone(base.json_file_path)
        # trying to call from_dict should raise an exception
        with self.assertRaises(NotImplementedError):
            base.from_dict(dictionary={})
