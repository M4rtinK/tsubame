#!/usr/bin/python3
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Representation of users posting messages.
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

import blitzdb
from threading import RLock
from core.base import TsubamePersistentBase
from core import list as list_module

def get_user_info(api, username):
    """Return information about a user specified by screen name.

    :param api: Twitter API instance
    :param str username: screen name of user to lookup

    :return: information about the user (if any)
    """
    return api.GetUser(screen_name=username)

def get_user_lists(api, username):
    """Get lists owned by a user.

    Note that if the user corresponds to the API/account used
    private lists (if any) will be returned.
    """

class LocalTwitterUserListData(blitzdb.Document):
    pass

class UsernameNotInList(Exception):
    pass

class User(TsubamePersistentBase):

    single_data_instance = True

    data_defaults = {"username" : None,
                     "name" : None,
                     "description" : "",
                     "custom_note" : ""}

    @property
    def username(self):
        return self.data.username

    @property
    def name(self):
        return self.data.name

    @name.setter
    def name(self, new_name):
        """Unlike user id, user name can be changed (at least on Twitter)."""
        self.data.name = new_name

    @property
    def description(self):
        return self.data.description

    @description.setter
    def description(self, new_description):
        self.data.description = new_description

    @property
    def custom_note(self):
        """Custom arbitrary information about the user."""
        return self.data.custom_note

    @custom_note.setter
    def custom_note(self, note_content):
        self.data.custom_note = note_content

class TwitterUserData(blitzdb.Document):
    pass

class TwitterUser(User):

    @staticmethod
    def _get_existing(db, username):
        """Get user data from the database.
        
        Return it if it exists and return None if not.
        """
        existing_data = False
        try:
            existing_data = db.get(TwitterUserData, {"username" : username}, single_instance=True)
        except blitzdb.Document.DoesNotExist:
            return None
        return existing_data

    @classmethod
    def new(cls, db, username, name=None):
        data = cls._get_existing(db, username)
        if data is None:
            data = TwitterUserData(cls.data_defaults.copy())
            data.username = username
            if name is None:
                name = username
            data.name = name
        return cls(db, data)

    @classmethod
    def from_twitter_user(cls, db, twitter_user):
        data = cls._get_existing(db, twitter_user.screen_name)
        if data is None:
            data = TwitterUserData(cls.data_defaults.copy())
            data.username = twitter_user.screen_name
            data.name = twitter_user.name
            data.description = twitter_user.description
        return cls(db, data)

    @classmethod
    def from_db(cls, db, username):
        data = db.get(TwitterUserData, {"username" : username}, single_instance=True)
        return cls(db, data)

    def __str__(self):
        return "%s (%s) - a Twitter user" % (self.username, self.name)



class UserList(TsubamePersistentBase):
    """A list of users - base class."""

    def __init__(self, db, data):
        super(UserList, self).__init__(db, data)

    def add(self, username):
        raise NotImplementedError

    def remove(self, username):
        raise NotImplementedError

    @property
    def usernames(self):
        raise NotImplementedError

