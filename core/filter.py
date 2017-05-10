# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Filters for filtering of messages in streams.
#
#----------------------------------------------------------------------------
# Copyright 2017, Martin Kolman
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#----------------------------------------------------------------------------

from blitzdb import Document

from core.base import TsubamePersistentBase

class Filter(TsubamePersistentBase):
    """Filtering base class."""

    data_defaults = {
        "name" : "",
        "description" : "",
        "positive" : True
    }

    def __init__(self, db, data):
        super(Filter, self).__init__(db, data)

    @property
    def positive(self):
        """Positive == matching messages will go through.
        
        Negative == matching messages will be dropped. 
        """
        return self.data.positive

    @positive.setter
    def positive(self, positive_value):
        self.data.positive = positive_value

    @property
    def name(self):
        """A human readable filter name (optional)."""
        return self.data.name

    @name.setter
    def name(self, new_name):
        self.data.name = new_name

    @property
    def description(self):
        """A human readable filter description."""
        return self.data.description

    @description.setter
    def description(self, new_description):
        self.data.description = new_description

    def filter_messages(self, messages):
        """Filter messages from iterable.
        
        And return a generator with messages matching the filter function
        and current positive/negative setting.
        """
        if self.positive:
            return (m for m in messages if self.filter_function(m))
        else:
            return (m for m in messages if not self.filter_function(m))

    def filter_function(self, message):
        """Function for matching messages according to current filter settings.
        
        Subclasses should always implement this method.
        """
        raise NotImplementedError


class TwitterUserFilterData(Document):
    pass

class TwitterUserFilter(Filter):
    """Filter messages according to a Twitter user id."""

    data_defaults = Filter.data_defaults.copy()
    data_defaults.update({
        "username" : None
    })

    @classmethod
    def new(cls, db, username):
        data = TwitterUserFilterData(cls.data_defaults)
        data.username = username
        return cls(db, data)

    @property
    def username(self):
        return self.data.username

    @username.setter
    def username(self, new_username):
        self.data.username = new_username

    def filter_function(self, message):
        #TODO: check what's actually in the results returned by python-twitter
        return message.user.screen_name == self.data.username


class TwitterUserListFilterData(Document):
    pass


class TwitterUserListFilter(Filter):
    """Filter messages according to Twitter users who sent them."""

    data_defaults = Filter.data_defaults.copy()
    data_defaults.update({
        "local_list_name" : None,
        "remote_list_id" : None
    })

    @classmethod
    def new(cls, db, user_list):
        data = TwitterUserListFilterData(cls.data_defaults)
        if user_list.local:  # local list
            data["local_list_name"] = user_list.name
        else:  # remote list
            data["remote_list_id"] = user_list.list_id
        return cls(db, data)

    def __init__(self, db, data):
        super(TwitterUserListFilter, self).__init__(db, data)
        self._user_list = None
        # TODO: list instance retrieval
        if self.data.remote_list_id:
            pass
        elif self.data.local_list_name:
            pass

    def filter_function(self, message):

        if self._user_list is None:
            self.log.warning("attempt to filter by user list without list set")
            return False
        else:
            return message.user.screen_name in self._user_list.usernames

class TwitterMediaFilterData(Document):
    pass

class TwitterMediaFilter(Filter):
    """Filter messages messages that contain media.
    
    Based on the negative property this filter can be used to either
    keep just messages that have media or to return only media-less messages.
    """

    def filter_function(self, message):
        return message.media is not None


CLASS_MAP = {
    TwitterUserFilterData : TwitterUserFilter,
    TwitterUserListFilterData : TwitterUserListFilter,
    TwitterMediaFilterData : TwitterMediaFilter
}