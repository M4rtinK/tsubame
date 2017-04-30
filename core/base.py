# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Tsubame flexible base classes
# - provide universal logging support
# - as well as generic de/serialisation
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
#--------------------------------------------------------------------------

import logging

class TsubameBase(object):
    """A common base class for non-trivial Tsubame objects.
    
    At the moment just adds a common logging mechanism.
    """
    def __init__(self):
        self._logger = None


    @property
    def log_prefix(self):
        """Log prefix for log messages originating from this class.
        
        This is the class name by default, mainly to make it easy
        to spot classes that have not overridden this by a custom
        and generally nicer log prefix.
        
        :returns: log prefix
        :rtype: str
        """
        return self.__class__.__name__

    @property
    def log(self):
        if not self._logger:
            self._logger = logging.getLogger(self.log_prefix)
        return self._logger

class TsubamePersistentBase(TsubameBase):
    """Adds a blitzdb based persistence based mechanism oon top of TsubameBase."""

    @classmethod
    def from_data(cls, data_class, json_file_path=None):
        """To be overridden by sub classes."""
        raise NotImplementedError("The from_dict() method should be implemented by sub class.")

    @classmethod
    def from_db(cls, db, data_class, properties):
        # get the class from the database based on the properties
        data_class = db.get(data_class, properties)
        # instantiate the class based on content of the data_class
        cls_instance = cls.from_data(data_class)
        # set path to db & data class used
        cls_instance.db = db
        cls_instance.data_class = data_class
        # the class instance should now be ready for use
        return cls_instance

    def to_dict(self):
        return dict()

    def __init__(self):
        super(TsubamePersistentBase, self).__init__()
        self._db = None
        self._data_class = None

    @property
    def db(self):
        return self._db

    @db.setter
    def db(self, new_db):
        self._db = new_db

    @property
    def data_class(self):
        return self._data_class

    @data_class.setter
    def data_class(self, new_data_class):
        self._data_class = new_data_class

    def save(self, commit=True):
        if self.data_class and self.db:
            self.data_class.save()
            if commit:
                self.db.commit()
        else:
            problem = "unknown issue"
            if not self.data_class and not self.db:
                problem = "data class and db not set"
            elif not self.data_class:
                problem = "data class not set"
            elif not self.db:
                problem = "db not set"
            self.log.error("can't serialize object: %s", problem)