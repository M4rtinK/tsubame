import unittest
import tempfile

import blitzdb
from core.db import CustomFileBackend
from core.user import TwitterUser, LocalTwitterUserList, UsernameNotInList

class UserTest(unittest.TestCase):
    def twitter_user_test(self):
        """Check the Twitter user class"""

        with tempfile.TemporaryDirectory() as temp_dir_name:
            db = CustomFileBackend(temp_dir_name)
            user = TwitterUser.new(db, username="monty", name="Python")
            user.description = "ni"
            user.custom_note = "shrubbery"
            self.assertEquals(user.username, "monty")
            self.assertEquals(user.name, "Python")
            self.assertEquals(user.description, "ni")
            self.assertEquals(user.custom_note, "shrubbery")


    def twitter_user_single_instance_test(self):
        """Check Twitter user class single instance behavior"""
        with tempfile.TemporaryDirectory() as temp_dir_name:
            db = CustomFileBackend(temp_dir_name)
            user = TwitterUser.new(db, username="monty", name="Python")
            user.description = "ni"
            user.custom_note = "shrubbery"
            self.assertEquals(user.username, "monty")
            self.assertEquals(user.name, "Python")
            self.assertEquals(user.description, "ni")
            self.assertEquals(user.custom_note, "shrubbery")
            user.save(commit=True)

            same_user = TwitterUser.from_db(db, username="monty")
            self.assertIs(user.data, same_user.data)

            # If we try to create a user that already exists in the database,
            # no new backing data should be created and if given user data class instance
            # was already seen, it should be returned (eq. single instance behavior).
            also_same_user = TwitterUser.new(db, username="monty", name="Python 3")
            self.assertIs(same_user.data, also_same_user.data)
            self.assertIs(user.data, also_same_user.data)
            # the different name should be ignored in this case
            self.assertEquals(user.username, "monty")
            self.assertEquals(user.name, "Python")
            self.assertEquals(user.description, "ni")
            self.assertEquals(user.custom_note, "shrubbery")
            # just in case also check that attribute changes do propagate
            also_same_user.custom_note="elderberry"
            self.assertEquals(also_same_user.custom_note, "elderberry")
            self.assertEquals(same_user.custom_note, "elderberry")
            self.assertEquals(user.custom_note, "elderberry")


    def local_twitter_user_list_test(self):
        """Check local Twitter user list class works correctly"""
        with tempfile.TemporaryDirectory() as temp_dir_name:
            db = CustomFileBackend(temp_dir_name)
            serval = TwitterUser.new(db, username="serval", name="Saabaru")
            serval.description="Is a friend that can jump high."
            serval.custom_note="catchphrase: Sugoi!"
            serval.save(commit=True)
            kaban = TwitterUser.new(db, username="kaban", name="Kaban")
            kaban.description = "Doesn't know what friend it is."
            kaban.custom_note = "catchphrase: Don't eat me!"
            mirai = TwitterUser.new(db, username="mirai", name="Mirai-san")
            mirai.description = "?"
            mirai.custom_note = "mysterious"

            # check instantiation
            user_list = LocalTwitterUserList.new(db,
                                                 name="japari list",
                                                 description="Welcome to the Japari Park!",
                                                 users=[mirai, serval])
            self.assertEquals(user_list.name, "japari list")
            self.assertEquals(user_list.description, "Welcome to the Japari Park!")
            self.assertSetEqual(set(["serval", "mirai"]), set(user_list.usernames))
            self.assertTrue("Sugoi!" in user_list.users["serval"].custom_note)

            # check that remove works
            user_list.remove(username="mirai")
            self.assertSetEqual(set(["serval"]), set(user_list.usernames))
            self.assertTrue("Sugoi!" in user_list.users["serval"].custom_note)

            # an exception should be raised when attempting to remove unknown users
            with self.assertRaises(UsernameNotInList):
                user_list.remove(username="toki")

            # check that adding works
            user_list.add(user=kaban)
            self.assertSetEqual(set(["serval", "kaban"]), set(user_list.usernames))
            self.assertTrue("Sugoi!" in user_list.users["serval"].custom_note)
            self.assertTrue("Don't eat me!" in user_list.users["kaban"].custom_note)

            # make sure the list is saved
            user_list.save(commit=True)

            # check de-serialisation
            user_list_1 = LocalTwitterUserList.from_db(db, name="japari list")
            self.assertSetEqual(set(["serval", "kaban"]), set(user_list_1.usernames))
            self.assertTrue("Sugoi!" in user_list_1.users["serval"].custom_note)
            self.assertTrue("Don't eat me!" in user_list_1.users["kaban"].custom_note)

            # both the list and users should be single instance, so test that as well
            user_list_1.users["serval"].name = "Saabaru-chan"
            self.assertEquals(user_list_1.users["serval"].name, "Saabaru-chan")
            self.assertEquals(user_list.users["serval"].name, "Saabaru-chan")
            self.assertEquals(TwitterUser.from_db(db, username="serval").name, "Saabaru-chan")
            user_list.description = "ようこそジャパリパークへ"
            self.assertEquals(user_list_1.description, "ようこそジャパリパークへ")
            # for this to work the functional object needs to be saved first, or else
            # there will not be anything in the single instance tracking dictionary
            # as apparently the save() on a class that has reference to the document
            # is not enough or uses a different backend call to save the referenced
            # document which our custom BlitzDB backend does not override (yet?)
            self.assertEquals(serval.name, "Saabaru-chan")