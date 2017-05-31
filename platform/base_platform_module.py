# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Base class for Tsubame platform modules.
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
from core.signal import Signal

class PlatformModule(object):
    """A Tsubame base platform module."""

    def __init__(self):
        self.internet_connectivity_changed = Signal()

    @property
    def platform_id(self):
        """Return an unique string identifying the device module."""
        return None

    @property
    def device_name(self):
        """Return a human readable name of the device."""
        return "unknown device"

    @property
    def preferred_window_wh(self):
        """Return the preferred application window size in pixels."""
        # we'll use VGA as a default value
        return 640, 480

    @property
    def start_in_fullscreen(self):
        """Return if Tsubame should be started fullscreen.
        
        NOTE: this is a default value and can be overridden by a
        user-set options key, etc.
        """
        return False

    @property
    def fullscreen_only(self):
        """Report if the platform is fullscreen-only.
        
        Some platforms are basically fullscreen-only (Harmattan),
        as applications only switch between fullscreen and a task switcher.
        """
        return False

    @property
    def screen_blanking_control_supported(self):
        """There is no universal way to control screen blanking, so its off by default.
        
        NOTE: Screen blanking can be implemented and enabled in the corresponding 
              device or gui module.
        """
        return False

    def pause_screen_blanking(self):
        """Pause screen blanking controlled by device module.        
        
        calling this method should pause screen blanking
        * on mobile devices, screen balking needs to be paused every n seconds
        * on desktop, one call might be enough, still, several calls should
        be handled without issues
        * also what about restoring the screen blanking on Desktop
          once Tsubame exits ?
        """
        pass

    @property
    def supported_gui_module_ids(self):
        """Supported GUI module IDs, ordered by preference from left to right.

        THE ":" NOTATION
        single GUI modules might support different subsets, the usability of
        these subsets can vary based on the current platform
        -> this functions enabled device modules to report which GUI subsets
        are most suitable for the given platform
        -> the string starts with the module id prefix, is separated by : and
        continues with the subset id
        EXAMPLE: ["QML:harmattan","QML:indep","GTK"]
        -> QML GUI with Harmattan Qt Components is preferred,
        QML GUI with platform independent Qt Components is less preferred
        and the GTK GUI is set as a fallback if everything else fails
        CURRENT USAGE
        there are different incompatible native Qt Component sets
        on various platforms (Harmattan QTC, Plasma Active QTC, Jolla QTC,...)
        the QML GUI aims to support most of these components sets to provide
        native look & feel and the subset id is used by the device module
        to signal the GUI module which QTC component to use
        """
        return ["qt5"] # the Qt 5 GUI is the default

    @property
    def has_notification_support(self):
        """Report if the device provides its own notification method."""
        return False

    def notify(self, message, msTimeout=0, icon=""):
        """Send a notification using platform/device specific API."""
        pass

    @property
    def has_keyboard(self):
        """Report if the device has a hardware keyboard."""
        return True

    @property
    def has_buttons(self):
        """Report if the device has some usable buttons other than a hardware keyboard."""
        if self.has_volume_keys:
            return True
        else:
            return False

    @property
    def has_volume_keys(self):
        """Report if the device has application-usable volume control keys or their equivalent.
        
        Basically basically just two nearby button that can be used for zooming up/down,
        skipping to next/previous and similar actions.
        """
        return False

    def enable_volume_keys(self):
        pass

    @property
    def profile_path(self):
        """Return path to the main profile folder or None if default path should be used.

        :returns: path to the profile folder or None
        :rtype: str or None
        """
        return None

    @property
    def needs_quit_button(self):
        """On some platforms applications need to provide their own shutdown buttons."""
        return False

    @property
    def needs_back_button(self):
        """Some platforms (Sailfish OS) don't need a in-UI back button."""
        return True

    @property
    def needs_page_background(self):
        """Some platforms (Sailfish OS) don't need a page background."""
        return True

    @property
    def handles_url_opening(self):
        """Some platform provide specific APIs for URL opening.
        
        For example, on the N900 a special DBUS command not available
        elsewhere needs to be used.
        """
        return False

    def open_url(self, url):
        """Open a URL."""
        pass

    @property
    def connectivity_status(self):
        """Report the current status of internet connectivity on the device.
        
        None - status reporting not supported or status unknown
        True - connected to the Internet
        False - disconnected from the Internet
        """
        connected = constants.InternetConnectivityStatus.OFFLINE
        # open the /proc/net/route file
        with open('/proc/net/route', 'r') as f:
            for line in f:
                # the line is delimited by tabulators
                lineSplit = line.split('\t')
                # check if the length is valid
                if len(lineSplit) >= 11:
                    if lineSplit[1] == '00000000' and lineSplit[7] == '00000000':
                        # if destination and mask are 00000000,
                        # it is probably an Internet connection
                        connected = constants.InternetConnectivityStatus.ONLINE
                        break
        return connected

    def enable_internet_connectivity(self):
        """Try to make sure that the device connects to the Internet."""
        pass

    @property
    def device_type(self):
        """Returns type of the current device.

        The device can currently be either a PC
        (desktop or laptop/notebook),
        smartphone or a tablet.
        This is currently used mainly for rough
        DPI estimation.
        Example:
        * high resolution & PC -> low DPI
        * high resolution & smartphone -> high DPI
        * high resolution & smartphone -> low DPI

        This could also be used in the future to
        use different PC/smartphone/tablet GUI styles.

        By default, the device type is unknown.
        """
        return None
