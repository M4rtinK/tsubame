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
from core.base import TsubameBase

class TwitterAccount(blitzdb.Document):
    """A Twitter account.
    
    Expected attributes:    
    id str: unique account id
    name str: human readable account name
    token str: Twitter access token
    token_secret str: Twitter access token secret
    """

    def __str__(self):
        return "%s (%s) - a Twitter account" % (self.id, self.name)

class AccountManager(TsubameBase):
    """Service account management."""

    def __init__(self, main_db):
        super(AccountManager, self).__init__()
        self._accounts = {}
        self._main_db = main_db

        # load stored accounts (if any)
        accounts = self._main_db.filter(TwitterAccount, {})

        for account in accounts:
            self._accounts[account.id] = account

        # if self._accounts:
        #     if len(self._accounts):
        #         self.log.info("found a single account")
        #     else:
        #         self.log.info("found %d accounts", len(self._accounts))
        # else:
        #     self.log.info("no accounts found")

    @property
    def log_prefix(self):
        return "core.account.manager"

    @property
    def accounts(self):
        return self._accounts

    def add(self, account, replace=False):
        # We could just add the account to the database,
        # but we want to prevent unwanted account overwrites,
        # so we use this function and the account manager.
        if account.id in self._accounts.keys() and not replace:
            self.log.error("can't add account %s - already present")
            return False

        # add the account to the database
        try:
            # save the account
            account.save(self._main_db)
            self._main_db.commit()
            # add it to tracking
            self._accounts[account.id] = account
            self.log.info("account has been added: %s", account)
        except:
            self.log.exception("can't save added account %s", account.id)
            return False

    def remove(self, account_id):
        account = self._accounts.get(account_id)
        if account:
            try:
                self._main_db.delete(account)
                self._main_db.commit()
                del self._accounts[account_id]
                self.log.info("account %s has been removed", account_id)
            except Exception:
                self.log.exception("account removal failed for id: %s", account_id)
        else:
            self.log.error("can't remove unknown account id: %s", account_id)