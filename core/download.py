# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Robust data download.
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

import requests
import os

from core import utils

import logging
log = logging.getLogger("core.download")

def download_file_(url, download_folder, filename):
    # try to make sure the download directory exists
    path_to_file = os.path.join(download_folder, filename)
    log.debug("downloading URL: %s to: %s", url, path_to_file)
    if not utils.create_folder_path(download_folder):
        log.error("can't create folder for the file download")
        return False
    # NOTE the stream=True parameter
    # TODO: proper error handling/reporting ;-P
    r = requests.get(url, stream=True)
    with open(path_to_file, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
    return True