# Tsubame current platform detection
import os

from core import qrc
from core.constants import PlatformID

DEFAULT_PLATFORM_MODULE_ID = "pc"
DEFAULT_GUI_MODULE_ID = "qt5"

OS_RELEASE_FILE = "/etc/os-release"

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

    # try to detect the platform based on /etc/os-release
    if os.path.exists(OS_RELEASE_FILE):
        try:
            # As ConfigParser still can't parse INI files without any section headers,
            # we need to parse this manually, yay! :P
            # For more see: https://bugs.python.org/issue22253
            with open("/etc/os-release", "rt") as f:
                os_release_dict = {}
                for line in f:
                    k, v = line.rstrip().split("=")
                    if v.startswith('"'):
                        v = v[1:-1]
                    os_release_dict[k] = v
                os_release_id = os_release_dict.get("ID")
                if os_release_id == "sailfishos":
                    log.info("* Sailfish OS device detected")
                    return PlatformID.SAILFISH
        except:
            log.exception("os-release parsing failed")

    # check CPU architecture
    import subprocess

    proc = subprocess.Popen(['uname', '-m', ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    arch = str(proc.communicate()[0])
    if ("i686" in arch) or ("x86_64" in arch):
        log.info("* PC detected")
        return PlatformID.PC # we are most probably on a PC

    # check procFS
    if os.path.exists("/proc/cpuinfo"):
        f = open("/proc/cpuinfo", "r")
        cpuinfo = f.read()
        f.close()
        if "Nokia RX-51" in cpuinfo: # N900
            log.info("* Nokia N900 detected")
            return PlatformID.N900

    return None
