# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Android platform module.
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
from core.platform.base_platform_module import PlatformModule

MAIN_TSUBAME_DATA_FOLDER = "/sdcard/tsubame"  # main Tsubame data folder on Android

def get_module():
    return PlatformAndroid()

class PlatformAndroid(PlatformModule):
    """A Tsubame platform-specific module for Android."""

    def __init__(self):
        super(PlatformAndroid, self).__init__()
        self.tempUnfullscreen = False

    @property
    def platform_id(self):
        return "android"

    @property
    def device_name(self):
        return "Android device"

    @property
    def preferred_window_wh(self):
        #return 480, 800
        return None

    @property
    def start_in_fullscreen(self):
        return True

    @property
    def fullscreen_only(self):
        return True

    @property
    def screen_blanking_control_supported(self):
        """Screen blanking support is handled through QtQuick."""
        return False

    @property
    def needs_quit_button(self):
        return False

    @property
    def device_type(self):
        # TODO: device type detection
        return None
