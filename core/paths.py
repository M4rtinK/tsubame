# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Tsubame paths handling
#----------------------------------------------------------------------------
# Copyright 2012, Martin Kolman
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
#---------------------------------------------------------------------------
import os
from core import utils

import logging
log = logging.getLogger("core.paths")

# folder names
DEFAULT_PROFILE_FOLDER_NAME = "tsubame"
CACHE_FOLDER_NAME = "cache"
DEBUG_LOGS_FOLDER_NAME = "debug_logs"
DATA_FOLDER_NAME = "data"
THEME_FOLDER_NAME = "theme"
# file names
OPTIONS_FILENAME = "options.json"
VERSION_INFO_FILENAME = "version.txt"
VERSION_STRING = None

_PROFILE_FOLDER_NAME = DEFAULT_PROFILE_FOLDER_NAME

def loadVersionString():
    """ Load version string from file"""
    # try to read the version file
    versionString = get_version_string()
    if versionString is not None:
        global VERSION_STRING
        VERSION_STRING = versionString


def get_version_string():
    """ Get version string from the default version file

    :returns: version string or None if unknown
    :rtype: str or None
    """

    if os.path.exists(VERSION_INFO_FILENAME):
        try:
            with open(VERSION_INFO_FILENAME, 'r') as f:
                versionString = f.readline()
            # make sure it is string (or the conversion throws an exception)
            # and that it does not have any dangling newlines
            versionString = str(versionString).rstrip()
            return versionString
        except Exception:
            log.exception("loading version info failed")
            return None
    else:
        log.warning("local version file is missing")
        return None

## XDG path getters ##

def get_HOME_path():
    """Get the path specified by the $HOME variable

    :returns: path to current users home directory
    :rtype: str
    """

    # if $HOME is not set, return ~ in a desperate attempt
    # to save the situation
    return os.environ.get("HOME", os.path.expanduser("~"))

def get_profile_name():
    """Get name of the Tsubame profile folder

    :returns: Tsubame profile folder name
    :rtype: str
    """
    return _PROFILE_FOLDER_NAME

def set_profile_name(name):
    """Set the name of the Tsubame profile folder

    :param str name: new profile name
    """
    global _PROFILE_FOLDER_NAME
    _PROFILE_FOLDER_NAME = name

def get_XDG_config_path():
    """Check the contents of the $XDG_CONFIG_HOME/tsubame variable and
    default to $HOME/.config/tsubame if not set.

    :returns: path to the XDG config folder
    :rtype: str
    """
    return os.path.join(
        os.environ.get("$XDG_CONFIG_HOME", os.path.join(get_HOME_path(), ".config")),
        get_profile_name()
    )

def get_XDG_data_path():
    """Check the contents of the $XDG_DATA_HOME variable and
    default to "$HOME/.cache" if not set.

    :returns: path to the XDG config folder
    :rtype: str
    """
    return os.path.join(
        os.environ.get("$XDG_DATA_HOME", os.path.join(get_HOME_path(), ".local/share")),
        get_profile_name()
    )

def get_XDG_cache_path():
    """Check the contents of the $XDG_CONFIG_HOME variable and
    default to "$HOME/.local/share" if not set.

    :returns: path to the XDG config folder
    :rtype: str
    """
    return os.path.join(
        os.environ.get("$XDG_CACHE_HOME", os.path.join(get_HOME_path(), ".cache")),
        get_profile_name()
    )

def get_XDG_profile_path():
    """Return XDG-compatible profile folder path

    basically the same as get_XDG_config_path()
    """
    return get_XDG_config_path()

def get_XDG_debug_log_path():
    """Return XDG-compatible debug log folder path"""
    return os.path.join(get_XDG_data_path(), DEBUG_LOGS_FOLDER_NAME)

class Paths(object):
    """
    Handle paths to various folders:
    * main profile folder
    * tracklogs folder
    * map tiles folder
    * generic cache
    * log folder
    * POI folder
    Not only provide the paths but also assure
    that folders are created automatically if they
    don't exist yet.
    """

    def __init__(self, tsubame):
        self.tsubame = tsubame

        # TODO: actually use this
        # get profile folder path
        # -> first check for device module override
        # if self.tsubame.dmod.profile_path:
        #     self._profile_folder_path = self.tsubame.dmod.profile_path
        # else:
        #     self._profile_folder_path = self.tsubame.get_profile_path()
        # # check the profile path and create the folders if necessary

        self._profile_folder_path = get_XDG_config_path()
        utils.create_folder_path(self._profile_folder_path)

    ## Important Tsubame folders ##

    @property
    def profile_path(self):
        """return path to the profile folder"""
        # check if the path exists and create it if not
        utils.create_folder_path(self._profile_folder_path)
        return self._profile_folder_path

    @property
    def options_file_path(self):
        """return path to the options store filename"""
        return os.path.join(self.profile_path, OPTIONS_FILENAME)

    @property
    def cache_folder_path(self):
        """Return path to a folder used for caching."""
        return self._assure_path(get_XDG_cache_path())

    @property
    def log_folder_path(self):
        """return path to the log folder"""
        if self.tsubame.platform:
            path = self.tsubame.dmod.log_folder_path()
            if path is not None: # None means there is no device dependent path
                return self._assure_path(path)
            else:
                return self._assure_path_folder(self.profile_path, DEBUG_LOGS_FOLDER_NAME)
        else:
            return self._assure_path_folder(self.profile_path, DEBUG_LOGS_FOLDER_NAME)

    @property
    def theme_folder_path(self):
        """Return path to folder used to store icons."""
        return self._assure_path(os.path.join(DATA_FOLDER_NAME, THEME_FOLDER_NAME))

    @property
    def version_string(self):
        """
        return current version string or None if not available
        """
        return VERSION_STRING

    def _assure_path_folder(self, path, folder):
        """combine the given path and folder and make sure the path exists,
        return the resulting path"""
        path = os.path.join(path, folder)
        return self._assure_path(path)

    def _assure_path(self, path):
        """assure path exists and return it back"""
        # check if the path exists and create it if not
        utils.create_folder_path(path)
        return path