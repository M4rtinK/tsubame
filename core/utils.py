# -*- coding: utf-8 -*-
# modRana - shared utility classes and methods
from __future__ import with_statement # for python 2.5
import threading
import os
import sys
import subprocess
import re

from core import constants
from core import qrc

if qrc.is_qrc:
    import pyotherside

import time

import logging
log = logging.getLogger("core.utils")

class Empty(Exception):
    """Exception raised by the Synchronized circular stack"""
    pass


class SynchronizedCircularStack(object):
    """
    this should be a synchronized circular stack implementation
    * LIFO
    * once the size limit is reached, items re discarded,
      starting by the oldest ones
    * thread safe using a mutex
    maxItems sets the maximum number of items, 0=infinite size
    """

    def __init__(self, max_items=0):
        self._list = []
        self._list_lock = threading.Lock()
        self._max_items = max_items

    def push(self, item):
        """add a new item to the stack, make sure the size stays in bounds"""
        with self._list_lock:
            self._list.append(item)
            # check list size
            if self._max_items:
                # discard oldest items to get back to the limit
                while len(self._list) > self._max_items:
                    del self._list[0]

    def batch_push(self, itemList):
        """batch push items in a smart way"""
        with self._list_lock:
            # reverse the input list to simulate stack pushes
            # then combine the old list and the new one
            # and finally slice it to fit to the size limit
            itemList.reverse()
            self._list.extend(itemList)
            self._list = self._list[-self._max_items:]

    def pop(self):
        """
        NOTE: when the queue is empty, the Empty exception is raised
        """
        with self._list_lock:
            if len(self._list) == 0:
                raise Empty
            else:
                return self._list.pop()

    def pop_valid(self):
        """
        if the stack is not empty and the item is valid, return
        (popped_item, True)
        if the stack is empty and no items are available, return
        (None, True)

        this basically enables easy consuming
        th queue without having to handle the
        Empty exception
        """
        with self._list_lock:
            if len(self._list) == 0:
                return None, False
            else:
                return self._list.pop(), True

    def is_in(self, item):
        """item existence testing"""
        with self._list_lock:
            return item in self._list

#  def isInNonSync(self, item):
#    """non-synchronized version of item existence testing"""
#    return item in self.list





def is_the_string_an_image(s):
    """test if the string contains an image
    by reading its magic number"""

    # NOTE: magic numbers taken from imghdr source code

    # as most tiles are PNGs, check for PNG first
    if s[:8] == b"\211PNG\r\n\032\n":
        return True
    elif s[6:10] in (b'JFIF', b'Exif'): # JPEG in JFIF or Exif format
        return True
    elif s[:6] in (b'GIF87a', b'GIF89a'): # GIF ('87 and '89 variants)
        return True
    elif s[:2] in (b'MM', b'II', b'BM'): # tiff or BMP
        return True
    else: # probably not an image file
        return False


def create_folder_path(newPath):
    """Create a path for a directory and all needed parent folders
    -> parent directories will be created
    -> if directory already exists, then do nothing
    -> if there is another filesystem object (like a file)
    with the same name, raise an exception"""
    if not newPath:
        log.error("cannot create folder, wrong path:")
        log.error(newPath)
        return False
    if os.path.isdir(newPath):
        return True
    elif os.path.isfile(newPath):
        log.error("cannot create directory, file already exists: %s", newPath)
        return False
    else:
        log.info("creating path: %s", newPath)
        try:
            head, tail = os.path.split(newPath)
            if head and not os.path.isdir(head):
                os.makedirs(head)
            if tail:
                os.mkdir(newPath)
            return True
        except Exception:
            log.exception("path creation failed")
            return False

#from
# http://stackoverflow.com/questions/3167154/
# how-to-split-a-dos-path-into-its-components-in-python
def split_path(split_path):
    pathSplit_lst = []
    while os.path.basename(split_path):
        pathSplit_lst.append(os.path.basename(split_path))
        split_path = os.path.dirname(split_path)
    pathSplit_lst.reverse()
    return pathSplit_lst

