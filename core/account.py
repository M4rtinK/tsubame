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

from core.base import TsubameBase

class Account(TsubameBase):
    """A generic account base class."""

    def __init__(self, identifier, name):
        super(Account, self).__init__()
        self._identifier = identifier
        self._name = name

    @property
    def identifier(self):
        """Unique account identifier.
        
        :returns: unique account identifier
        :rtype: str
        """
        return self._identifier

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
        d["identifier"] = self.identifier
        d["name"] = self.name
        return d

class TwitterAccount(Account):
    """A Twitter account."""

    @classmethod
    def from_dict(cls, dictionary):
        #TODO: validate the dict first
        return cls(identifier=dictionary["identifier"],
                   name=dictionary["name"],
                   token=dictionary["token"],
                   token_secret=dictionary["token_secret"]
                   )

    def __init__(self, identifier, name, token, token_secret):
        super(TwitterAccount, self).__init__(identifier, name)
        self._token = token
        self._token_secret = token_secret

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