# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Sailfish OS platform module.
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
#---------------------------------------------------------------------------
from core import constants
from core import paths
from core.platform.base_platform_module import PlatformModule
import os
import subprocess

# third party apps for Sailfish OS should use the harbour- prefix
SAILFISH_MODRANA_PROFILE_NAME = "harbour-tsubame"

def get_module():
    return PlatformSailfishOS()


class PlatformSailfishOS(PlatformModule):
    """A Sailfish OS platform module."""

    def __init__(self):
        super(PlatformSailfishOS, self).__init__()

        # override the default profile name to harbour-tsubame
        #TODO: implement this
        #paths.profile_name = SAILFISH_MODRANA_PROFILE_NAME

    @property
    def platform_id(self):
        return "jolla"

    @property
    def device_name(self):
        return "Jolla"

    @property
    def preferred_window_wh(self):
        """Jolla 1 screen resolution.
        
        TODO: Account for the Jolla Tablet, Jolla C
              and other Sailfish OS devices.
        """
        return 960, 540

    @property
    def start_in_fullscreen(self):
        return True

    @property
    def fullscreen_only(self):
        """Applications running on Sailfish@Jolla are fullscreen only."""
        return True

    @property
    def screen_blanking_control_supported(self):
        return True  # might actually not be True for Harbour version for now

    @property
    def has_buttons(self):
        # TODO: support for volume buttons
        return False


    # ** PATHS **

    # Sailfish OS uses paths based on the XDG standard,
    # and debug logs go to $HOME/Public/tsubame_debug_logs
    # so that they are easily accessible to users

    @property
    def log_folder_path(self):
        return os.path.join(paths.get_HOME_path(), "Documents", "tsubame_debug_logs")

    @property
    def needs_quit_button(self):
        """No need for a separate Quit button thanks to the the Sailfish UI."""
        return False

    @property
    def needs_back_button(self):
        return False

    @property
    def needs_page_background(self):
        return False

    @property
    def device_type(self):
        # TODO: detect Sailfish OS tablets
        return constants.DEVICE_TYPE_SMARTPHONE

    @property
    def connectivity_status(self):
        # TODO: actual connectivity tracking :)
        return True

    @property
    def universal_components_backend(self):
        """We use the Silica UC backend on Sailfish OS."""
        return "silica"

    def open_url(self, url):
        subprocess.call(["xdg-open", url])