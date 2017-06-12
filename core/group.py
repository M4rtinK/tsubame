#----------------------------------------------------------------------------
# Persistent element grouping support.
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

import copy

from threading import RLock

from core.base import TsubamePersistentBase
from core import filter
from core import stream

class Group(TsubamePersistentBase):
    """And ordered serializable group of items.
    
    Supports atomic operations on the contained group.
    """

    data_defaults = {"members" : []}

    def __init__(self, db, data):
        super(Group, self).__init__(db, data)
        self._group_lock = RLock()
        self._members = []

    def add(self, item):
        with self._group_lock:
            # the items to be added need to be
            # persistent class instances
            self.data.members.append(item.data)
            self._members.append(item)

    def clear(self):
        with self._group_lock:
            self.data.members.clear()
            self._members.clear()

    def _load_members(self):
        raise NotImplementedError

    @property
    def members(self):
        with self._group_lock:
            return self._members

    def pop(self, index):
        with self._group_lock:
            self.data.members.pop(index)
            return self._members.pop(index)

    # NOTE: The reordering operations need to be always done
    #       in the backing filter data list as well to keep
    #       them in sync.

    def swap(self, item_1, item_2):
        # TODO
        raise NotImplementedError

    def swap_by_index(self):
        # TODO
        raise NotImplementedError

    def replace_items(self, new_items):
        with self._group_lock:
            self._members.clear()
            self.data.members.clear()
            self._members = new_items
            self.data.members = [i.data for i in new_items]

    def __repr__(self):
        return "%s containing %s" % (self.__class__.__name__, self.members)


class FilterGroupData(blitzdb.Document):
    pass


class FilterGroup(Group):

    data_defaults = copy.deepcopy(Group.data_defaults)

    @classmethod
    def new(cls, db):
        data = FilterGroupData(copy.deepcopy(cls.data_defaults))
        return cls(db, data)

    def __init__(self, db, data):
        super(FilterGroup, self).__init__(db, data)
        with self._group_lock:
            self._load_members()

    def _load_members(self):
        for item_data in self.data.members:
            # Fetch the functional filter class based
            # based on data class.
            cls = filter.CLASS_MAP.get(item_data.__class__)
            if cls is None:
                self.log.error("Filter class class not found for data: %s",
                                item_data)
            else:
                self._members.append(cls(self.db, item_data))

    def filter_messages(self, messages):
        for single_filter in self.members:
            messages = single_filter.filter_messages(messages)
        return list(messages)  # make sure we return a list of messages


class InputGroupData(blitzdb.Document):
    pass


class InputGroup(Group):

    data_defaults = copy.deepcopy(Group.data_defaults)

    @classmethod
    def new(cls, db):
        data = InputGroupData(copy.deepcopy(cls.data_defaults))
        return cls(db, data)

    def __init__(self, db, data):
        super(InputGroup, self).__init__(db, data)
        with self._group_lock:
            self._load_members()

    def _load_members(self):
        for item_data in self.data.members:
            # Fetch the functional input class based
            # based on data class.
            cls = stream.CLASS_MAP.get(item_data.__class__)
            if cls is None:
                self.log.error("Source class class not found for data: %s", item_data)
            else:
                self._members.append(cls(self.db, item_data))

    @property
    def messages(self):
        """Get a combined list of all messages from the sources.
        
        TODO: time/message id based sorting ?
        """
        message_list = []
        for member in self.members:
            message_list.extend(member.messages)
        return message_list

    def refresh(self):
        """Refresh all sources and return list of all new messages."""
        new_messages = []
        for source in self.members:
            new_messages.extend(source.refresh())
        return new_messages


