import unittest
import tempfile
import os
import sys

import blitzdb
from core.account import TwitterAccount

class TwitterAccountClassTest(unittest.TestCase):

    def account_test(self):
        """Check if twitter_accounts can be properly instantiated"""
        with tempfile.TemporaryDirectory() as temp_dir_name:
            db = blitzdb.FileBackend(temp_dir_name)

            account = TwitterAccount.new(db, username="avatar", token="oxium",
                                         token_secret="radium", name="Steve")
            self.assertEquals(account.username, "avatar")
            self.assertEquals(account.name, "Steve")
            self.assertEquals(account.token, "oxium")
            self.assertEquals(account.token_secret, "radium")

    def serialisation_test(self):
        """Check that twitter_accounts can be serialized and deserialized"""
        with tempfile.TemporaryDirectory() as temp_dir_name:
            db = blitzdb.FileBackend(temp_dir_name)

            account = TwitterAccount.new(db, username="avatar", token="oxium",
                                         token_secret="radium", name="Steve")

            # check that the temporary folder exists (just in case)
            self.assertTrue(os.path.isdir(temp_dir_name))

            # serialize the account to the database
            account.save(commit=True)

            # deserialize the account from the file
            loaded_account = TwitterAccount.from_db(db, username="avatar")

            # check that the deserialized account has the expected properties
            self.assertEquals(loaded_account.username, "avatar")
            self.assertEquals(loaded_account.name, "Steve")
            self.assertEquals(loaded_account.token, "oxium")
            self.assertEquals(loaded_account.token_secret, "radium")