# from:
# http://www.5dollarwhitebox.org/drupal/node/84
def bytes2pretty_unit_string(bytes):
    bytes = float(bytes)
    if bytes >= 1099511627776:
        terabytes = bytes / 1099511627776
        size = '%.2fTB' % terabytes
    elif bytes >= 1073741824:
        gigabytes = bytes / 1073741824
        size = '%.2fGB' % gigabytes
    elif bytes >= 1048576:
        megabytes = bytes / 1048576
        size = '%.2fMB' % megabytes
    elif bytes >= 1024:
        kilobytes = bytes / 1024
        size = '%.2fKB' % kilobytes
    else:
        size = '%.2fb' % bytes
    return size

def free_space_in_path(path):
    """Return free space in the given path in bytes

    :param string path: path to check
    :returns: free space in path in bytes, None if free space
              could not be determined
    :rtype: int or None
    """
    try:
        f = os.statvfs(path)
        return f.f_bsize * f.f_bavail
    except Exception:
        log.exception("using statvfs() for free space detection failed")

    # yes, this can happen even on Unix-like operating systems such as
    # Android, if the Python build that is used is incorrectly compiled
    log.debug("calling the df utility as a fallback to broken statvfs()")
    try:
        df_process = subprocess.Popen(["df", path], stdout=subprocess.PIPE)
        df_output = df_process.communicate()[0].decode('utf-8')
        # replace continuous whitespace and tabs by single whitespace
        df_output = re.sub("\s\s+", " ", df_output)
        # split by whitespace and extract free space info
        mega_bytes_available_string = df_output.split("\n")[1].split(" ")[3]
        if mega_bytes_available_string.upper().endswith("M"):
            mega_bytes_available_string = int(mega_bytes_available_string[:-1])*1024*1024
        else:
            mega_bytes_available_string = int(mega_bytes_available_string)*1024
        return mega_bytes_available_string
    except Exception:
        log.exception("calling df also failed")
        return None

def create_connection_pool(url, maxThreads=1):
    """Create the connection pool -> to facilitate socket reuse

    :param string url: root URL for the threadpool
    :param int maxThreads: pool capacity
    """
    # only import urllib3 once needed
    if sys.version_info[:2] <= (2, 5):
        from core.backports import urllib3_python25 as urllib3
    else:
        import urllib3
    return urllib3.connection_from_url(url, timeout=constants.INTERNET_CONNECTIVITY_TIMEOUT,
                                       maxsize=maxThreads, block=False)

def get_elapsed_time_string(start_timestamp):
    return "%1.2f ms" % (1000 * (time.clock() - start_timestamp))

# Note about the "internal" functions
#
# This are used to work with files that modRana ships and expects to be available
# once installed (themes, example tracklogs, default configuration files).
# These files are normally just present in the modRana installation directory,
# but in some case (running on Android) might be bundled using qrc. In such case they
# are not available like "real" files/folders and special functions need to be called
# to access them.
#
# These internal_* function serve as wrappers that make it possible to handle both "normal"
# and qrc bundled files and folders in the same way.
#
# If modRana is running from qrc, the path is expected to point
# inside the qrc bundle. If you need to work with both qrc and non-qrc paths at once
# (eq. listing stuff from qrc & from real filesystem on Android) you need to handle
# that yourself (check if path should go to qrc and not use an internal_* function). :)

def internal_listdir(path):
    """Internal listdir function that works on both normal files and files
    bundled in qrc.

    :param str path: path to the folder to list
    :returns: folder contents
    :rtype: list of strings
    """
    if qrc.is_qrc:
        return pyotherside.qrc_list_dir(path)
    else:
        return os.listdir(path)

def internal_isdir(path):
    """Internal isdir function that works on both normal files and files
    bundled in qrc.

    :param str path: path to the folder to check
    :returns: True if path is file, False if not
    :rtype: bool
    """
    if qrc.is_qrc:
        return pyotherside.qrc_is_dir(path)
    else:
        return os.path.isdir(path)

def internal_isfile(path):
    """Internal isfile function that works on both normal files and files
    bundled in qrc.

    :param str path: path to the file to check
    :returns: True if path is file, False if not
    :rtype: bool
    """
    if qrc.is_qrc:
        return pyotherside.qrc_is_file(path)
    else:
        return os.path.isfile(path)

def internal_get_file_contents(path):
    """Internal function for getting file content as bytearray,
    works both on normal files and files bundled in qrc.

    :param str path: path to the file to fetch
    :returns: file contents as bytearray
    :rtype: bytearray
    """

    if qrc.is_qrc:
        return pyotherside.qrc_get_file_contents(path)
    else:
        with open(path, 'rb') as f:
            return bytearray(f.read())