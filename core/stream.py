#!/usr/bin/python3
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Message streams.
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
from core.signal import Signal
from core.base import TsubamePersistentBase, TsubameBase

from enum import Enum

class SourceTypes(Enum):
    TWITTER_TIMELINE = "source-twitter-timeline"
    TWITTER_FAVOURITES = "source-twitter-favourites"
    TWITTER_USER_TWEETS = "source-twitter-user-tweets"
    TWITTER_USER_FAVOURITES = "source-twitter-user-favourites"
    TWITTER_REMOTE_LIST = "source-twitter-remote-list"
    TWITTER_LOCAL_LIST = "source-twitter-local-list"

class MessageSource(TsubameBase):
    """A "root" message source used by message
    streams so that they actually have something to stream. :)
    """

    source_type = None
    root_message_source = True

    def __init__(self):
        super(MessageSource, self).__init__()
        self._messages = []
        self._latest_message_id = None
        self.refresh_done = Signal()

    @property
    def messages(self):
        return self._messages

    @property
    def latest_message_id(self):
        return self._latest_message_id

    def _do_refresh(self):
        raise NotImplementedError

    def refresh(self):
        raise NotImplementedError


class TwitterMessageSource(MessageSource):
    def __init__(self, api):
        super(TwitterMessageSource, self).__init__()
        self._api = api

    @property
    def api(self):
        return self._api

    def refresh(self):
        self._do_refresh()
        new_messages = self._do_refresh()
        if new_messages:
            self._latest_message_id = new_messages[-1].id
            self._messages.append(new_messages)
        self.refresh_done()


class OwnTwitterTimeline(TwitterMessageSource):
    """Own twitter timeline."""
    source_type = SourceTypes.TWITTER_TIMELINE

    def _do_refresh(self):
        # Either just get messages from the timeline or get new messages
        # since the timeline was last refreshed.
        return self.api.GetHomeTimeline(since_id=self.latest_message_id)

class OwnTwitterFavourites(TwitterMessageSource):
    """Stream of our own favorite messages."""
    source_type = SourceTypes.TWITTER_FAVOURITES

    def _do_refresh(self):
        return self.api.GetFavorites(since_id=self.latest_message_id)


class TwitterUserTweets(TwitterMessageSource):
    """Tweets of a Twitter user."""
    source_type = SourceTypes.TWITTER_USER_TWEETS

    def __init__(self, api, user_id):
        super(TwitterUserTweets, self).__init__(api)
        self._user_id = user_id

    def _do_refresh(self):
        return self.api.GetUserTimeline(user_id=self._user_id, since_id=self.latest_message_id)


class TwitterUserFavourites(TwitterMessageSource):
    """Favourites of a Twitter user."""
    source_type = SourceTypes.TWITTER_USER_FAVOURITES


    def __init__(self, api, user_id):
        super(TwitterUserFavourites, self).__init__(api)
        self._user_id = user_id

    def _do_refresh(self):
        return self.api.GetFavorites(user_id=self._user_id, since_id=self.latest_message_id)


class TwitterRemoteList(TwitterMessageSource):
    source_type = SourceTypes.TWITTER_REMOTE_LIST

    def __init__(self, api, remote_list):
        super(TwitterRemoteList, self).__init__(api)
        self._remote_list = remote_list

    def _do_refresh(self):
        return self.api.GetListTimeline(list_id=self._remote_list.list_id)


class TwitterLocalList(TwitterMessageSource):
    source_type = SourceTypes.TWITTER_REMOTE_LIST

    # I guess there could be rate limiting issues
    # if we query tweets from many users at once


class MessageStream(TsubamePersistentBase):
    root_message_source = False

    data_defaults = {
        "name" : "",
        "description" : "",
        "inputs" : [],
        "filter_group" : None
    }

    def __init__(self, db, data, api):
        super(MessageStream, self).__init__(db, data)
        self._api = api
        self._messages = []
        self._inputs = []
        self._filter_group = None
        self._latest_message_id = None
        self.refresh_done = Signal()

    def refresh(self):
        self._do_refresh()
        new_messages = self._do_refresh()
        if new_messages:
            self._latest_message_id = new_messages[-1].id
            self._messages.append(new_messages)
        self.refresh_done()

    def _do_refresh(self):
        raise NotImplementedError

    @property
    def latest_message_id(self):
        return self._latest_message_id
