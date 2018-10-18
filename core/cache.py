#!/usr/bin/python3
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Caching.
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

from core.base import TsubamePersistentBase

import blitzdb
import twitter
import copy
import time
import operator

class AccountInfoCache(TsubamePersistentBase):
    """Cache for user data associated with Tsubame accounts."""

    CACHE_TIMEOUT = 900  # 15 minutes/one Twitter rate limit window

    PRIVATE_LISTS_KEY = "private_lists"
    PRIVATE_LIST_COUNT_KEY = "private_list_count"
    PUBLIC_LISTS_KEY = "public_lists"
    PUBLIC_LIST_COUNT_KEY = "public_list_count"

    data_defaults = {
        "account_username" : None,
        "user_info" : {},
        "private_lists" : [],
        "public_lists" : [],
        "last_updated" : None  # epoch if set
    }

    @classmethod
    def new(cls, db, account_username):
        data = AccountInfoCacheData(copy.deepcopy(cls.data_defaults))
        data.account_username = account_username
        return cls(db, data)

    @classmethod
    def from_db(cls, db, account_username):
        data = db.get(AccountInfoCacheData, {"account_username" : account_username})
        return cls(db, data)

    def __init__(self, db, data):
        super(AccountInfoCache, self).__init__(db, data)

    def clear(self):
        """Clear the cache."""
        self.log.debug("clearing account user info cache for %s", self.data.account_username)
        self.data.user_info.clear()
        self.data.private_lists.clear()
        self.data.public_lists.clear()

    @property
    def valid(self):
        if not self.last_updated:
            # never updated - not valid
            return False
        elif time.time() - self.last_updated > self.CACHE_TIMEOUT:
            # timed out - not valid
            return False
        elif not self.data.user_info:
            # no user info - not valid
            # (even if there is information about lists)
            return False
        else:
            return True

    @property
    def user_info(self):
        list_info = {
            self.PRIVATE_LISTS_KEY : self.private_lists,
            self.PRIVATE_LIST_COUNT_KEY : len(self.private_lists),
            self.PUBLIC_LISTS_KEY : self.public_lists,
            self.PUBLIC_LIST_COUNT_KEY : len(self.public_lists)
        }
        return self.data.user_info, list_info

    @property
    def private_lists(self):
        return self.data.private_lists

    @property
    def public_lists(self):
        return self.data.public_lists

    @user_info.setter
    def user_info(self, new_user_info):
        # store the user info
        self.data.user_info = new_user_info
        # record when the main cache has been created
        self.data.last_updated = time.time()

    def add_lists(self, private_lists, public_lists):
        """Add more lists to user info cache.

        :param list private_lists: private lists instances to add
        :param list public_lists: public lists instances to add
        """
        for l in private_lists:
            self.data.private_lists.append(l.AsDict())
        for l in public_lists:
            self.data.public_lists.append(l.AsDict())
        # sort the lists alphabetically by name in place
        self.data.private_lists.sort(key=operator.itemgetter('name'))
        self.data.public_lists.sort(key=operator.itemgetter('name'))

    @property
    def last_updated(self):
        return self.data.last_updated


class AccountInfoCacheData(blitzdb.Document):
    pass


class MessageCache(TsubamePersistentBase):

    data_defaults = {"messages" : [],
                     "maximum_number_of_messages" : 1000,
                     "last_updated" : None  # epoch if set
                     }

    def __init__(self, db, data):
        super(MessageCache, self).__init__(db, data)
        self._messages = None

    @property
    def pk(self):
        """Just return the data class instance public key.
        
        Used to tell the MessageCache instances apart.        
        """
        return self.data.pk

    def _load_messages(self):
        """Get implementation specific message class instances."""
        raise NotImplementedError

    @property
    def messages(self):
        if self._messages is None:
            self._load_messages()
        return self._messages

    @property
    def last_updated(self):
        return self.data.last_updated

    @property
    def maximum_number_of_messages(self):
        return self.data.maximum_number_of_messages

    @maximum_number_of_messages.setter
    def maximum_number_of_messages(self, new_maximum_number):
        self.data.maximum_number_of_messages = new_maximum_number

    def _do_add_messages(self, messages):
        """Store implementation specific message class instances."""
        raise NotImplementedError

    def add_messages(self, messages):
        if self._messages is None:
            self._load_messages()
        self._do_add_messages(messages)
        # check if we are not over limit
        if len(self.data.messages) > self.maximum_number_of_messages:
            # discard older messages to fit under the limit
            split_index = len(self.data.messages) - self.maximum_number_of_messages
            self.data.messages = self.data.messages[split_index]

    def clear(self):
        self.data.messages.clear()
        self.data.last_updated = None

class TweetCacheData(blitzdb.Document):
    pass

class TweetCache(MessageCache):

    data_defaults = copy.deepcopy(MessageCache.data_defaults)

    @classmethod
    def new(cls, db):
        data = TweetCacheData(copy.deepcopy(cls.data_defaults))
        return cls(db, data)

    @classmethod
    def from_db(cls, db, pk):
        data = db.get(TweetCacheData, {"pk" : pk})
        return cls(db, data)

    def _load_messages(self):
        # create Twitter Status instances from the dicts stored in BlitzDB
        try:
            self._messages = [twitter.models.Status.NewFromJsonDict(m) for m in self.data.messages]
        except Exception:
            self.log.exception("cache loading failed, clearing cache")
            self.data.messages = []
            self._messages = []

    def _do_add_messages(self, messages):
        # first add the Status instances to the instance cache
        self._messages.extend(messages)
        # then add the dicts corresponding to the Status instances to backing data class
        for message in messages:
            message_dict = message.AsDict()
            # Fixup some issues with the AsDict() method not being fully compatible
            # with NewFromJsonDict().
            message_dict["entities"] = {}
            for key in ("urls", "user_mentions", "hashtags", "media"):
                if key in message_dict:
                    message_dict["entities"][key] = message_dict[key]
                    del message_dict[key]
            self.data.messages.append(message_dict)