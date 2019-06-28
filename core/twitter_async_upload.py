# The MIT License (MIT)

# Copyright (c) 2016- @TwitterDev

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# based on:
# https://github.com/twitterdev/large-video-upload-python


import os
import sys
import time

import json
import requests
from requests_oauthlib import OAuth1

import logging
log = logging.getLogger("core.twitter_async_upload")

MEDIA_ENDPOINT_URL = 'https://upload.twitter.com/1.1/media/upload.json'
POST_TWEET_URL = 'https://api.twitter.com/1.1/statuses/update.json'

CONSUMER_KEY = 'your-consumer-key'
CONSUMER_SECRET = 'your-consumer-secret'
ACCESS_TOKEN = 'your-access-token'
ACCESS_TOKEN_SECRET = 'your-access-secret'

VIDEO_FILENAME = 'path/to/video/file'

def get_oauth(consumer_key, consumer_secret, token_key, token_secret):
    """Get an OAuth session."""
    oauth = OAuth1(consumer_key,
                   client_secret=consumer_secret,
                   resource_owner_key=token_key,
                   resource_owner_secret=token_secret)
    return oauth

class MediaUpload(object):

    def __init__(self, file_name, oauth, media_category, progress_callback=None):
        """Defines video tweet properties."""
        self.media_filename = file_name
        self.oauth = oauth
        self.media_category = media_category
        self.progress_callback = progress_callback
        self.total_bytes = os.path.getsize(self.media_filename)
        self.media_id = None
        self.processing_info = None

    def upload_init(self):
        """Initializes Upload."""
        log.debug('upload init')

        request_data = {
            'command': 'INIT',
            'media_type': 'video/mp4',
            'total_bytes': self.total_bytes,
            'media_category': self.media_category
        }

        req = requests.post(url=MEDIA_ENDPOINT_URL, data=request_data, auth=self.oauth)
        log.debug("REQ")
        log.debug(req)
        media_id = req.json()['media_id']

        self.media_id = media_id

        log.debug('Media ID: %s' % str(media_id))

    def upload_append(self):
        """Uploads media in chunks and appends to chunks uploaded."""
        segment_id = 0
        bytes_sent = 0
        file = open(self.media_filename, 'rb')

        while bytes_sent < self.total_bytes:
            chunk = file.read(1 * 1024 * 1024)

            log.debug('append')

            request_data = {
                'command': 'APPEND',
                'media_id': self.media_id,
                'segment_index': segment_id
            }

            files = {
                'media': chunk
            }

            req = requests.post(url=MEDIA_ENDPOINT_URL, data=request_data, files=files, auth=self.oauth)

            if req.status_code < 200 or req.status_code > 299:
                log.error("twitter async media upload failed")
                log.error(req.status_code)
                log.error(req.text)
                break

            segment_id = segment_id + 1
            bytes_sent = file.tell()

            log.debug('%s of %s bytes uploaded' % (str(bytes_sent), str(self.total_bytes)))
            if self.progress_callback:
                self.progress_callback(bytes_sent / self.total_bytes)

        log.debug('Upload chunks complete.')

    def upload_finalize(self):
        """Finalizes uploads and starts video processing."""
        log.debug('FINALIZE')
        request_data = {
            'command': 'FINALIZE',
            'media_id': self.media_id
        }

        req = requests.post(url=MEDIA_ENDPOINT_URL, data=request_data, auth=self.oauth)
        log.debug(req.json())

        self.processing_info = req.json().get('processing_info', None)
        if self.progress_callback:
            self.progress_callback(1.0, finalizing=True)
        self.check_status()
        if self.processing_info:
            state = self.processing_info['state']
            if state == u'succeeded':
                return True, ""
            if state == u'failed':
                return False, self.processing_info["error"]["message"]
        return True, ""



    def check_status(self):
        """Checks media processing status."""
        if self.processing_info is None:
            return True

        state = self.processing_info['state']

        log.info('Media processing status is %s ' % state)
        log.debug(self.processing_info)

        if state == u'succeeded':
            return True

        if state == u'failed':
            return False

        check_after_secs = self.processing_info['check_after_secs']

        log.debug('Checking after %s seconds' % str(check_after_secs))
        time.sleep(check_after_secs)

        log.debug('STATUS')

        request_params = {
            'command': 'STATUS',
            'media_id': self.media_id
        }

        req = requests.get(url=MEDIA_ENDPOINT_URL, params=request_params, auth=self.oauth)

        self.processing_info = req.json().get('processing_info', None)
        self.check_status()


    def run(self):
        """Run a media upload session."""
        self.upload_init()
        self.upload_append()
        return self.upload_finalize()