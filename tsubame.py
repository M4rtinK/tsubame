#!/usr/bin/python3
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Tsubame main file.
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
import sys
import time
import os
import subprocess

start_timestamp = time.time()

tsubame = None
platform = None
gui = None

PLATFORM_MODULES_FOLDER = "core/platform"

# initialize logging
from core import tsubame_log
from core.signal import Signal
tsubame_log.init_logging()
import logging
log = logging.getLogger("")

# qrc handling
from core import qrc
USING_QRC = qrc.is_qrc
qrc.handle_qrc()

def set_correct_CWD():
    # change to folder where the main tsubame file is located
    # * this enables to run Tsubame with absolute path without adverse
    # effect such as Tsubame not finding modules, etc.
    current_absolute_path = os.path.dirname(os.path.abspath(__file__))
    if USING_QRC:
        # we are running from qrc, so just use the qrc:/ prefix as CWD,
        # no need to chdir
        current_absolute_path = "qrc:/"
    else:
        os.chdir(current_absolute_path)
    # append the path to the bundle directory so that Tsubame can fall-back
    # to it's bundled modules if a given module is not available on the system
    # - at the same time just a simple "import foo" import is enough and
    #   "from core.bundle import foo" is not needed
    sys.path.append(os.path.join(current_absolute_path, 'core', 'bundle'))
    # do the same thing for the backports folder, which serves a similar role
    # as the bundle folder (TODO: merge content of backports to bundle ?)
    sys.path.append(os.path.join(current_absolute_path, 'core', 'backports'))

# before we start importing our stuff we need to correctly setup CWD
# and Python import paths
set_correct_CWD()

# import core modules/classes
from core import startup
from core import utils
from core import paths
from core import db
from core import threads
from core import singleton
from core import account
from core import api
from core import stream
from core import platform_detection
from core import constants

# record that imports-done timestamp
imports_done_timestamp = time.time()

