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
import copy

from core.signal import Signal
from core.base import TsubamePersistentBase, TsubameBase
from core import api as api_module
from core import group
from core import account as account_module
from core import cache as cache_module
from core import db as db_module

from enum import Enum
from threading import RLock

stream_manager = None

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

    data_defaults = {"enabled": True,
                     "cache_messages" : False}

    source_type = None
    root_message_source = True

    def __init__(self, db ,data):
        super(MessageSource, self).__init__(db, data)
        self._messages = []
        self._latest_message_id = None
        self.refresh_done = Signal()
        self._cache = None

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

    @property
    def cache_messages(self):
        return self.data.cache_messages

    @cache_messages.setter
    def cache_messages(self, value):
        self.data.cache_messages = value

    def _do_refresh(self):
        raise NotImplementedError

    def refresh(self):
        raise NotImplementedError


class TwitterMessageSourceData(blitzdb.Document):
    pass


class TwitterMessageSource(MessageSource):

    data_defaults = copy.deepcopy(MessageSource.data_defaults)
    data_defaults.update({"api_username" : None,
                          "tweet_cache_pk" : None})

    def __init__(self, db, data):
        super(TwitterMessageSource, self).__init__(db, data)
        self._api = api_module.api_manager.get_twitter_api(account_username=self.data.api_username)
        if self.cache_messages:  # get messages from the cache
            self._init_caching()
            self._messages = self._cache.messages
            if self._messages:
                self._latest_message_id = self._messages[-1].id

    def _init_caching(self):
        pk = self.data.tweet_cache_pk
        cache_db = db_module.db_manager.tweet_cache
        if pk:  # cache already exists
            try:
                self._cache = cache_module.TweetCache.from_db(db=cache_db, pk=self.data.tweet_cache_pk)
            except blitzdb.Document.DoesNotExist:
                self.log.info("cache folder probably cleared - creating new cache instance for %s",
                              self.__class__.__name__)
                # cache folder has probably been cleared since last time,
                # create a new clean cache instead
                self._cache = cache_module.TweetCache.new(db=cache_db)
                # save it so pk is valid
                self._cache.save(commit=True)
                # and remember its public key so we can find it next time
                self.data.tweet_cache_pk = self._cache.pk
                self.save(commit=True)
        else:  # create new cache
            self._cache = cache_module.TweetCache.new(db=cache_db)
            # save it so pk is valid
            self._cache.save(commit=True)
            # and remember its public key so we can find it next time
            self.data.tweet_cache_pk = self._cache.pk
            self.save(commit=True)

    @property
    def api(self):
        return self._api

    def refresh(self):
        # skip refresh if this source is not enabled
        if not self.enabled:
            return
        new_messages = self._do_refresh()
        if new_messages:
            new_messages.reverse()
            # The python-twitter library returns messages as newest -> oldest,
            # which is problematic for caching, so revert the order.
            # Like this we can just use extend() when caching & the
            # index of a message should not change as long as the message
            # list is not flushed.
            self._latest_message_id = new_messages[-1].id
            self._messages.append(new_messages)
        if self.cache_messages:
            if not self._cache:
                self._init_caching()
            self._cache.add_messages(new_messages)
            self._cache.save(commit=True)
        self.refresh_done()
        return new_messages


class OwnTwitterTimelineData(blitzdb.Document):
    pass


class OwnTwitterTimeline(TwitterMessageSource):
    """Own Twitter timeline."""
    source_type = SourceTypes.TWITTER_TIMELINE
    data_defaults = copy.deepcopy(TwitterMessageSource.data_defaults)

    @classmethod
    def new(cls, db, api_username):
        data = OwnTwitterTimelineData(copy.deepcopy(cls.data_defaults))
        data.api_username = api_username
        return cls(db, data)

    def _do_refresh(self):
        # Either just get messages from the timeline or get new messages
        # since the timeline was last refreshed.
        # NOTE: This has a pretty low rate limit - 15 requests per 15 minute window,
        #       so local persistent caching should be used where possible.
        return self.api.GetHomeTimeline(since_id=self.latest_message_id,
                                        count=200)


class OwnTwitterMentionsData(blitzdb.Document):
    pass


class OwnTwitterMentions(TwitterMessageSource):
    """Own Twitter mentions."""
    source_type = SourceTypes.TWITTER_TIMELINE
    data_defaults = copy.deepcopy(TwitterMessageSource.data_defaults)

    @classmethod
    def new(cls, db, api_username):
        data = OwnTwitterMentionsData(copy.deepcopy(cls.data_defaults))
        data.api_username = api_username
        return cls(db, data)

    def _do_refresh(self):
        # Either just get messages from the timeline or get new messages
        # since the timeline was last refreshed.
        return self.api.GetMentions(since_id=self.latest_message_id,
                                    count=200)


