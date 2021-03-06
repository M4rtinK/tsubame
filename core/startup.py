# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Tsubame startup handling
# * parse startup arguments
# * load device module
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
import sys
import time
import json
import os
import argparse

from enum import Enum, IntEnum

import logging
log = logging.getLogger("core.startup")

from core import tsubame_log
from core import account as account_module
from core import utils
from core import api as api_module

# error codes
class StartupErrorCodes(IntEnum):
    UNKNOWN_ERROR = 1
    API_TOKEN_FILE_MISSING = 64
    API_TOKEN_FILE_INACCESSIBLE = 65
    API_TOKEN_FILE_INVALID = 66
    TWITTER_APP_AUTHENTICATION_FAILED = 67

class Subcommand(Enum):
    ACCOUNT = "account"
    SEARCH = "search"
    LIST = "list"
    STREAM = "stream"


# Create a command string : command enum mapping, eq.:
# {"account" : Subcommand.ACCOUNT}

SUBCOMMANDS = {c.value : c.value for c in Subcommand}

class Startup(object):
    def __init__(self, tsubame):
        self.tsubame = tsubame
        self.original_stdout = None
        self.original_stderr = None
        self._subcommand_present = len(sys.argv) >= 2 and sys.argv[1] in SUBCOMMANDS
        current_subcommands = ", ".join(SUBCOMMANDS.values())
        parser = argparse.ArgumentParser(description="A flexible Twitter client.",
                                         epilog="You can also use the following subcommands: [%s] \
                                                 To see what a subcommand does use <subcommand> --help, \
                                                 EXAMPLE: account --help" % current_subcommands)
        # device
        parser.add_argument(
            '-p', "--platform", metavar="platform ID", type=str,
            help="specify platform to run on",
            default=None, action="store",
            dest="platform_id",
            choices=self.tsubame.available_platform_modules_by_id
        )

        # startup debugging - don't disable stdout
        parser.add_argument(
            '--debug-startup',
            help="startup debugging - don't disable stdout",
            default=None,
            action="store_true"
        )

        # start in fullscreen
        parser.add_argument(
            '--fullscreen',
            help="start in fullscreen",
            default=None,
            action="store_true"
        )

        # subcommands
        #
        # As argparse does not support support optional subcommands
        # (non-optional subcommands would preclude running modrana without arguments
        #  or with the current optional arguments), so only register subcommands if
        # they are spotted in sys.argv. Like this the subcommands don't show up in the
        # automatically generated help, which we workaround by mentioning the available
        # subcommands in the epilog.
        # Handling subcommands like this also has the benefit of skipping all the subcommand
        # setup code when the subcommand is not actually needed a even if a subcommand is
        # spotted only a single subcommand is setup, not all of them.

        if self._subcommand_present:
            subcommand = sys.argv[1]
            if subcommand == Subcommand.ACCOUNT.value:
                self._account_subcommand_present = True
                subcommands = parser.add_subparsers()
                account = subcommands.add_parser(Subcommand.ACCOUNT.value, help="Twitter account handling.")
                account.required = False
                account_subcommands = account.add_subparsers(dest="account_subcommand")
                # add twitter account
                account_add = account_subcommands.add_parser("add-twitter", help='add a Twitter account to Tsubame')
                account_add.add_argument(type=str, dest="twitter_username", default=None,
                                         help='Twitter username (the thing after @)')
                account_add.add_argument("--name", type=str, default=None, dest="twitter_account_name",
                                         metavar="ACCOUNT_NAME", help="optional local name of the account")
                # list
                account_list = account_subcommands.add_parser("list", help='list all Twitter twitter_accounts added to Tsubame')
                account_list.add_argument("--foo", action="store_true", dest="account_list")

                # # info
                # account_info = account_subcommands.add_parser("info", help='display Twitter account info')
                # account_info.add_argument(type=str, dest="twitter_account_id", default=None, nargs="?",
                #                          metavar="ACCOUNT_ID", help='account id to provide information about')

                # remove
                account_remove = account_subcommands.add_parser("remove", help='remove Twitter account from Tsubame')
                account_remove.add_argument(type=str, dest="twitter_account_id", default=None, nargs="?",
                                            metavar="ACCOUNT_ID",help='account id to remove')

        self.args, _unknownArgs = parser.parse_known_args()

    def handle_CLI_tasks(self):
        # account management
        if not self._subcommand_present:
            # nothing to do
            return

        if self.args.account_subcommand:
            account_manager = account_module.AccountManager(main_db=self.tsubame.db.main)
            if self.args.account_subcommand == "add-twitter":
                account_username = self.args.twitter_username
                account_name = account_username
                if self.args.twitter_account_name:
                    account_name = self.args.twitter_account_name

                # try to get the Tsubame user Tokens from Twitter
                try:
                    consumer_key, consumer_secret = self.get_twitter_app_key()
                    access_token_key, access_token_secret = utils.get_access_token_via_cli(
                        consumer_key=consumer_key, consumer_secret=consumer_secret,
                        open_url_function=self.tsubame.platform.open_url
                    )
                except ValueError:
                    print("Authentication with Twitter failed (are you online ?).")
                    exit(StartupErrorCodes.TWITTER_APP_AUTHENTICATION_FAILED)

                new_account = account_module.TwitterAccount.new(
                    db=self.tsubame.db.main,
                    username=account_username,
                    name=account_name,
                    token=access_token_key,
                    token_secret=access_token_secret
                )
                account_manager.add(account=new_account)

            elif self.args.account_subcommand == "list":
                account_count = len(account_manager.twitter_accounts)
                if account_count:
                    if account_count > 1:
                        print("%d twitter_accounts found:" % account_count)
                    else:
                        print("one account found:")
                else:
                    print("no twitter_accounts found")
                for single_account in account_manager.twitter_accounts.values():
                    print(single_account)
            elif self.args.account_subcommand == "remove":
                account_manager.remove(account_username=self.args.twitter_account_id)
            # and we should be done by now
            exit(0)



    def _enable_stdout(self):
        """enable stdout output"""
        if self.original_stdout:
            sys.stdout = self.original_stdout
            self.original_stdout = None

        if self.original_stderr:
            sys.stderr = self.original_stderr
            self.original_stderr = None

        # re-enable logging to stdout
        tsubame_log.log_manager.enable_stdout_log()

    def _disable_stdout(self):
        """disable stdout output
        -> this is mainly used for CLI processing so that Tsubame stdout logging
           doesn't get into the output that will be parsed by outside programs or scripts
        """
        # if startup debugging is enabled, don't disable stdout
        if self.args.debug_startup:
            return

        if self.original_stdout is None:
            self.original_stdout = sys.stdout
            sys.stdout = self

        if self.original_stderr is None:
            self.original_stderr = sys.stderr
            sys.stdout = self

        # also disable output to stdout from our logging infrastructure
        log.log_manager.disable_stdout_log()

    def write(self, s):
        """a write function that does nothing for stdout redirection"""
        pass

    def _exit(self, errorCode=0):
        sys.exit(errorCode)

    def get_twitter_app_key(self):
        """Get twitter app key values.

        This method is basically just a wrapper around the function from
        the api module with some startup related error reporting.
        """
        try:
            twitter_key, twitter_secret = api_module.get_twitter_app_key()
            return twitter_key, twitter_secret
        except api_module.APITokenFileInaccessible:
            exit(StartupErrorCodes.API_TOKEN_FILE_INACCESSIBLE)
        except api_module.APITokenFileInvalid:
            exit(StartupErrorCodes.API_TOKEN_FILE_INVALID)
        except api_module.APITokenFileMissing:
            exit(StartupErrorCodes.API_TOKEN_FILE_MISSING)
        except:
            exit(StartupErrorCodes.UNKNOWN_ERROR)