#!/usr/bin/python3
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Remote service API management.
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

import twitter

from core import account
from core.base import TsubameBase

api_manager = None

class TwitterAccountForAPINotFound(Exception):
    def __init__(self, account_username):
        self._account_username = account_username

    def __str__(self):
        return "no API found for account username: %s" % self._account_username

class ApiManager(TsubameBase):
    """Provides access to remote API access points."""

    def __init__(self, account_manager, twitter_consumer_key, twitter_consumer_secret):
        super(ApiManager, self).__init__()
        self._account_manager = account_manager
        self._twitter_consumer_key = twitter_consumer_key
        self._twitter_consumer_secret = twitter_consumer_secret

        # Twitter API instances for different twitter_accounts.
        self._twitter_api_dict = {}

    @property
    def twitter_consumer_key(self):
        return self._twitter_consumer_key

    @property
    def twitter_consumer_secret(self):
        return self._twitter_consumer_secret

    def get_twitter_api(self, account_username):
        """Get Twitter API access object corresponding to the provided username.
        
        The API access objects are created on demand and cached.
        
        :param str account_username: unique Twitter username of an account that has been added to Tsubame
        """
        api = self._twitter_api_dict.get(account_username)
        if api is None:
            twitter_account = self._account_manager.twitter_accounts.get(account_username)
            if twitter_account is None:
                raise TwitterAccountForAPINotFound(account_username)
            api = twitter.Api(consumer_key=self._twitter_consumer_key,
                              consumer_secret=self._twitter_consumer_secret,
                              access_token_key=twitter_account.token,
                              access_token_secret=twitter_account.token_secret,
                              tweet_mode="extended")
            self._twitter_api_dict[account_username] = api
        return api

    def get_an_api_username(self):
        """Get an arbitrary Twitter API username.

        This is generally used to get an API for retrieving data for temporary message streams.

        Eventually we most likely either want to make:
        - track message API source per message
        - make default account for temporary streams configurable
        """
        if self._twitter_api_dict:
            return list(self._twitter_api_dict.keys()).pop()
        else:
            return TwitterAccountForAPINotFound

def initialize_api_manager(account_manager, twitter_consumer_key, twitter_consumer_secret):
    global api_manager
    api_manager = ApiManager(account_manager=account_manager,
                             twitter_consumer_key=twitter_consumer_key,
                             twitter_consumer_secret=twitter_consumer_secret)
