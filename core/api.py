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

import json
import logging
import os

import twitter

from core.base import TsubameBase

log = logging.getLogger("core.api")

api_manager = None

# paths
TWITTER_API_TOKEN_FILE= "app_token.json"

class APITokenFileInaccessible(Exception):
    def __str__(self):
        return "Can't open the API token file for Tsubame."

class APITokenFileInvalid(Exception):
    def __str__(self):
        return "The API token file for Tsubame is invalid."

class APITokenFileMissing(Exception):
    def __str__(self):
        return "The API token file is missing."

def get_api_key_from_file(file_path):
    """Get an API key from a json API key file.

    An API key file is a simple json file with a single key called "api_key" holding
    the api key.

    We use a JSON file instead of something like a unformatted plaintext file
    for possible extensibility in the future.
    """
    api_key = None
    if os.path.exists(file_path):
        try:
            with open(file_path, "rt") as f:
                api_key_json = json.load(f)

                api_key = api_key_json.get("api_key")
        except:
            log.exception("API key file parsing failed: %s", file_path)
    else:
        log.warning("API key file not found: %s", file_path)

    return api_key

def get_twitter_app_key():
    if os.path.isfile(TWITTER_API_TOKEN_FILE):
        tokens = {}
        try:
            with open(TWITTER_API_TOKEN_FILE, "rt") as token_file:
                tokens = json.load(token_file)
        except Exception:
            log.exception("Can't open API token file.")
            raise APITokenFileInaccessible
        twitter_key = tokens.get("consumer_key")
        twitter_secret = tokens.get("consumer_secret")
        token_valid = True
        # do some token validation
        if twitter_key is None:
            token_valid = False
        elif len(twitter_key) <= 0:
            token_valid = False
        if twitter_secret is None:
            token_valid = False
        elif len(twitter_secret) <= 0:
            token_valid = False

        if token_valid:
            return twitter_key, twitter_secret
        else:
            log.critical("The API token file %s is invalid.", TWITTER_API_TOKEN_FILE)
            raise APITokenFileInvalid

    else:
        log.critical("The API token file %s is missing!", TWITTER_API_TOKEN_FILE)
        raise APITokenFileMissing

def get_twitter_api_user(consumer_key, consumer_secret, access_token_key, access_token_secret):
    """A convenience function used for fetching data about a twitter account user.
    
    Can be used for example to fetch username and pre-fill an account name
    before persistently storing a newly added Twitter account.

    :param str consumer_key: consumer key
    :param str consumer_secret: consumer secret
    :param str access_token_key: access token key
    :param str access_token_secret: access token secret
    :returns: Twitter.User instance or None if account is not valid
    :rtype: Twitter.User or None
    """
    api = twitter.Api(consumer_key=consumer_key,
                      consumer_secret=consumer_secret,
                      access_token_key=access_token_key,
                      access_token_secret=access_token_secret,
                      tweet_mode="extended")
    return api.VerifyCredentials(skip_status=True, include_entities=False)


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

    def get_twitter_tokens(self, account_username):
        """Get Twitter API access tokens corresponding to the provided username.

        :param str account_username: unique Twitter username of an account that has been added to Tsubame
        """
        twitter_account = self._account_manager.twitter_accounts.get(account_username)
        if twitter_account is None:
            raise TwitterAccountForAPINotFound(account_username)

        consumer_key = self._twitter_consumer_key
        consumer_secret = self._twitter_consumer_secret
        token_key = twitter_account.token
        token_secret = twitter_account.token_secret

        return consumer_key, consumer_secret, token_key, token_secret


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
