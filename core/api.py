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
    pass

class ApiManager(TsubameBase):
    """Provides access to remote API access points."""

    def __init__(self, account_manager, twitter_key, twitter_secret):
        super(ApiManager, self).__init__()
        self._account_manager = account_manager
        self._twitter_key = twitter_key
        self._twitter_secret = twitter_secret

        # Twitter API instances for different twitter_accounts.
        self._twitter_api_dict = {}

    def get_twitter_api(self, api_username):
        """Get Twitter API access object corresponding to the provided username.
        
        The API access objects are created on demand and cached.
        
        :param str api_username: unique Twitter username of an account that has been added to Tsubame
        """
        api = self._twitter_api_dict.get(api_username)
        if api is None:
            twitter_account = self._account_manager.twitter_accounts.get(api_username)
            if twitter_account is None:
                raise TwitterAccountForAPINotFound
            api = twitter.Api(consumer_key=self._twitter_key,
                              consumer_secret=self._twitter_secret,
                              access_token_key=twitter_account.token,
                              access_token_secret=twitter_account.token_secret)
            self._twitter_api_dict[api_username] = api
        return api



def initialize_api_manager(account_manager, twitter_key, twitter_secret):
    global api_manager
    api_manager = ApiManager(account_manager=account_manager,
                             twitter_key=twitter_key,
                             twitter_secret=twitter_secret)