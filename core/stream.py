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

import blitzdb

from core.signal import Signal
from core.base import TsubamePersistentBase, TsubameBase
from core import api as api_module
from core import group
from core import account as account_module

from enum import Enum
from threading import RLock

class SourceTypes(Enum):
    TWITTER_TIMELINE = "source-twitter-timeline"
    TWITTER_MENTIONS = "source-twitter-mentions"
    TWITTER_FAVOURITES = "source-twitter-favourites"
    TWITTER_USER_TWEETS = "source-twitter-user-tweets"
    TWITTER_USER_FAVOURITES = "source-twitter-user-favourites"
    TWITTER_REMOTE_LIST = "source-twitter-remote-list"
    TWITTER_LOCAL_LIST = "source-twitter-local-list"


class MessageStreamNameAlreadyExists(Exception):
    pass


class MessageSource(TsubamePersistentBase):
    """A "root" message source used by message
    streams so that they actually have something to stream. :)
    """

    data_defaults = {"enabled": True}

    source_type = None
    root_message_source = True

    def __init__(self, db ,data):
        super(MessageSource, self).__init__(db, data)
        self._messages = []
        self._latest_message_id = None
        self.refresh_done = Signal()

    @property
    def messages(self):
        return self._messages

    @property
    def latest_message_id(self):
        return self._latest_message_id

    @property
    def enabled(self):
        return self.data.enabled

    @enabled.setter
    def enabled(self, new_state):
        self.data.enabled = new_state

    def _do_refresh(self):
        raise NotImplementedError

    def refresh(self):
        raise NotImplementedError


class TwitterMessageSourceData(blitzdb.Document):
    pass


class TwitterMessageSource(MessageSource):

    data_defaults = MessageSource.data_defaults.copy()
    data_defaults.update({"api_username" : None})

    def __init__(self, db, data):
        super(TwitterMessageSource, self).__init__(db, data)
        self._api = api_module.api_manager.get_twiter_api(account_username=self.data.api_username)

    @property
    def api(self):
        return self._api

    def refresh(self):
        # skip refresh if this source is not enabled
        if not self.enabled:
            return
        self._do_refresh()
        new_messages = self._do_refresh()
        if new_messages:
            self._latest_message_id = new_messages[-1].id
            self._messages.append(new_messages)
        self.refresh_done()
        return new_messages


class OwnTwitterTimelineData(blitzdb.Document):
    pass


class OwnTwitterTimeline(TwitterMessageSource):
    """Own Twitter timeline."""
    source_type = SourceTypes.TWITTER_TIMELINE

    @classmethod
    def new(cls, db, api_username):
        data = OwnTwitterTimelineData(cls.data_defaults.copy())
        data.api_username = api_username
        return cls(db, data)

    def _do_refresh(self):
        # Either just get messages from the timeline or get new messages
        # since the timeline was last refreshed.
        return self.api.GetHomeTimeline(since_id=self.latest_message_id)


class OwnTwitterMentionsData(blitzdb.Document):
    pass


class OwnTwitterMentions(TwitterMessageSource):
    """Own Twitter mentions."""
    source_type = SourceTypes.TWITTER_TIMELINE

    @classmethod
    def new(cls, db, api_username):
        data = OwnTwitterMentionsData(cls.data_defaults.copy())
        data.api_username = api_username
        return cls(db, data)

    def _do_refresh(self):
        # Either just get messages from the timeline or get new messages
        # since the timeline was last refreshed.
        return self.api.GetMentions(since_id=self.latest_message_id)


class OwnTwitterFavouritesData(blitzdb.Document):
    pass


class OwnTwitterFavourites(TwitterMessageSource):
    """Stream of our own favorite messages."""
    source_type = SourceTypes.TWITTER_FAVOURITES

    @classmethod
    def new(cls, db, api_username):
        data = OwnTwitterFavouritesData(cls.data_defaults.copy())
        data.api_username = api_username
        return cls(db, data)

    def _do_refresh(self):
        return self.api.GetFavorites(since_id=self.latest_message_id)


