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
    data_defaults = {}

    single_data_instance = False

    def __init__(self, db, data):
        super(TsubamePersistentBase, self).__init__()
        self._db = db
        self._data = self._assure_expected_attributes(data)

    def _assure_expected_attributes(self, data):
        """Make sure the data storage class instance has all the expected fields.
        
        As the data storage class instance is accessed directly by the persistent
        class instance, there could be issues if some properties of the data class
        instance did not exist - an AttributeError would be raised.
        
        This can happen quite easily:
        - let's have persistent class instance backed by a data class instance
        - the persistent class has a property "foo", backed by the "foo" attribute         
          of the data class instance
        - the data class instance is saved to the database
        - a new property "bar" is added to the persistent class
        - the data class instance is deserialized, backing the modified persistent class
        - attempt to access the "bar" property raises an attribute error as
          the deserialized data class instance has no such attribute
          
        As it would be probably too costly (any annoying/error prone) to check
        for missing attributes of the data class instance at runtime,
        we make sure the data class instance has all expected attributes when
        the persistent class is instantiated.
        
        For this the data_defaults dictionary, which holds all expected attribute names
        and their default values is used.
        
        :param data: data class instance to be used for persistent class instantiation
        :returns: data class instance with all expected attributes
        """
        for attribute_name, default_value in self.data_defaults.items():
            if not hasattr(data, attribute_name):
                data[attribute_name] = default_value
        return data

    @property
    def db(self):
        return self._db

    @property
    def data(self):
       return self._data

    def save(self, commit=True):
        """Save backing data of this object to the database.
        
        :param bool commit: commit the save operation to the
                            database at once
        """
        self.db.save(self.data, single_instance=self.single_data_instance)
        if commit:
            self.db.commit()

    def delete(self, commit=True):
        """Delete backing data for this persistent object from the database.
        
        Note that this actually does not delete the content of
        the backing data instance.
        
        :param bool commit: commit the delete operation to the
                            database at once
        """
        self.data.delete(backend=self.db)
        if commit:
            self.db.commit()
