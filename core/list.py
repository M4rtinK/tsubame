# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Various list operations
#
# - the current aim of this module is to host various stateless
#   list based operations
#----------------------------------------------------------------------------
# Copyright 2018, Martin Kolman
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

import logging
log = logging.getLogger("core.list")

TWITTER_LIST_MODE_PRIVATE = "private"
TWITTER_LIST_MODE_PUBLIC = "public"

def get_lists(api):
    """Get lists of the given API-user.

    :param api: Twitter API instance
    :returns: list of Twitter list instances
    """
    return api.GetLists()

def get_list_membership(api, username):
    """Get lists of which the username is member owned by the the API-user.

    :param api: Twitter API instance
    :param str username: username to lookup
    :returns: list of Twitter list instances of which the username is a member
    """
    return api.GetMemberships(screen_name=username, filter_to_owned_lists=True)

def get_users_lists(api, username):
     """Get lists of the given username.

     :param api: Twitter API instance
     :param str username: return lists owned by this username
     :returns: list of Twitter list instances
     """
     return api.GetLists(screen_name=username)

def get_user_list_membership(api, username):
    """Get list of lists the user has been added to.
    :param api: Twitter API instance
    :param str username: return lists this username is member of
    :returns: list of Twitter list instances
    """
    return api.GetMemberships(screen_name=username, count=1000)

def create_list(api, list_name, description=None, private=True):
    """Create a new list.

    Tsubame creates new lists private by default.

    :param api: Twitter API instance
    :param str list_name: name of the list
    :param description: optional description
    :type description: str or None
    :param bool private: True - create private list, False - create public list
    :returns: Twitter list instance
    """
    log.debug("creating list % (api %s)", list_name, api)
    list_mode = TWITTER_LIST_MODE_PRIVATE
    if not private:
        list_mode = TWITTER_LIST_MODE_PUBLIC
    return api.CreateList(name=list_name, description=description, mode=list_mode)

def destroy_list(api, list_owner_username, list_name):
    """Destroy a list by name.

    :param api: Twitter API instance
    :param str list_owner_username: username of the list owner
    :param str list_name: name of the list
    """
    log.debug("destroying list % owned by %s (api %s)",
              list_name, list_owner_username, api)
    api.DestroyList(owner_screen_name=list_owner_username,
                    slug=list_name)

def destroy_list_by_id(api, list_id):
    """Destroy a list by id.

    :param api: Twitter API instance
    :param str list_id: Twitter provided id of the list
    """
    log.debug("destroying list with id % (api %s)", list_id, api)
    api.DestroyList(list_id=list_id)


def add_user_to_list(api, list_owner_username, list_name, username):
    """Add a user defined by username to a list.

    :param api: Twitter API instance
    :param str list_owner_username: username of the list owner
    :param str list_name: name of the list
    :param str username: username to add to list
    """
    log.debug("adding user %s to list % owned by %s (api %s)", username, list_name, list_owner_username, api)
    return api.CreateListsMember(slug=list_name, owner_screen_name=list_owner_username,
                                 screen_name=username)

def remove_user_from_list(api, list_owner_username, list_name, username):
    """Remove user defined by username from a list.

    :param api: Twitter API instance
    :param str list_owner_username: username of the list owner
    :param str list_name: name of the list
    :param str username: username to add to list
    """
    log.debug("removing user %s from list % owned by %s (api %s)", username, list_name, list_owner_username, api_username)
    return api.CreateListsMember(slug=list_name, owner_screen_name=list_owner_username,
                                 screen_name=username)

def get_list_members(api, list_owner_username, list_name):
    """Get list members.

    :param api: Twitter API instance
    :param str list_owner_username: username of the list owner
    :param str list_name: name of the list
    :returns: list of user data objects for list members (if any)
    """
    return api.GetListMembers(owner_screen_name=list_owner_username,
                              slug=list_name)