class TwitterUserTweetsData(blitzdb.Document):
    pass


class TwitterUserTweets(TwitterMessageSource):
    """Tweets of a Twitter user."""
    source_type = SourceTypes.TWITTER_USER_TWEETS

    data_defaults = TwitterMessageSource.data_defaults.copy()
    data_defaults.update({"source_username": None})

    @classmethod
    def new(cls, db, api_username, source_username):
        data = TwitterUserTweetsData(cls.data_defaults.copy())
        data.api_username = api_username
        data.source_username = source_username
        return cls(db, data)

    @property
    def source_username(self):
        return self.data.source_username

    def _do_refresh(self):
        return self.api.GetUserTimeline(user_id=self.source_username, since_id=self.latest_message_id)


class TwitterUserFavouritesData(blitzdb.Document):
    pass


class TwitterUserFavourites(TwitterMessageSource):
    """Favourites of a Twitter user."""
    source_type = SourceTypes.TWITTER_USER_FAVOURITES

    data_defaults = TwitterMessageSource.data_defaults.copy()
    data_defaults.update({"source_username": None})

    @classmethod
    def new(cls, db, api_username, source_username):
        data = TwitterUserFavouritesData(cls.data_defaults.copy())
        data.api_username = api_username
        data.source_username = source_username
        return cls(db, data)

    @property
    def source_username(self):
        return self.data.source_username

    def _do_refresh(self):
        return self.api.GetFavorites(user_id=self.source_username, since_id=self.latest_message_id)


class TwitterRemoteListData(blitzdb.Document):
    pass


class TwitterRemoteList(TwitterMessageSource):
    source_type = SourceTypes.TWITTER_REMOTE_LIST

    data_defaults = TwitterMessageSource.data_defaults.copy()
    data_defaults.update({"remote_list_id": None})

    @classmethod
    def new(cls, db, api_username, remote_list_id):
        data = TwitterUserTweetsData(cls.data_defaults.copy())
        data.api_username = api_username
        data.remote_list_id = remote_list_id
        return cls(db, data)

    @property
    def remote_list_id(self):
        return self.data.remote_list_id

    def _do_refresh(self):
        return self.api.GetListTimeline(list_id=self.remote_list_id)


class TwitterLocalListData(blitzdb.Document):
    pass


class TwitterLocalList(TwitterMessageSource):
    source_type = SourceTypes.TWITTER_REMOTE_LIST

    # TODO: fetch tweets from all users in a local list
    #
    # I guess there could be rate limiting issues
    # if we query tweets from many users at once


class MessageStreamData(blitzdb.Document):
    pass


class MessageStream(TsubamePersistentBase):
    root_message_source = False

    data_defaults = {
        "name" : "",
        "description" : "",
        "inputs" : [],
        "filter_group" : None
    }

    @classmethod
    def new(cls, db, name, description=""):
        # first check if a stream with this name already exists
        try:
            if db.get(MessageStreamData, {"name" : name}):
                # A message stream with this name already exists,
                # raise an exception.
                raise MessageStreamNameAlreadyExists()
        except blitzdb.Document.DoesNotExist:
            # Nothing found, we can create a new stream with this name.
            pass

        data = MessageStreamData(cls.data_defaults.copy())
        data.name = name
        data.description = description
        return cls(db, data)

    @classmethod
    def from_db(cls, db, stream_name):
        data = db.get(MessageStreamData, {"name" : stream_name})
        return cls(db, data)

    def __init__(self, db, data):
        super(MessageStream, self).__init__(db, data)
        self._messages = []
        self._inputs = None
        self._filter_group = None
        self.refresh_done = Signal()

    @property
    def inputs(self):
        if self._inputs is None:
            self._inputs = []
            # lazy initialization
            for input_data in self.data.inputs:
                # get the input source class corresponding to the data class
                # that has been serialized to the database
                cls = CLASS_MAP.get(input_data.__class__)
                if cls:
                    # instantiate the input source class and add it to the
                    # list of input sources
                    self._inputs.append(cls(self.db, input_data))
                else:
                    self.log.error("Input source class not found for data: %s",
                                   input_data)
        return self._inputs

    @property
    def filters(self):
        if self._filter_group is None:
            # first look if we have something in data
            if self.data.filter_group:
                self._filter_group = group.FilterGroup(self.db, self.data.filter_group)
            else:  # create a new filter group
                self._filter_group = group.FilterGroup.new(self.db)
                self.data.filter_group = self._filter_group.data
        return self._filter_group

    def refresh(self):
        self._do_refresh()
        new_messages = self._do_refresh()
        if new_messages:
            self._messages.extend(new_messages)
        self.refresh_done()
        return new_messages

    def _do_refresh(self):
        new_messages = []
        # get new messages
        for source in self._inputs:
            new_messages.extend(source.refresh())
        # let's try to sort the messages
        # - this might or might not work as expected :)
        new_messages.sort()
        # filter the new messages
        new_messages = self.filters.filter_messages(new_messages)
        # return the result
        return new_messages


