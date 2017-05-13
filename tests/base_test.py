import unittest
import tempfile
import blitzdb

from core.base import TsubameBase, TsubamePersistentBase
from core.db import CustomFileBackend

class BaseClassTest(unittest.TestCase):

    def base_class_test(self):
        """Test base class functionality functionality"""
        base = TsubameBase()
        # log prefix should be the class name by default,
        # until overridden by a sub-class
        self.assertEquals(base.log_prefix, TsubameBase.__name__)


    def base_persistent_class_test(self):
        """Test the persistent base class"""

        class TestClassData(blitzdb.Document):
            pass

        with tempfile.TemporaryDirectory() as temp_dir_name:
            db = CustomFileBackend(temp_dir_name)
            data = TestClassData()
            tci = TsubamePersistentBase(db, data)
            self.assertEquals(tci.db, db)
            # self._data should be set to the data class
            self.assertEquals(tci._data, data)
            # an exported via the data property
            self.assertEquals(tci.data, data)
            # lets set some data to the data class
            tci.data.foo = "bar"
            tci.data.some_set = set(["blah"])
            # check the data is set
            self.assertEquals(tci.data.foo, "bar")
            self.assertTrue("blah" in tci.data.some_set)
            # now check the class can be serialized
            tci.save()
            # and deserialized
            loaded_data = db.get(TestClassData, {"foo": "bar"})
            new_tci = TsubamePersistentBase(db, loaded_data)
            # check the data was deserialized properly
            self.assertEquals(new_tci.data.foo, "bar")
            self.assertTrue("blah" in new_tci.data.some_set)

    def test_default_attributes(self):
        """Test that the data class always has default attributes"""

        class TestClass(TsubamePersistentBase):
            data_defaults = {"foo": "bar",
                             "baz" : 1}

        class TestClassData(blitzdb.Document):
            pass

        with tempfile.TemporaryDirectory() as temp_dir_name:
            db = blitzdb.FileBackend(temp_dir_name)
            data = TestClassData()
            tci = TestClass(db, data)
            # check that the expected default attributes are there
            self.assertEquals(tci.data.foo, "bar")
            self.assertEquals(tci.data.baz, 1)

    def test_expected_attributes(self):
        """Test that the data class always has expected attributes"""

        class TestClass(TsubamePersistentBase):
            data_defaults = {"foo": "bar",
                             "baz" : 1}

        class TestClassData(blitzdb.Document):
            pass

        with tempfile.TemporaryDirectory() as temp_dir_name:
            db = blitzdb.FileBackend(temp_dir_name)
            # In this case we basically simulate a case
            # where the data class instance is loaded from a database
            # by a newer version of the application, which expects
            # new attributes taht did not exist when the data class
            # was stored in the database.
            # So basically an application upgrade test with existing database.

            # before the data class instance just used to have the "foo" attribute
            data = TestClassData({"foo" : "bar"})
            self.assertTrue(hasattr(data, "foo"))
            self.assertFalse(hasattr(data, "baz"))
            tci = TestClass(db, data)
            # since then the baz attribute has been added,
            # check that the it has been added during the persistent
            # class instantiation from the data_defaults dict
            self.assertEquals(tci.data.foo, "bar")
            self.assertEquals(tci.data.baz, 1)