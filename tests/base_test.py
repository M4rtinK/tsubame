import unittest

from core.base import TsubameBase, TsubamePersistentBase

class BaseClassTest(unittest.TestCase):

    def base_class_test(self):
        """Test base class functionality functionality"""
        base = TsubameBase()
        # log prefix should be the class name by default,
        # until overridden by a sub-class
        self.assertEquals(base.log_prefix, TsubameBase.__name__)


    def base_persistent_class_test(self):
        """Test the persistent base class"""
        base = TsubamePersistentBase()
        # the dictionary returned by to_dict() should be empty by default
        self.assertEquals(base.to_dict(), dict())
        # TODO: test db de/serialisation

