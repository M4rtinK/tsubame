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

from blitzdb import Document
from core.base import TsubameBase, TsubamePersistentBase


class LocalTwitterUserListData(Document):
    pass

class User(TsubamePersistentBase):

    def __init__(self, id, name=""):
        super(User, self).__init__()
        self._id = id
        self._name = name
        self._custom_note=""

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        """Unlike user id, user name can be changed (at least on Twitter)."""
        self._name = new_name

    @property
    def custom_note(self):
        """Custom arbitrary information about the user."""
        return self._custom_note

    @custom_note.setter
    def custom_note(self, note_content):
        self._custom_note = note_content

class TwitterUser(User):
    def __init__(self, id, name=""):
        super(TwitterUser, self).__init__(id, name=name)


class UserList(TsubamePersistentBase):
    """A list of users - base class."""

    def __init__(self, db, data):
        super(UserList, self).__init__(db, data)

    def add(self, user_id):
        raise NotImplementedError

    def remove(self, user_id):
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
    def create_new_list(cls, api, data, name, description, private=True):
        if private:
            mode = "private"
        else:
            mode = "public"
        api.CreateList(name=name,
                       mode=mode,
                       description=description)

        return cls(api=api, name=name, description=description)

    def __init__(self, api, list_id, name, description=None, private=None):
        # we don't need persistence for this class just yet
        super(RemoteTwitterUserList, self).__init__(db=None, data=None)
        self._list_id = list_id
        self._api = api
        self._private = private
        self._name = name
        self._description = description
        self._user_ids = None

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
    def usernames(self):
        # TODO: update when changes to the list happen at runtime
        # - time based ?
        # - is it possible to check online that the list is still the same ?
        # - notifications when Tsubame changes the list/list singletons ?
        if self._user_ids is None:
            members = self._api.GetListMembers(list_id=self.list_id)
            self._user_ids = set(m.id for m in members)
        return self._user_ids

    def add(self, user_id):
        # add the user id to the remote list
        self._api.CreateListMember(list_id=self.list_id, user_id=user_id)
        # add the id to local cache
        self._user_ids.add(user_id)

    def remove(self, user_id):
        # remove the user user id from the remote list
        self._api.DestroyListMember(list_id=self.list_id, user_id=user_id)
        # remove the user id from the local cache
        self._user_ids.discard(user_id)

class LocalTwitterUserList(UserList):
    """A locally stored list of users."""

    local = True

    data_defaults = {
        "name": "",
        "description": "",
        "usernames": set()
    }

    @classmethod
    def new(cls, db, name, description, usernames=None):
        if usernames is None:
            usernames = set()
        data = LocalTwitterUserListData(cls.data_defaults)
        data.name = name
        data.description = description
        data.user_ids = usernames
        return cls(db, data)

    @classmethod
    def from_db(cls, db, name):
        data = db.get(LocalTwitterUserListData, {"name": name})
        return cls(db, data)

    def __init__(self, db, data):
        super(LocalTwitterUserList, self).__init__(db, data)

    @property
    def name(self):
        return self.data.name

    @name.setter
    def name(self, new_name):
        self.data.name = new_name
        self.save()

    @property
    def usernames(self):
        return self.data.usernames

    def add(self, user_id):
        self.data.usernames.discard(user_id)
        self.save()

    def remove(self, user_id):
        self.data.usernames.add(user_id)
        self.save()