class OwnTwitterFavouritesData(blitzdb.Document):
    pass


class OwnTwitterFavourites(TwitterMessageSource):
    """Stream of our own favorite messages."""
    source_type = SourceTypes.TWITTER_FAVOURITES
    data_defaults = copy.deepcopy(TwitterMessageSource.data_defaults)

    @classmethod
    def new(cls, db, api_username):
        data = OwnTwitterFavouritesData(copy.deepcopy(cls.data_defaults))
        data.api_username = api_username
        return cls(db, data)

    def _do_refresh(self):
        return self.api.GetFavorites(since_id=self.latest_message_id,
                                     count=200)


class TwitterUserTweetsData(blitzdb.Document):
    pass


class TwitterUserTweets(TwitterMessageSource):
    """Tweets of a Twitter user."""
    source_type = SourceTypes.TWITTER_USER_TWEETS

    data_defaults = copy.deepcopy(TwitterMessageSource.data_defaults)
    data_defaults.update({"source_username": None})

    @classmethod
    def new(cls, db, api_username, source_username):
        data = TwitterUserTweetsData(copy.deepcopy(cls.data_defaults))
        data.api_username = api_username
        data.source_username = source_username
        return cls(db, data)

    @property
    def source_username(self):
        return self.data.source_username

    def _do_refresh(self):
        return self.api.GetUserTimeline(screen_name=self.source_username, since_id=self.latest_message_id)


class TwitterUserFavouritesData(blitzdb.Document):
    pass


