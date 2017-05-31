# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Base class for Tsubame GUI modules
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
from core.base import TsubameBase

import blitzdb

class OptionsData(blitzdb.Document):
    pass

class GUI(TsubameBase):
    def __init__(self, tsubame):
        super(GUI, self).__init__()
        self.tsubame = tsubame

        # persistent options dictionary goes here
        self._options = self._load_options()
        # Unlike in modRana the persistent dict should
        # just hold some GUI specific stuff in Tsubame
        # with backend persistence being handled via
        # persistent classes.


    @property
    def gui_toolkit(self):
        """report which toolkit the current GUI uses"""
        return None

    def notify(self, message, ms_timeout=0):
        """handle a notification"""
        pass

    def open_url(self, url):
        """open a given URL asynchronously"""
        # the webbrowser module should be a good default
        import webbrowser
        webbrowser.open(url)

    @property
    def gui_id(self):
        return None

    @property
    def screen_wh(self):
        """In some cases, the GUI module might be able
        to get screen resolution"""
        return None

    @property
    def highDPI(self):
        """Try to guess if to show the high DPI GUI or not"""
        if self.screen_wh:
            size = max(self.screen_wh)
            device_type = self.tsubame.platform.device_type
            if size > 854 and device_type == constants.DEVICE_TYPE_SMARTPHONE:
                # high DPI smartphone
                return True
            elif size > 1024 and device_type == constants.DEVICE_TYPE_TABLET:
                # high DPI tablet
                return True
            elif size > 1920 and device_type == constants.DEVICE_TYPE_DESKTOP:
                # high DPI desktop
                return True
            else:
                return False
        else:
            return False

    def _get_style_constants(self):
        # as True == 1 and False == 0,
        # we use the highDPI boolean as a tuple index
        # * highDpi == False -> first value is used
        # * highDpi == True -> second value is used
        i = self.highDPI

        style = {
            "m" : (1, 2)[i], # approximate size multiplier
            "main" : {
                "multiplier" : (1, 1.5)[i],
                "spacing" : (8, 12)[i],
                "spacingBig" : (16, 24)[i]
            },
            "button" : {
                "selector" : {
                    "width" : (200, 300)[i],
                    "height" : (80, 120)[i],
                },
                "icon" : {
                    "size" : (80, 120)[i]
                },
                "iconGrid" : {
                    "size" : (100, 150)[i],
                    "radius" : (10, 15)[i],
                    "textSizePortrait" : (42, 60)[i],
                    "textSizeLandscape" : (36, 54)[i]
                },
                "generic" : {
                    "height" : (60, 90)[i]
                }
            },
            "dialog" : {
                "item" : {
                    "height" : (80, 120)[i]
                }
            },

            "map": {
                "button": {
                    "size": (72, 108)[i],
                    "margin": (16, 24)[i],
                    "spacing": (16, 24)[i],
                },
                "scaleBar" : {
                    "border" : (2, 3)[i],
                    "height" : (4, 6)[i],
                    "fontSize" : (24, 36)[i],
                },
                "tracklogTrace" : {
                    "width" : (10, 15)[i],
                    "color" : "blue",
                },
            },
            "listView" : {
                "spacing" : (8, 24)[i],
                "cornerRadius" : (8, 12)[i],
                "itemBorder" : (20, 30)[i],
            }
        }
        return style

    @property
    def constants(self):
        if self.tsubame.platform.platform_id == "jolla":
            defaultTheme = "silica"
        else:
            defaultTheme = "default"

        C = {
            "style": self._get_style_constants(),
            "default" : {
                "theme" : defaultTheme,
            }
        }
        return C

    @property
    def portrait(self):
        """Report if viewport is currently in portrait
        orientation

        NOTE: square screen is considered landscape

        :returns: True if in portrait, False otherwise
        :rtype: bool
        """
        w = h = 0
        screenWH = self.screen_wh
        if screenWH:
            w, h = screenWH
        return w < h

    @property
    def square(self):
        """Report if viewport is a square

        NOTE: square screen is considered landscape

        :returns: True if viewport is square, False otherwise
        :rtype: bool
        """
        w = 1
        h = 0
        screenWH = self.screen_wh
        if screenWH:
            w, h = screenWH
        return w == h

    @property
    def should_start_in_fullscreen(self):
        """Report if the GUI should start in fullscreen
        * could be required by device module
        * could be requested by CLI flag
        * could be enabled in options

        :returns: if GUI should start in fullscreen or not
        :rtype: bool
        """
        return any(
            (self.tsubame.platform.start_in_fullscreen,
               self.tsubame.args.fullscreen,
               self.get("start_in_fullscreen", False))
        )

    @property
    def show_quit_button(self):
        """Report if the GUI should show a quit button
        * could be required by device module
        * could be enabled in options

        :returns: if GUI should show quit button or not
        :rtype: bool
        """
        return any((self.tsubame.platform.needs_quit_button, self.get("showQuitButton", False)))

    def _load_options(self):
        db = self.tsubame.db.main
        try:
           options = db.get(OptionsData, {})
        except blitzdb.Document.DoesNotExist:
            options = OptionsData()
            options.backend = db
        return options

    def _save_options(self):
        self._options.save()
        self._options.backend.commit()

    def get(self, key, default_value):
        return self._options.get(key, default_value)

    def set(self, key, value):
        self._options[key] = value
        self._save_options()
