# -*- coding: utf-8 -*-
# Load and store dictionaries as JSON files

import os
import shutil
from threading import RLock

from core import utils

import logging
log = logging.getLogger("core.json_dict")

try:
    import json
except ImportError: # try to use local copy
    import simplejson as json

class PathNotSetException(Exception):
    pass

class JSONDict(dict):

    def __init__(self, file_path=None, dictionary=None):
        super(JSONDict, self).__init__()
        self._path = file_path
        # some operations like saving/loading/changing the path or
        # moving the backing file can't be safely done at the same
        # time so we need a mutex that makes sure only one such
        # operation is happening at a time
        self._mutex = RLock()

        if dictionary:
            self.update(dictionary)
        elif file_path:
            self.load_from_file(file_path)

    @property
    def path(self):
        """Return path to the JSON file

        :returns: path to the JSON file or None
        :rtype: str or None
        """
        return self._path

    @path.setter
    def path(self, path):
        """Set path to the JSON file

        :param str path: path to the underlying JSON file
        """
        with self._mutex:
            self._path = path

    def save_to_file(self, file_path):
        # first try to make sure the folder for storing
        # the JSON file exists
        with self._mutex:
            success = False
            if utils.create_folder_path(os.path.dirname(file_path)):
                try:
                    # the Python JSON module has some issues with serializing
                    # unicode strings, so we need to make it dump the dict to
                    # string, utf encode it and then save it to file manually
                    jsonString = json.dumps(self, ensure_ascii=False, indent=True)
                    jsonString.encode('utf8')
                    with open(file_path, "w") as f:
                        f.write(jsonString)
                    success = True
                except Exception:
                    log.exception("saving to JSON file failed")
            else:
                log.error("JSONDict: can't save file to: %s", file_path)
            return success

    def load_from_file(self, file_path):
        with self._mutex:
            if not file_path:  # even "" is wrong for a file path
                raise PathNotSetException
            success = False
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    d = json.load(f)
                    if d:
                        self.clear()
                        self.update(d)
                        success = True
            return success

    def save(self):
        """Save the dict to the currently set path

        :return: True is success, False otherwise
        :rtype: bool
        """
        with self._mutex:
            if self._path:
                self.save_to_file(self._path)
            else:
                raise PathNotSetException

    def load(self):
        """Load the dict from the currently set path"""
        with self._mutex:
            if self._path:
                self.load_from_file(self._path)
            else:
                raise PathNotSetException

    def move(self, newPath):
        """Move the backing file"""
        with self._mutex:
            if self._path:
                shutil.move(self._path, newPath)
                self._path = newPath
            else:
                raise PathNotSetException