# Tsubame current platform detection
import os
import sys

from core import qrc
from core.constants import PlatformID

DEFAULT_PLATFORM_MODULE_ID = "pc"
DEFAULT_GUI_MODULE_ID = "qt5"

import logging
log = logging.getLogger("core.platform_detection")

def get_best_platform_module_id():
    log.info("** detecting current device **")

    result = _try_to_detect_platform()

    if result is not None:
        platform_module_id = result
    else:
        platform_module_id = DEFAULT_PLATFORM_MODULE_ID # use Qt5 GUI module as fallback
        log.info("* no known device detected")

    log.info("** selected %s as device module ID **" % platform_module_id)
    return platform_module_id

def _try_to_detect_platform():
    """Try to detect current device/platform."""

    # TODO: turn platform IDs to proper constants

    # qrc is currently used only on Android, so if we are running with
    # qrc, we are on Android
    if qrc.is_qrc:
        return PlatformID.ANDROID

    # check CPU architecture
    import subprocess

    proc = subprocess.Popen(['uname', '-m', ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    arch = str(proc.communicate()[0])
    if ("i686" in arch) or ("x86_64" in arch):
        log.info("* PC detected")
        return PlatformID.PC # we are most probably on a PC
    if sys.platform == "qnx6":
        log.info("* BlackBerry 10 device detected")
        return PlatformID.BB10

    try:
        import platform
        if platform.node() == "Sailfish":
            return PlatformID.SAILFISH
    except:
        log.exception("the Python stdlib platform module is apparently unusable on this platform")

    # check procFS
    if os.path.exists("/proc/cpuinfo"):
        f = open("/proc/cpuinfo", "r")
        cpuinfo = f.read()
        f.close()
        if "Nokia RX-51" in cpuinfo: # N900
            log.info("* Nokia N900 detected")
            return PlatformID.N900
        # N9 and N950 share the same device module
        elif "Nokia RM-680" in cpuinfo: # N950
            log.info("* Nokia N950 detected")
            return PlatformID.N9
        elif "Nokia RM-696" in cpuinfo: # N9
            log.info("* Nokia N9 detected")
            return PlatformID.N9
        elif "GTA02" in cpuinfo: # N9
            log.info("* Neo FreeRunner GTA02 detected")
            return PlatformID.NEO

    # check lsb_release
    try:
        proc = subprocess.Popen(['lsb_release', '-s', '-i'],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        distributionId = proc.communicate()[0].decode("utf-8").lower().strip()
        log.info("lsb_release distro id: %s ", distributionId)
        # import pdb; pdb.set_trace()
        if distributionId == 'mer':
            # TODO: could be also Nemo mobile or other Mer based distro,
            # we should probably discern those two in the future
            log.info("* Jolla (or other Mer based device) detected")
            return PlatformID.SAILFISH
    except:
        log.exception("running lsb_release during platform detection failed")

    return None


