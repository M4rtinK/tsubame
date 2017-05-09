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

from threading import RLock

from core.base import TsubameBase
from core import filter

class Group(TsubameBase):
    """And ordered serializable group of items.
    
    Supports atomic operations on the contained group.
    """

    def __init__(self, items=None):
        super(Group, self).__init__()
        self._group_lock = RLock()
        if items is None:
            items = []
        self._items = []

    def add(self, item):
        with self._group_lock:
            self._items.append()

    def clear(self):
        with self._group_lock:
            self._items.clear()

    @property
    def items(self):
        with self._group_lock:
            return self._items

    def pop(self, index):
        with self._group_lock:
            return self._items.pop(index)

    def swap(self, item_1, item_2):
        # TODO
        raise NotImplementedError

    def swap_by_index(self):
        # TODO
        raise NotImplementedError

    def replace_items(self, new_items):
        with self._group_lock:
            self._items.clear()
            self._items = new_items


class FilterGroup(Group):

    def __init__(self, items=None):
        super(FilterGroup, self).__init__(items=items)