class TwitterUserFavourites(TwitterMessageSource):
    """Favourites of a Twitter user."""
    source_type = SourceTypes.TWITTER_USER_FAVOURITES

    data_defaults = copy.deepcopy(TwitterMessageSource.data_defaults)
    data_defaults.update({"source_username": None})

    @classmethod
    def new(cls, db, api_username, source_username):
        data = TwitterUserFavouritesData(copy.deepcopy(cls.data_defaults))
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

    data_defaults = copy.deepcopy(TwitterMessageSource.data_defaults)
    data_defaults.update({"remote_list_id": None})

    @classmethod
    def new(cls, db, api_username, remote_list_id):
        data = TwitterUserTweetsData(copy.deepcopy(cls.data_defaults))
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
        "input_group" : None,
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

        data = MessageStreamData(copy.deepcopy(cls.data_defaults))
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
        self._input_group = None
        self._filter_group = None

        if self.data.input_group:
            self._input_group = InputGroup(self.db, self.data.input_group)
        else:  # create a new input group
            self._input_group = InputGroup.new(self.db)
            self.data.input_group = self._input_group.data

        if self.data.filter_group:
            self._filter_group = group.FilterGroup(self.db, self.data.filter_group)
        else:  # create a new filter group
            self._filter_group = group.FilterGroup.new(self.db)
            self.data.filter_group = self._filter_group.data

        # get initial messages
        initial_messages = self.inputs.messages

        self._messages = self.filters.filter_messages(initial_messages)

        self.refresh_done = Signal()

    @property
    def name(self):
        return self.data.name

    @property
    def messages(self):
        return self._messages

    @property
    def inputs(self):
        return self._input_group

    @property
    def filters(self):
        return self._filter_group

    def refresh(self):
        new_messages = self._do_refresh()
        if new_messages:
            self._messages.extend(new_messages)
        self.refresh_done()
        return new_messages

    def _do_refresh(self):
        # get new messages
        new_messages = self.inputs.refresh()
        # let's try to sort the messages
        # - this might or might not work as expected :)
        # UPDATE: does not work (at least for Twitter messages) :D
        #new_messages.sort()
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
        self._streams_loaded = False
        self._stream_list = []
        self._stream_dict = {}

        #self._clear_streams()

    def _clear_streams(self):
        """Useful for debugging"""
        self.log.debug("Deleting everything!!")
        for data in self.data.stream_list:
            self.db.delete(data)
        self.data.stream_list = []
        self.db.commit()
        return

    def _load_streams(self):
        if self.data.stream_list:
            for stream_data in self.data.stream_list:
                stream = MessageStream(self.db, stream_data)
                self._stream_list.append(stream)
                self._stream_dict[stream.name] = stream
        self._streams_loaded = True

    @property
    def stream_list(self):
        with self._lock:
            if not self._streams_loaded:  # not yet loaded
                self._load_streams()
            return self._stream_list

    @property
    def stream_dict(self):
        with self._lock:
            if not self._streams_loaded:  # not yet loaded
                self._load_streams()
            return self._stream_dict

    def append_stream(self, stream):
        with self._lock:
            if not self._streams_loaded:  # not yet loaded
                self._load_streams()
            self._stream_list.append(stream)
            self.data.stream_list.append(stream.data)
            self.stream_dict[stream.name] = stream

    def delete_stream(self, stream_name):
        with self._lock:
            if not self._streams_loaded:  # not yet loaded
                self._load_streams()
            stream = self.stream_dict.get(stream_name, None)
            if stream:  # remove stream from tracking & database
                self._stream_list.remove(stream)
                self.data.stream_list.remove(stream.data)
                stream.data.delete()
                self.save(commit=True)
                self.db.commit()
                # This is actually pretty brutal & messy as we basically
                # leave a lof of garbage in the database in the form of
                # unreferenced sources, filters and caches used by the deleted
                # stream. We really should do this properly eventually.
                #
                # We should also have unit tests for this to make sure the
                # stream deletion actually works correctly.
                return True
            else:
                self.log.error("can't delete stream - stream name unknown: %s", stream_name)
                return False

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

            for account in account_module.account_manager.twitter_accounts.values():
                self.log.info("adding initial streams for account: %s", account)
                # add the timeline stream
                timeline_name = "%s timeline" % account.username
                timeline_description = "Twitter timeline stream for %s." % account.username
                timeline = MessageStream.new(db=self.db,
                                             name=timeline_name,
                                             description=timeline_description)
                # Using own timeline really needs caching (at least for development)
                # due to the 15 requests/15 minutes rate limit.
                timeline_source = OwnTwitterTimeline.new(db=self.db,
                                                        api_username=account.username)
                # named streams should have stream caching by default
                timeline_source.cache_messages = True
                timeline.inputs.add(timeline_source)
                self.append_stream(timeline)

                # add the mentions stream
                mentions_name = "%s mentions" % account.username
                mentions_description = "Twitter mentions stream for %s." % account.username
                mentions = MessageStream.new(db=self.db,
                                             name=mentions_name,
                                             description=mentions_description)
                mentions_source = OwnTwitterMentions.new(db=self.db,
                                                         api_username=account.username)
                # named streams should have stream caching by default
                mentions_source.cache_messages = True
                mentions.inputs.add(mentions_source)
                self.append_stream(mentions)

                # add the favourites stream
                favourites_name = "%s favourites" % account.username
                favourites_description = "Twitter favourites stream for %s." % account.username
                favourites = MessageStream.new(db=self.db,
                                             name=favourites_name,
                                             description=favourites_description)
                favourites_source = OwnTwitterFavourites.new(db=self.db,
                                                         api_username=account.username)
                # named streams should have stream caching by default
                favourites_source.cache_messages = True
                favourites.inputs.add(favourites_source)
                self.append_stream(favourites)

                # call a refresh on the streams so that they have some content
                timeline.refresh()
                mentions.refresh()
                favourites.refresh()

                # save the streams
                timeline.save(commit=True)
                mentions.save(commit=True)
                favourites.save(commit=True)

                # save own state
                self.save(commit=True)


class InputGroupData(blitzdb.Document):
    pass


class InputGroup(group.Group):

    data_defaults = copy.deepcopy(group.Group.data_defaults)

    @classmethod
    def new(cls, db):
        data = InputGroupData(copy.deepcopy(cls.data_defaults))
        return cls(db, data)

    def __init__(self, db, data):
        super(InputGroup, self).__init__(db, data)
        with self._group_lock:
            self._load_members()

    def _load_members(self):
        for item_data in self.data.members:
            # Fetch the functional input class based
            # based on data class.
            cls = CLASS_MAP.get(item_data.__class__)
            if cls is None:
                self.log.error("Source class class not found for data: %s", item_data)
            else:
                self._members.append(cls(self.db, item_data))

    @property
    def messages(self):
        """Get a combined list of all messages from the sources.
        
        TODO: time/message id based sorting ?
        """
        message_list = []
        for member in self.members:
            message_list.extend(member.messages)
        return message_list

    def refresh(self):
        """Refresh all sources and return list of all new messages."""
        new_messages = []
        for source in self.members:
            new_messages.extend(source.refresh())
        return new_messages


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

def initialize_stream_manager(db):
    global stream_manager
    stream_manager = StreamManager.get_from_db(db)
