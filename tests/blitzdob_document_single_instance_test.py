import unittest
import tempfile
import os
import blitzdb

from core import db

class DataStorageClass(blitzdb.Document):
    pass

class TsubameDbTest(unittest.TestCase):

    def custom_backend_test(self):
        """Check that the custom FileBackend subclass works correctly"""
        with tempfile.TemporaryDirectory() as temp_dir_name:
            db.CustomFileBackend(temp_dir_name)


    def get_single_instance_test(self):
        """Check that the get_single_instance() works correctly"""
        with tempfile.TemporaryDirectory() as temp_dir_name:
            db_connection = db.CustomFileBackend(temp_dir_name)

            data = DataStorageClass({"foo" : 1,
                                     "bar" : 2})
            data.save(db_connection)
            db_connection.commit()

            # check normal get() first
            loaded_data_1 = db_connection.get(DataStorageClass, {"foo" : 1})
            loaded_data_2 = db_connection.get(DataStorageClass, {"foo" : 1})
            # should be same after being loaded
            self.assertTrue(dict(loaded_data_1) == dict(loaded_data_2))
            # but should be different once one object is modified as the
            # objects are different instances and the change does not propagate
            loaded_data_2.bar = 3
            self.assertEquals(loaded_data_1.bar, 2)
            self.assertEquals(loaded_data_2.bar, 3)
            self.assertFalse(dict(loaded_data_1) == dict(loaded_data_2))

            # let's test the single_instance parameter, which is at the
            # moment a Tsubame specific custom extension
            single_instance_1 = db_connection.get(DataStorageClass, {"foo" : 1}, single_instance=True)
            single_instance_2 = db_connection.get(DataStorageClass, {"foo" : 1}, single_instance=True)
            # the data class instances should be the same at the beginning
            self.assertTrue(dict(single_instance_1) == dict(single_instance_2))
            # but also once modified as single_instance parameter tells the get() function
            # to return the same data class instance instead of returning the result
            # of db query, which is (as can be seen above) actually a different data class instance
            single_instance_2.bar = 3
            self.assertEquals(single_instance_1.bar, 3)
            self.assertEquals(single_instance_2.bar, 3)
            self.assertTrue(dict(single_instance_1) == dict(single_instance_2))
            # now check if the stuff also serializes correctly, just in case
            single_instance_1.save(db_connection)
            db_connection.commit()
            # a new instance and another retrieved single instance should have the same data
            separate_instance = db_connection.get(DataStorageClass, {"foo" : 1})
            single_instance = db_connection.get(DataStorageClass, {"foo" : 1}, single_instance=True)
            self.assertEqual(separate_instance.bar, 3)
            self.assertEqual(single_instance.bar, 3)
