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

from enum import Enum

class AccountType(Enum):
    TWITTER = "twitter"

import blitzdb
from core.base import TsubameBase

account_manager = None

class TwitterAccount(blitzdb.Document):
    """A Twitter account.
    
    Expected attributes:    
    username str: unique account username
    name str: human readable account name
    token str: Twitter access token
    token_secret str: Twitter access token secret
    """

    account_type = AccountType.TWITTER

    def __str__(self):
        return "%s (%s) - a Twitter account" % (self.username, self.name)

class AccountManager(TsubameBase):
    """Service account management."""

    def __init__(self, main_db):
        super(AccountManager, self).__init__()
        self._accounts = {}
        self._main_db = main_db

        # load stored accounts (if any)
        accounts = self._main_db.filter(TwitterAccount, {})

        for account in accounts:
            self._accounts[account.username] = account

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
            account.save(self._main_db)
            self._main_db.commit()
            # add it to tracking
            self._accounts[account.username] = account
            self.log.info("account has been added: %s", account)
        except:
            self.log.exception("can't save added account %s", account.username)
            return False

    def remove(self, account_username):
        account = self._accounts.get(account_username)
        if account:
            try:
                self._main_db.delete(account)
                self._main_db.commit()
                del self._accounts[account_username]
                self.log.info("account %s has been removed", account_username)
            except Exception:
                self.log.exception("account removal failed for username: %s", account_username)
        else:
            self.log.error("can't remove unknown account username: %s", account_username)

def load_accounts(main_db):
    global account_manager
    account_manager = AccountManager(main_db=main_db)