import unittest
import tempfile
import os
import sys

from gui.qt5 import lib

class Qt5GUITest(unittest.TestCase):

    def process_twitter_message_text_url_test(self):
        """Check Twitter text message processing for Qt 5 - make urls clickable."""
        message_dict = {
            "urls" : [
                {"url" : "https://short.url.com/foo", "expanded_url" : "https://expanded.url.com/foo"},
                {"url" : "https://short.url.com/bar", "expanded_url" : "https://expanded.url.com/bar"},
                {"url" : "https://short.url.com/baz", "expanded_url" : "https://expanded.url.com/baz"}
            ]
        }
        full_text = "foo https://short.url.com/foo bar https://short.url.com/bar baz https://short.url.com/baz"
        result_text, result_plaintext = lib.process_twitter_message_text(full_text, message_dict)
        # check the short URLs have been correctly replaced by extended URL & plaintext does not
        # have clickable links
        expected_result_text = 'foo <a href="https://expanded.url.com/foo">https://expanded.url.com/foo</a> bar <a href="https://expanded.url.com/bar">https://expanded.url.com/bar</a> baz <a href="https://expanded.url.com/baz">https://expanded.url.com/baz</a>'
        expected_result_plaintext = 'foo https://expanded.url.com/foo bar https://expanded.url.com/bar baz https://expanded.url.com/baz'
        self.assertEqual(result_text, expected_result_text)
        self.assertEqual(result_plaintext, expected_result_plaintext)


    def process_twitter_message_text_drop_media_urls_test(self):
        """Check Twitter text message processing for Qt 5 - drop media urls."""
        message_dict = {
            "media" : [
                {"url" : "https://media.url.com/foo"},
                {"url" : "https://media.url.com/bar"},
                {"url" : "https://media.url.com/baz"}
            ]
        }

        full_text = "blah blah blah https://media.url.com/foo https://media.url.com/bar https://media.url.com/baz"
        result_text, result_plaintext = lib.process_twitter_message_text(full_text, message_dict)
        # check the results are correctly stripped of the media links
        expected_result_text = 'blah blah blah'
        expected_result_plaintext = 'blah blah blah'
        self.assertEqual(result_text, expected_result_text)
        self.assertEqual(result_plaintext, expected_result_plaintext)


    def process_twitter_message_text_clickable_hashtags_test(self):
        """Check Twitter text message processing for Qt 5 - clickable hashtags."""
        # check that hashtags are correctly turned into clickable links, including non-ASCII hashtags
        message_dict = {
            "hashtags" : [
                {"text" : "cat_ears"},
                {"text" : "kočičí_uši"},
                {"text" : "猫耳"},
                {"text" : "けものフレンズ"},
            ]
        }
        # we include a user mention and some message text before and after the hashtags
        full_text = "@tsubame_project Serval-chan is very cute! #cat_ears #kočičí_uši #猫耳 #けものフレンズ 楽しい!!"
        result_text, result_plaintext = lib.process_twitter_message_text(full_text, message_dict)
        # check the results have correctly processed hashtags
        expected_result_text = '@tsubame_project Serval-chan is very cute! <a href="#cat_ears">#cat_ears</a> ' \
                               '<a href="#kočičí_uši">#kočičí_uši</a> ' \
                               '<a href="#猫耳">#猫耳</a> ' \
                               '<a href="#けものフレンズ">#けものフレンズ</a> ' \
                               '楽しい!!'
        expected_result_plaintext = "@tsubame_project Serval-chan is very cute! #cat_ears #kočičí_uši #猫耳 #けものフレンズ 楽しい!!"
        self.assertEqual(result_text, expected_result_text)
        self.assertEqual(result_plaintext, expected_result_plaintext)

    def process_twitter_message_text_newline_test(self):
        """Check Twitter text message processing for Qt 5 - newline replacement."""
        message_dict = {}
        full_text = 'a\n\nb\nc <a href="http://www.example.com">foo</a>'
        result_text, result_plaintext = lib.process_twitter_message_text(full_text, message_dict)
        # check that the resulting text contains <br> instead of \n and
        # does not contain the hyperlink
        expected_result_text = 'a<br><br>b<br>c <a href="http://www.example.com">foo</a>'
        expected_result_plaintext = 'a\n\nb\nc foo'
        self.assertEqual(result_text, expected_result_text)
        self.assertEqual(result_plaintext, expected_result_plaintext)

    def process_twitter_message_text_combined_test(self):
        """Check Twitter text message processing for Qt 5 - combined test."""
        # check all the text processing techniques at once to verify they don't interfere with each other
        # - clickable hashtags
        # - media URL removal
        # - URL expansion
        # - newline replacement (in fulltext only)
        # - correct plaintext version
        message_dict = {
            "hashtags" : [
                {"text" : "猫耳"},
                {"text" : "けものフレンズ"},
            ],
            "media" : [
                {"url" : "https://kaban.media.org/sugoi"}
            ],
            "urls" : [
                {"url" : "https://short.japari.park/boss", "expanded_url" : "https://expanded.japari.park/boss"}
            ]
        }
        full_text = "@tsubame_project Serval-chan is very cute!\n#猫耳 #けものフレンズ https://short.japari.park/boss\n楽しい!! https://kaban.media.org/sugoi"
        result_text, result_plaintext = lib.process_twitter_message_text(full_text, message_dict)
        # check the results look correct
        expected_result_text = '@tsubame_project Serval-chan is very cute!<br>' \
                               '<a href="#猫耳">#猫耳</a> ' \
                               '<a href="#けものフレンズ">#けものフレンズ</a> ' \
                               '<a href="https://expanded.japari.park/boss">https://expanded.japari.park/boss</a><br>' \
                               '楽しい!!'
        expected_result_plaintext = "@tsubame_project Serval-chan is very cute!\n#猫耳 #けものフレンズ https://expanded.japari.park/boss\n楽しい!!"
        self.assertEqual(result_text, expected_result_text)
        self.assertEqual(result_plaintext, expected_result_plaintext)