class RemoteTwitterUserList(UserList):
    """A remote user list stored as part of a Twitter user account.
    
    A list can be public or private.
    
    Public list's can be seen by all twitter users and people added to the list are notified
    about that.
    
    Private lists are visible only to the user who has created them and users are not
    notified that they have been added.
    """

    local = False

    @classmethod
    def create_new_list(cls, api, data, owner_username, name, description=None, private=True):
        new_list = list_module.create_list(api=api,
                                           list_name=name,
                                           description=description,
                                           private=private)
        return cls(api=api, list_id=new_list.id, owner_username=owner_username,
                   name=name, description=description, private=private)

    def __init__(self, api, list_id, owner_username, name, description=None, private=None):
        # we don't need persistence for this class just yet
        super(RemoteTwitterUserList, self).__init__(db=None, data=None)
        self._lock = RLock()
        self._list_id = list_id
        self._api = api
        self._private = private
        self._owner_username = owner_username
        self._name = name
        self._description = description
        self._members = None
        # a cache of member usernames for easy membership checking
        self._member_usernames = set()

    @property
    def private(self):
        return self._private

    @property
    def list_id(self):
        return self._list_id

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    @property
    def owner_username(self):
        return self._owner_username

    def _refresh_member_cache(self):
        """Refresh the member data and username cache."""
        self._members = list_module.get_list_members(api=self._api,
                                                     list_owner_username=self.owner_username,
                                                     list_name=self.name)
        self._member_usernames = set(m.id for m in self._members)

    @property
    def members(self):
        # TODO: changes could happen outside Tsubame,
        #       so it would be good to update the local cache,
        #       especially if we make the list persistent
        with self._lock:
            if self._members is None:
                # member cache not yet created, do it now
                self._refresh_member_cache()
            return self._members

    def add(self, username):
        """Add a user to the list.

        :param str username: user defined by username to add
        """
        with self._lock:
            list_module.add_user_to_list(api=self._api,
                                         list_owner_username=self.owner_username,
                                         list_name=self.name,
                                         username=username)
            # update local member cache
            self._refresh_member_cache()

    def remove(self, username):
        """Remove a user from the list.

        :param str username: user defined by username to remove
        """
        with self._lock:
            # remove the user user id from the remote list
            list_module.remove_user_from_list(api=self._api,
                                              list_owner_username=self.owner_username,
                                              list_name=self.name,
                                              username=username)
            # update local member cache
            self._refresh_member_cache()


class LocalTwitterUserList(UserList):
    """A locally stored list of users."""

    single_data_instance = True

    local = True

    data_defaults = {
        "name": "",
        "description": "",
        "users": dict(),
        "insertion_order" : []
    }

    @classmethod
    def new(cls, db, name, description, users=None):
        if users is None:
            users = []
        data = LocalTwitterUserListData(cls.data_defaults.copy())
        data.name = name
        data.description = description
        # Note that we actually don't pass the functional Twitter user
        # object instance, but just the backing data instance.
        # Looks like this should not cause any issues - at least for now. ;-)
        for user in users:
            data.users[user.username] = user.data
            data.insertion_order.append(user.username)
        return cls(db, data)

    @classmethod
    def from_db(cls, db, name):
        data = db.get(LocalTwitterUserListData, {"name": name}, single_instance=True)
        return cls(db, data)

    def __init__(self, db, data):
        super(LocalTwitterUserList, self).__init__(db, data)
        self._lock = RLock()
        self._users = None

    def _init_users(self):
        """Create functional objects for our user data."""
        self._users = {}
        for user_data in self.data.users.values():
            self._users[user_data.username] = TwitterUser(self.db, user_data)

    @property
    def name(self):
        return self.data.name

    @name.setter
    def name(self, new_name):
        self.data.name = new_name
        self.save()

    @property
    def description(self):
        return self.data.description

    @description.setter
    def description(self, new_description):
        self.data.description = new_description

    @property
    def usernames(self):
        with self._lock:
            return self.data.users.keys()

    @property
    def users(self):
        with self._lock:
            # how fast is comparing of two keys() outputs in Python ?
            if self._users is None or self._users.keys() != self.data.users.keys():
                self._init_users()
            return self._users

    def add(self, user):
        with self._lock:
            self._users[user.username] = user
            self.data.users[user.username] = user.data
            # make sure the username is not in the insertion order list
            try:
                self.data.insertion_order.remove(user.username)
            except ValueError:
                pass
            self.data.insertion_order.append(user.username)
            self.save()

    def remove(self, username):
        with self._lock:
            if username in self.data.users:
                del self._users[username]
                del self.data.users[username]
                # remove the username from the insertion order list
                try:
                    self.data.insertion_order.remove(username)
                except ValueError:
                    pass
                self.save()
            else:
                raise UsernameNotInList

    def save(self, commit=True):
        # we should use the lock also in the save function as the add
        # and remove methods modify the backing data object
        with self._lock:
            super(LocalTwitterUserList, self).save(commit=commit)
