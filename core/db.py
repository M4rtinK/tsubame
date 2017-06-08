# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Database handling.
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

import os
import logging

from core.base import TsubameBase
import blitzdb

MAIN_DB_FOLDER = "main_db"
TWEET_CACHE_DB_FOLDER = "tweet_cache_db"

log = logging.getLogger("core.db")

class CustomFileBackend(blitzdb.FileBackend):
    """Custom file backend subclass with single instance behavior added."""

    def __init__(self, path, **kwargs):
        super(CustomFileBackend, self).__init__(path, **kwargs)
        self._single_instance_classes = {}

    def get(self, cls, query, single_instance=False):
        """Custom get() with single instance behavior added."""
        if single_instance:
            # TODO: locking ?
            loaded_data = super(CustomFileBackend, self).get(cls, query)
            already_loaded_data = self._single_instance_classes.get(loaded_data.pk)
            if already_loaded_data:
                return already_loaded_data
            else:
                self._single_instance_classes[loaded_data.pk] = loaded_data
                return loaded_data
        else:
            return super(CustomFileBackend, self).get(cls, query)

    def filter(self, cls_or_collection, query, initial_keys=None, single_instance=False):
        """Custom filter() with single instance behavior added."""
        if single_instance == True:
            results = super(CustomFileBackend, self).filter(cls_or_collection, query, initial_keys)
            single_instance_results = []
            for result in results:
                existing_instance = self._single_instance_classes.get(result.pk)
                if existing_instance:
                    single_instance_results.append(existing_instance)
                else:
                    single_instance_results[result.pk] = result
                    single_instance_results.append(result)
                return single_instance_results
        else:
            return super(CustomFileBackend, self).filter(cls_or_collection, query, initial_keys)

    def save(self, obj, call_hook = True, single_instance=False):
        """Custom save() with single instance behavior added."""
        super(CustomFileBackend, self).save(obj, call_hook)
        if single_instance == True:
            self._single_instance_classes[obj.pk] = obj


class DatabaseManager(TsubameBase):

    def __init__(self, paths):
        super(DatabaseManager, self).__init__()
        self.paths = paths
        self._main_db = None
        self._tweet_cache_db = None

    @property
    def main(self):
        if not self._main_db:
            self._main_db = CustomFileBackend(os.path.join(self.paths.profile_path, MAIN_DB_FOLDER))
        return  self._main_db

    @property
    def tweet_cache(self):
        if not self._tweet_cache_db:
            self._tweet_cache_db = CustomFileBackend(os.path.join(self.paths.cache_folder_path, TWEET_CACHE_DB_FOLDER))
        return  self._main_db

    def commit_all(self):
        for db in (self._main_db, self._tweet_cache_db):
            if db:
                db.commit()