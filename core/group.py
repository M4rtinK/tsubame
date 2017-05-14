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

from threading import RLock

from core.base import TsubamePersistentBase
from core import filter

class Group(TsubamePersistentBase):
    """And ordered serializable group of items.
    
    Supports atomic operations on the contained group.
    """

    data_defaults = {"items" : []}

    def __init__(self, db, data):
        super(Group, self).__init__(db, data)
        self._group_lock = RLock()
        self._items = None

    def add(self, item):
        with self._group_lock:
            # the items to be added need to be
            # persistent class instances
            self.data.items.append(item.data)
            self._items.append()

    def clear(self):
        with self._group_lock:
            self.data.items.clear()
            self._items.clear()

    def _get_items(self):
        raise NotImplementedError

    @property
    def items(self):
        with self._group_lock:
            if self._items is None:
                self._items = self._get_items()
            return self._items

    def pop(self, index):
        with self._group_lock:
            self.data.items.pop(index)
            return self._items.pop(index)

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
            self._items.clear()
            self.data.items.clear()
            self._items = new_items
            self.data.items = [i.data for i in new_items]

class FilterGroupData(blitzdb.Document):
    pass

class FilterGroup(Group):

    @classmethod
    def new(cls, db):
        data = FilterGroupData(cls.data_defaults.copy())
        return cls(db, data)

    def _get_items(self):
        items = []
        for item_data in self.data.items:
            # Fetch the functional filter class based
            # based on data class.
            cls = filter.CLASS_MAP.get(item_data.__class__)
            if cls is None:
                self.log.error("Filter class class not found for data: %s",
                                item_data)
            else:
                items.append(cls(self.db, item_data))
        return items