class Tsubame(object):
    """
    This is THE main Tsubame class.
    """

    qt5_gui_running = False

    def __init__(self):
        singleton.tsubame = self

        self.timing = []

        self.add_custom_time("Tsubame start", start_timestamp)
        self.add_custom_time("imports done", imports_done_timestamp)

        self.platform = None
        self.platform = gui

        # signals
        self.shutdown_signal = Signal()
        self.notification_triggered = Signal()

        # initialize threading
        threads.init_threading()

        # paths
        self.paths = paths.Paths(tsubame=self)


        # add the startup handling core module
        self.startup = startup.Startup(self)
        # initialize the database manager
        db.initialize_database_manager(self.paths)
        self.db = db.db_manager
        self.args = self.startup.args

        # handle tasks requested from the CLI
        self.startup.handle_CLI_tasks()

        # load the platform module
        platform_id = self.args.platform_id
        if platform_id is None:  # not set via CLI
            platform_id = platform_detection.get_best_platform_module_id()

        # We have just 3 platform modules in Tsubame at the moment so
        # might as well do the platform module loading statically for now.
        if platform_id == constants.PlatformID.PC:
            from core.platform import platform_pc as platform_module
        elif platform_id == constants.PlatformID.SAILFISH:
            from core.platform import platform_sailfish as platform_module
        elif platform_id == constants.PlatformID.ANDROID:
            from core.platform import platform_android as platform_module
        else:
            # we don't have a platform module for this platform id,
            # so log that and fall back to the PC platform module
            log.error("unknown platform id: %s", platform_id)
            log.error("falling back to using the PC platform module")
            from platform import platform_pc as platform_module

        # instantiate the platform module
        self.platform = platform_module.get_module()

        # load accounts
        account.load_accounts(main_db=self.db.main)

        # get Twitter app tokens
        twitter_key, twitter_secret = self.startup.get_twitter_app_key()

        # initialize API manager
        # - this needs to be done only after twitter_accounts are loaded
        api.initialize_api_manager(account_manager=account.account_manager,
                                   twitter_key=twitter_key,
                                   twitter_secret=twitter_secret)

        # initialize the Stream manager
        stream.initialize_stream_manager(self.db.main)

        # If we got as far as this we either need to start the GUI
        # or we are done as the GUI is already running.
        if not self.qt5_gui_running:
            self._start_qt5_gui()
        else:
            # The QML part of the Qt 5 GUI is already running,
            # so just instantiate the GUI module so that QML can use it.
            from gui.qt5.qt5_gui import Qt5GUI
            self.gui = Qt5GUI(tsubame=self)

    def _get_module_names_from_folder(self, folder, prefix='platform_'):
        """List a given folder and find all possible module names.
        
        Module names:
        Module names start with a given prefix and don't end with .pyc or .pyo.
        Consequences:
        Valid modules need to have an existing .py file or be folder-modules
        (don't name a folder module mod_foo.pyc :) ), even if they are
        actually loaded from the .pyc or .pyo in the end.
        This is done so that dangling .pyc/.pyo file from a module
        that was removed are not loaded by mistake.
        This situation shouldn't really happen if modRana is installed from a package,
        as all .pyc files are purged during package upgrade and regenerated."""
        if USING_QRC:
            # if we are running from qrc, we need to use the pyotherside function for enumerating
            # the modules stored in the qrc "bundle"
            import pyotherside
            moduleNames = filter(
                lambda x: x[0:len(prefix)] == prefix, pyotherside.qrc_list_dir(os.path.join("/", folder))
            )
        else:
            moduleNames = filter(
                lambda x: x[0:len(prefix)] == prefix, os.listdir(folder)
            )

        # remove the extension
        moduleNames = map(lambda x: os.path.splitext(x)[0], moduleNames)
        # return a set of unique module names
        # * like this, two module names will not be returned if there are
        # both py and pyc files
        return set(moduleNames)

    def _start_qt5_gui(self):
        """Start the Qt 5 GUI.
        
        This is actually a bit crazy as we basically start main.qml in qmlscene
        and then exit - qmlscene then initializes the QtQuick 2 GUI, which
        then instantiates the Tsubame class *again*, just without it
        starting qmlscene again. 
        
        The qt5_gui_running class attribute is used during this to protect against
        an infinite loop.
                
        TODO: CLI argument passing ? Well, once we have some relevant arguments I guess. ;-)
        """

        qml_main = "gui/qt5/qml/main.qml"
        # path to the component set
        universal_components_path = "gui/qt5/qml/universal_components/%s" % self.platform.universal_components_backend

        # export QML_IMPORT_DIR = /

        command = "%s %s -I %s" % (self.platform.qmlscene_command,
                                   qml_main,
                                   universal_components_path)

        subprocess.call(command, shell=True)

    @property
    def available_platform_modules_by_id(self):
        prefix = "platform_"
        module_names = self._get_module_names_from_folder(PLATFORM_MODULES_FOLDER, prefix=prefix)
        # remove the prefix and return the results
        # NOTE:
        # - .py, .pyc & .pyo should be removed already in _get_module_names_from_folder()
        # - also sort the module names alphabetically
        return sorted(map(lambda x: x[len(prefix):], module_names))


    ## STARTUP TIMING ##

    def add_time(self, message):
        timestamp = time.time()
        self.timing.append((message, timestamp))
        return timestamp

    def add_custom_time(self, message, timestamp):
        self.timing.append((message, timestamp))
        return timestamp

    def report_startup_time(self):
        if self.timing:
            log.info("** Tsubame startup timing **")

            # log device identificator and name
            if self.platform:
                device_name = self.platform.device_name
                device_string = self.platform.platform_id
                log.info("# device: %s (%s)" % (device_name, device_string))

            tl = self.timing
            startupTime = tl[0][1] * 1000
            lastTime = startupTime
            totalTime = (tl[-1][1] * 1000) - startupTime
            for i in tl:
                (message, t) = i
                t *= 1000  # convert to ms
                timeSpent = t - lastTime
                timeSinceStart = t - startupTime
                log.info("* %s (%1.0f ms), %1.0f/%1.0f ms", message, timeSpent, timeSinceStart, totalTime)
                lastTime = t
            log.info("** whole startup: %1.0f ms **" % totalTime)
        else:
            log.info("* timing list empty *")

    def shutdown(self):
        """Cleanly shutdown everything."""
        log.warning("Shutdown not yet implemented - oops! ^_~")


def start(argv=None):
    """This function is used when starting Tsubame with PyOtherSide.
    When Tsubame is started from PyOtherSide there is no sys.argv,
    so QML needs to pass it from its side.

    :param list argv: arguments the program got on cli or arguments
                      injected by QML
    """
    if not argv: argv = []
    # only assign fake values to argv if argv is empty or missing,
    # so that real command line arguments are not overwritten
    if not hasattr(sys, "argv") or not isinstance(sys.argv, list) or not sys.argv:
        log.debug("argv from QML:\n%s", argv)
        sys.argv = ["tsubame.py"]
    # only log full argv if it was extended
    if argv:
        sys.argv.extend(argv)
        log.debug("full argv:\n%s", sys.argv)

    Tsubame.qt5_gui_running = True
    global tsubame
    global platform
    global gui
    tsubame = Tsubame()
    platform = tsubame.platform
    gui = tsubame.gui

if __name__ == "__main__":
    Tsubame()
