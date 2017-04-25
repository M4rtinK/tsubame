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

import os
import glob

from core.base import TsubameBase

class Account(TsubameBase):
    """A generic account base class."""

    def __init__(self, id, name):
        super(Account, self).__init__()
        self._id = id
        self._name = name

    @property
    def log_prefix(self):
        return "core.account"

    @property
    def id(self):
        """Unique account id.
        
        :returns: unique account id
        :rtype: str
        """
        return self._id

    @property
    def name(self):
        """User specified account name.
        
        :returns: user specified account name
        :rtype: str
        """
        return self._name


    def to_dict(self):
        """Return dictionary representing state of the Account instance."""
        d = super(Account, self).to_dict()
        d["id"] = self.id
        d["name"] = self.name
        return d

class TwitterAccount(Account):
    """A Twitter account."""

    @classmethod
    def from_dict(cls, dictionary):
        #TODO: validate the dict first
        return cls(id=dictionary["id"],
                   name=dictionary["name"],
                   token=dictionary["token"],
                   token_secret=dictionary["token_secret"]
                   )

    def __init__(self, id, name, token, token_secret):
        super(TwitterAccount, self).__init__(id, name)
        self._token = token
        self._token_secret = token_secret

    def __repr__(self):
        return "%s (%s) - a Twitter account" % (self.id, self.name)

    @property
    def log_prefix(self):
        return "core.account.twitter"

    @property
    def token(self):
        """Twitter account access token.
        
        :returns: Twitter account access token
        :rtype: str
        """
        return self._token

    @property
    def token_secret(self):
        """Twitter account access token secret.
        
        :returns: Twitter account access token secret
        :rtype: str
        """
        return self._token_secret

    def to_dict(self):
        """Return dictionary representing state of the TwitterAccount instance."""
        d = super(TwitterAccount, self).to_dict()
        d["token"] = self.token
        d["token_secret"] = self.token_secret
        return d

class AccountManager(TsubameBase):
    """Service account management."""

    def __init__(self, accounts_folder):
        super(AccountManager, self).__init__()
        self._accounts = {}
        self._accounts_folder = accounts_folder

        # load stored accounts (if any)
        if os.path.isdir(accounts_folder):
            accounts_glob = os.path.join(accounts_folder, "*.json")
            account_files = glob.glob(accounts_glob)
            for file_path in account_files:
                try:
                    account = TwitterAccount.from_json_file(file_path)
                    self._accounts[account.id] = account
                except Exception:
                    self.log.exception("account file loading failed for: %s", file_path)

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
        if account.id in self._accounts.keys() and not replace:
            self.log.error("can't add account %s - already present")
            return False

        # set storage path
        account_file_path = os.path.join(self._accounts_folder, account.id + ".json")
        account.json_file_path = account_file_path
        try:
            # save the account
            account.save()
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
                os.remove(account.json_file_path)
                del self._accounts[account_id]
                self.log.info("account %s has been removed", account_id)
            except Exception:
                self.log.exception("account removal failed for id: %s", account_id)
        else:
            self.log.error("can't remove unknown account id: %s", account_id)