class StreamManagerData(blitzdb.Document):
    pass


class StreamManager(TsubamePersistentBase):
    data_defaults = {
        "stream_list" : []
    }

    @classmethod
    def get_from_db(cls, db):
        # There should always be only one instance of this class
        # and its data class so we can as well
        # create the initial instance here.
        try:
            data = db.get(StreamManagerData, {})
        except blitzdb.Document.DoesNotExist:
            data = StreamManagerData()
        return cls(db, data)

    def __init__(self, db, data):
        super(StreamManager, self).__init__(db, data)
        self._lock = RLock()
        self._stream_list = None

    @property
    def stream_list(self):
        with self._lock:
            if self._stream_list is None:  # not yet initialized
                self._stream_list = []
                if self.data.stream_list:
                    for stream_data in self.data.stream_list:
                        self._stream_list.append(MessageStream(self.db, stream_data))
            return self._stream_list

    def append_stream(self, stream):
        with self._lock:
            self._stream_list.append(stream)
            self.data.stream_list.append(stream.data)

    def add_initial_streams(self):
        """Add some initial "default" streams.
        
        Generally used to pre-fill the stream list on first application run.
        """
        with self._lock:
            if account_module.account_manager.twitter_accounts:
                self.log.info("adding initial Twitter account streams streams.")
            else:
                self.log.info("not adding initial Twitter account streams streams"
                              " - no Twitter accounts have been added to Tsubame")

            for account in account_module.account_manager.twitter_accounts:
                self.log.info("adding initial streams for account: %s", account)
                # add the timeline stream
                timeline_name = "%s timeline" % account.username
                timeline_description = "Twitter timeline stream for %s." % account.username
                timeline = MessageStream.new(db=self.db,
                                             name=timeline_name,
                                             description=timeline_description)
                timeline_source = OwnTwitterTimeline.new(db=self.db,
                                                         api_username=account.username)
                timeline.inputs.append(timeline_source)
                self.append_stream(timeline)

                # add the mentions stream
                mentions_name = "%s mentions" % account.username
                mentions_description = "Twitter mentions stream for %s." % account.username
                mentions = MessageStream.new(db=self.db,
                                             name=mentions_name,
                                             description=mentions_description)
                mentions_source = OwnTwitterMentions.new(db=self.db,
                                                         api_username=account.username)
                mentions.inputs.append(mentions_source)
                self.append_stream(mentions)


# mapping of data classes to functional classes
CLASS_MAP = {
    OwnTwitterTimelineData : OwnTwitterTimeline,
    OwnTwitterFavouritesData : OwnTwitterFavourites,
    OwnTwitterMentionsData : OwnTwitterMentions,
    TwitterUserTweetsData : TwitterUserTweets,
    TwitterUserFavouritesData : TwitterUserFavourites,
    TwitterRemoteListData : TwitterRemoteList,
    TwitterLocalListData : TwitterLocalList
}

