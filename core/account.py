# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Tsubame account handling
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
#--------------------------------------------------------------------------

import blitzdb
from core.base import TsubameBase, TsubamePersistentBase
from core import stream as stream_module

account_manager = None


class TwitterAccountData(blitzdb.Document):
    pass


class TwitterAccount(TsubamePersistentBase):

    data_defaults = {
        "username" : None,
        "name" : None,
        "token" : None,
        "token_secret" : None
    }

    @classmethod
    def new(cls, db, username, token, token_secret, name=None):
        data = TwitterAccountData(cls.data_defaults.copy())
        data.username = username
        data.name = name
        data.token = token
        data.token_secret = token_secret
        return cls(db, data)

    @classmethod
    def from_db(cls, db, username):
        data = db.get(TwitterAccountData, {"username" : username})
        return cls(db, data)

    @property
    def username(self):
        return self.data.username

    @property
    def name(self):
        return self.data.name

    @name.setter
    def name(self, new_name):
        self.data.name = new_name

    @property
    def token(self):
        return self.data.token

    @property
    def token_secret(self):
        return self.data.token_secret

    def __str__(self):
        return "%s (%s) - a Twitter account" % (self.data.username, self.data.name)


class AccountManager(TsubameBase):
    """Service account management."""

    def __init__(self, main_db):
        super(AccountManager, self).__init__()
        self._accounts = {}
        self._main_db = main_db

        # load stored accounts (if any)
        account_data = self._main_db.filter(TwitterAccountData, {})

        for data in account_data:
            self._accounts[data.username] = TwitterAccount(main_db, data)

        # if self._accounts:
        #     if len(self._accounts):
        #         self.log.info("found a single account")
        #     else:
        #         self.log.info("found %d twitter_accounts", len(self._accounts))
        # else:
        #     self.log.info("no twitter_accounts found")

    @property
    def log_prefix(self):
        return "core.account.manager"

    @property
    def twitter_accounts(self):
        return self._accounts

    def add(self, account, replace=False):
        # We could just add the account to the database,
        # but we want to prevent unwanted account overwrites,
        # so we use this function and the account manager.
        if account.username in self._accounts.keys() and not replace:
            self.log.error("can't add account %s - already present")
            return False

        # add the account to the database
        try:
            # save the account
            account.save(commit=True)
            # add it to tracking
            self._accounts[account.username] = account
            self.log.info("account has been added: %s", account)
        except:
            self.log.exception("can't save added account %s", account)
            return False

        # add some initial default streams for the account
        # - otherwise the persistent stream list would be initially
        #   totally empty, even after adding an account and that
        #   would look bad
        stream_module.stream_manager.add_default_streams_for_account(account)

    def remove(self, account_username):
        account = self._accounts.get(account_username)
        if account:
            try:
                account.delete(commit=True)
                del self._accounts[account_username]
                self.log.info("account %s has been removed", account_username)
            except Exception:
                self.log.exception("account removal failed for username: %s", account_username)
        else:
            self.log.error("can't remove unknown account username: %s", account_username)

def load_accounts(main_db):
    global account_manager
    account_manager = AccountManager(main_db=main_db)