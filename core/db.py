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

from core.base import TsubameBase
import blitzdb

MAIN_DB_FOLDER = "main_db"

class DatabaseManager(TsubameBase):

    def __init__(self, profile_path):
        super(DatabaseManager, self).__init__()
        self._profile_path = profile_path
        self._main_db = None

    @property
    def main(self):
        if not self._main_db:
            self._main_db = blitzdb.FileBackend(os.path.join(self._profile_path, MAIN_DB_FOLDER))
        return  self._main_db

    def commit_all(self):
        for db in self._main_db:
            if db:
                db.commit()