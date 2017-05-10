import unittest
import tempfile
import blitzdb

from core import filter

class FilterTestCase(unittest.TestCase):

    def instantiation_test(self):
        with tempfile.TemporaryDirectory() as temp_dir_name:
            db = blitzdb.FileBackend(temp_dir_name)

            # first lets test the Twitter user filter
            twitter_user_filter = filter.TwitterUserFilter.new(db=db, username="such_user")
            self.assertEquals(twitter_user_filter.username, "such_user")
            self.assertEquals(twitter_user_filter.name, "")
            self.assertEquals(twitter_user_filter.description, "")
            self.assertEquals(twitter_user_filter.positive, True)
            # check if properties can be set and changed
            twitter_user_filter.name = "wow"
            twitter_user_filter.description = "such"
            twitter_user_filter.username = "very_user"
            twitter_user_filter.positive = False
            self.assertEquals(twitter_user_filter.name, "wow")
            self.assertEquals(twitter_user_filter.description, "such")
            self.assertEquals(twitter_user_filter.username, "very_user")
            self.assertEquals(twitter_user_filter.positive, False)

            # check if the filter can be saved to the database
            twitter_user_filter.save()
            db.commit()
            pk = twitter_user_filter.data.pk
            del twitter_user_filter

            # and now check if the functional class can be succesfully
            # instantiated from the data class with all expected
            # properties in place
            data = db.get(filter.TwitterUserFilterData, {"pk" : pk})
            twitter_user_filter = filter.TwitterUserFilter(db, data)
            self.assertEquals(twitter_user_filter.name, "wow")
            self.assertEquals(twitter_user_filter.description, "such")
            self.assertEquals(twitter_user_filter.username, "very_user")
            self.assertEquals(twitter_user_filter.positive, False)
