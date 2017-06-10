from enum import Enum

# device types
DEVICE_TYPE_DESKTOP = 1
DEVICE_TYPE_SMARTPHONE = 2
DEVICE_TYPE_TABLET = 3

# device ids


class PlatformID(Enum):
    PC = "pc"
    SAILFISH = "sailfish"
    ANDROID = "android"
    N900 = "n900"
    BB10 = "bb10"
    N9 = "n9"
    NEO = "neo"

class InternetConnectivityStatus(Enum):
    ONLINE = True
    OFFLINE = False
    UNKNOWN = None

class MessageType(Enum):
    TWEET = "tweet"