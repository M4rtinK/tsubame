#----------------------------------------------------------------------------
# Library functions for Tsubame Qt 5 QtQuick 2.0 GUI module
#----------------------------------------------------------------------------
# Copyright 2019, Martin Kolman
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
#---------------------------------------------------------------------------

import re

from core import constants

REMOVE_HTML_RE = re.compile(r'<[^<]+?>')

def process_twitter_message_text(full_text, message_dict):
    """Process a Twitter message text.

    We have a separate method for this as we might need to process both "regular" messages,
    retweets and quoted messages.

    :param str full_text: full text of the message as returned by the Twitter API vy python-twitter
    :param dict message_dict: message data in dict form
    :return: processed message full text
    :rtype: str
    """

    # make normal URLs clickable
    for url in message_dict.get("urls", []):
        short_url = url["url"]
        link = '<a href="%s">%s</a>' % (url["expanded_url"], url["expanded_url"])
        full_text = full_text.replace(short_url, link)

    # drop media URLs as we show a per-media detail page
    for medium in message_dict.get("media", []):
        full_text = full_text.replace(medium["url"], "").rstrip()

    # make hashtags clickable
    # - we cant really do this with regexps on the QML side as the Javascript regexps
    #   can't really handle non latin characters such as Japanese
    # - if this even turns into a bottleneck we can likely move these substitutions
    #   to the delegate on the QML side
    for hashtag in message_dict.get("hashtags", []):
        hashtag_string = hashtag["text"]
        link = '<a href="#%s">#%s</a>' % (hashtag_string, hashtag_string)
        full_text = full_text.replace("#" + hashtag_string, link)

    # drop hyperlinks from the full tweet text & append it
    full_text_plaintext= REMOVE_HTML_RE.sub("", full_text)

     # QML needs <br> in place of \n and ignores any \n it finds, so we need to adjust the
    # full message text accordingly. At least we can avoid doing that twice for the
    # plaintext version as well.
    full_text = full_text.replace("\n", "<br>")

    return full_text, full_text_plaintext

def process_twitter_message(message, active_message_id=None):
    """Turn the twitter message to dict and apply any Tsubame related tweaks."""
    message_dict = message.AsDict()
    matches_active_id = active_message_id and message_dict.get("id_str") == active_message_id

    is_retweet = False
    is_quote = False
    nested_user = None
    # check if this is a simple retweet (without added content)
    retweeted_status = message_dict.get("retweeted_status")
    quoted_status = message_dict.get("quoted_status")
    if retweeted_status:
        is_retweet = True
        # in this case we don't need to care about the retweet full text (it's likely truncated anyway)
        # but instead just process the text from the original tweet
        full_text, full_text_plaintext = process_twitter_message_text(retweeted_status["full_text"], message_dict)
        message_dict["retweeted_status"]["tsubame_message_created_at_epoch"] = message.retweeted_status.created_at_in_seconds
        message_dict["retweeted_status"]["tsubame_message_source_plaintext"] = REMOVE_HTML_RE.sub("", message.retweeted_status.source)
        # record the user who did the retweet
        message_dict["tsubame_retweet_user"] = message_dict["user"]
        # set the original user as the top level user
        message_dict["user"] = message_dict["retweeted_status"]["user"]
    else:
        full_text, full_text_plaintext = process_twitter_message_text(message_dict["full_text"], message_dict)
        if quoted_status:
            is_quote = True
            # also process the text for the quoted status
            quoted_full_text, quoted_full_text_plaintext = process_twitter_message_text(quoted_status["full_text"], message_dict)
            message_dict["quoted_status"]["full_text"] = quoted_full_text
            message_dict["quoted_status"]["tsubame_full_text_plaintext"] = quoted_full_text_plaintext
            message_dict["quoted_status"]["tsubame_message_created_at_epoch"] = message.quoted_status.created_at_in_seconds
            message_dict["quoted_status"]["tsubame_message_source_plaintext"] = REMOVE_HTML_RE.sub("", message.quoted_status.source)
            message_dict["quoted_status"]["tsubame_message_full_text_plaintext"] = quoted_full_text_plaintext

    message_dict["full_text"] = full_text
    message_dict["tsubame_message_is_retweet"] = is_retweet
    message_dict["tsubame_message_is_quote"] = is_quote
    message_dict["tsubame_message_type"] = constants.MessageType.TWEET.value
    message_dict["tsubame_message_created_at_epoch"] = message.created_at_in_seconds
    message_dict["tsubame_message_source_plaintext"] = REMOVE_HTML_RE.sub("", message.source)
    message_dict["tsubame_message_full_text_plaintext"] = full_text_plaintext
    return message_dict, matches_active_id

