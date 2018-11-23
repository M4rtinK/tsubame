import unittest
import tempfile
import os
import sys

from core.api import get_api_key_from_file

class ApiKeysTest(unittest.TestCase):

    def api_key_from_file_test(self):
        """Check if an api key can be correctly fetched from a file."""
        # valid file
        with tempfile.NamedTemporaryFile("wt") as temp_file:
            temp_file.write('{"api_key" : "nuko"}')
            temp_file.flush()
            api_key = get_api_key_from_file(temp_file.name)
            self.assertEqual(api_key, "nuko")
        # empty file
        with tempfile.NamedTemporaryFile("wt") as temp_file:
            api_key = get_api_key_from_file(temp_file.name)
            self.assertIsNone(api_key)
        # invalid file
        with tempfile.NamedTemporaryFile("wt") as temp_file:
            temp_file.write('Kanazawa')
            api_key = get_api_key_from_file(temp_file.name)
            self.assertIsNone(api_key)
        # file that does not exist
        with tempfile.TemporaryDirectory() as temp_dir:
            api_key = get_api_key_from_file(os.path.join(temp_dir, "foo"))
            self.assertIsNone(api_key)