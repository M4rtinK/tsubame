# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Tsubame flexible base class
# - provides generic de/serialisation code
# - as well as universal logging support (TBD)
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

from .json_dict import JSONDict

class TsubameBase(object):

    def __init__(self):
        self._json_file_path = None
        self._logger = None

    @classmethod
    def from_dict(cls, dictionary, json_file_path=None):
        """To be overridden by sub classes."""
        raise NotImplementedError("The from_dict() method should be implemented by sub class.")

    @classmethod
    def from_json_file(cls, json_file_path):
        # instantiate the class from the dictionary loaded from a json file
        cls_instance = cls.from_dict(dictionary=JSONDict(file_path=json_file_path))
        # set path to the origin json file
        cls_instance.json_file_path = json_file_path
        # the class instance should now be ready for use
        return cls_instance

    def to_dict(self):
        return dict()

    @staticmethod
    def save_to_json_file(dictionary, file_path):
        # If both dictionary and path are set for the
        # JSON dict, the dictionary will be loaded to the
        # object and the path set as file path.
        json_dict = JSONDict(dictionary=dictionary, file_path=file_path)
        json_dict.save()

    @property
    def json_file_path(self):
        return self._json_file_path

    @json_file_path.setter
    def json_file_path(self, file_path):
        self._json_file_path = file_path

    def save(self):
        self.save_to_json_file(dictionary=self.to_dict(),
                           file_path=self.json_file_path)

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