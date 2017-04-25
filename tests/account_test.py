import unittest
import tempfile
import os

from core.account import TwitterAccount

class TwitterAccountClassTest(unittest.TestCase):

    def account_test(self):
        account = TwitterAccount(
            id="avatar",
            name = "Steve",
            token="oxium",
            token_secret="radium"
        )
        self.assertEquals(account.id, "avatar")
        self.assertEquals(account.name, "Steve")
        self.assertEquals(account.token, "oxium")
        self.assertEquals(account.token_secret, "radium")

    def serialisation_test(self):
        with tempfile.TemporaryDirectory() as temp_dir_name:

            account_json_file = os.path.join(temp_dir_name, "account.json")

            account = TwitterAccount(
                id="avatar",
                name = "Steve",
                token="oxium",
                token_secret="radium"
            )

            # check that the temporary folder exists (just in case)
            self.assertTrue(os.path.isdir(temp_dir_name))

            # check that the file does not exist beforehand
            self.assertFalse(os.path.isfile(account_json_file))

            # the serialisation file should be None for freskly created
            # (eq. not deserialized) class instances
            self.assertIsNone(account.json_file_path)

            # set the serialisation file path path
            account.json_file_path = account_json_file

            # check that the path is correctly set
            self.assertEquals(account.json_file_path, account_json_file)

            # serialize the account to file
            account.save()

            # check that the json file was created
            self.assertTrue(os.path.isfile(account_json_file))

            # deserialize the account from the file
            loaded_account = TwitterAccount.from_json_file(account_json_file)

            # check that the deserialized account has the expected properties
            self.assertEquals(loaded_account.id, "avatar")
            self.assertEquals(loaded_account.name, "Steve")
            self.assertEquals(loaded_account.token, "oxium")
            self.assertEquals(loaded_account.token_secret, "radium")
            self.assertEquals(loaded_account.json_file_path, account_json_file)


