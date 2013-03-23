#!/usr/bin/env python
#
# Copyright (c) 2013 Walter Bender, Raul Gutierrez Segales, Martin Abente

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#THE SOFTWARE.

from gettext import gettext as _
import logging
import os
import tempfile
import time
import json

from twitter.twr_account import TwrAccount
from twitter.twr_status import TwrStatus
from twitter.twr_timeline import TwrTimeline

from gi.repository import Gtk
from gi.repository import GdkPixbuf
from gi.repository import GConf
from gi.repository import GObject

from sugar3.datastore import datastore
from sugar3.graphics.alert import NotifyAlert
from sugar3.graphics.icon import Icon

from jarabe.journal import journalwindow

from jarabe.web import online_account

ACCOUNT_NEEDS_ATTENTION = 0
ACCOUNT_ACTIVE = 1
ONLINE_ACCOUNT_NAME = _('Twitter')
COMMENTS = 'comments'
COMMENT_IDS = 'twr_comment_ids'

class TwitterOnlineAccount(online_account.OnlineAccount):

    CONSUMER_TOKEN_KEY = "/desktop/sugar/collaboration/twitter_consumer_token"
    CONSUMER_SECRET_KEY = "/desktop/sugar/collaboration/twitter_consumer_secret"
    ACCESS_TOKEN_KEY = "/desktop/sugar/collaboration/twitter_access_token"
    ACCESS_SECRET_KEY = "/desktop/sugar/collaboration/twitter_access_secret"

    def __init__(self):
        online_account.OnlineAccount.__init__(self)
        self._client = GConf.Client.get_default()
        ctoken, csecret, atoken, asecret = self._access_tokens()
        TwrAccount.set_secrets(ctoken, csecret, atoken, asecret)
        self._alert = None

    def get_description(self):
        return ONLINE_ACCOUNT_NAME

    def is_configured(self):
        return None not in self._access_tokens()

    def is_active(self):
        # No expiration date
        return None not in self._access_tokens()

    def get_share_menu(self, journal_entry_metadata):
        twr_share_menu = _TwitterShareMenu(journal_entry_metadata,
                                          self.is_active())
        self._connect_transfer_signals(twr_share_menu)
        return twr_share_menu

    def get_refresh_button(self):
        twr_refresh_button = _TwitterRefreshButton(self.is_active())
        self._connect_transfer_signals(twr_refresh_button)
        return twr_refresh_button

    def _connect_transfer_signals(self, transfer_widget):
        transfer_widget.connect('transfer-state-changed',
                                self._transfer_state_changed_cb)

    def _transfer_state_changed_cb(self, widget, state_message):
        logging.debug('_transfer_state_changed_cb')

        # First, remove any existing alert
        if self._alert is None:
            self._alert = NotifyAlert()
            self._alert.props.title = ONLINE_ACCOUNT_NAME
            self._alert.connect('response', self._alert_response_cb)
            journalwindow.get_journal_window().add_alert(self._alert)
            self._alert.show()

        logging.debug(state_message)
        self._alert.props.msg = state_message

    def _alert_response_cb(self, alert, response_id):
        journalwindow.get_journal_window().remove_alert(alert)
        self._alert = None

    def _access_tokens(self):
        return (self._client.get_string(self.CONSUMER_TOKEN_KEY),
                self._client.get_string(self.CONSUMER_SECRET_KEY),
                self._client.get_string(self.ACCESS_TOKEN_KEY),
                self._client.get_string(self.ACCESS_SECRET_KEY))


class _TwitterShareMenu(online_account.OnlineShareMenu):
    __gtype_name__ = 'JournalTwitterMenu'

    def __init__(self, metadata, is_active):
        online_account.OnlineShareMenu.__init__(self, ONLINE_ACCOUNT_NAME)

        if is_active:
            icon_name = 'twitter-share'
        else:
            icon_name = 'twitter-share-insensitive'
        self.set_image(Icon(icon_name=icon_name,
                            icon_size=Gtk.IconSize.MENU))
        self.show()
        self._metadata = metadata
        self._comment = '%s: %s' % (self._get_metadata_by_key('title'),
                                    self._get_metadata_by_key('description'))

        self.connect('activate', self._twitter_share_menu_cb)

    def _get_metadata_by_key(self, key, default_value=''):
        if key in self._metadata:
            return self._metadata[key]
        return default_value

    def __status_updated_cb(self, tweet, data):
        self._metadata['twr_object_id'] = tweet._status_id

    def _twitter_share_menu_cb(self, menu_item):
        logging.debug('_twitter_share_menu_cb')

        self.emit('transfer-state-changed', _('Download started'))
        tmp_file = tempfile.mktemp()
        self._image_file_from_metadata(tmp_file)

        tweet = TwrStatus()
        tweet.connect('status-updated', self.__status_updated_cb)
        tweet.update_with_media(self._comment, tmp_file)

    def _image_file_from_metadata(self, image_path):
        """ Load a pixbuf from a Journal object. """
        pixbufloader = \
            GdkPixbuf.PixbufLoader.new_with_mime_type('image/png')
        pixbufloader.set_size(300, 225)
        try:
            pixbufloader.write(self._metadata['preview'])
            pixbuf = pixbufloader.get_pixbuf()
        except Exception as ex:
            logging.debug("_image_file_from_metadata: %s" % (str(ex)))
            pixbuf = None

        pixbufloader.close()
        if pixbuf:
            pixbuf.savev(image_path, 'png', [], [])


class _TwitterRefreshButton(online_account.OnlineRefreshButton):
    def __init__(self, is_active):
        online_account.OnlineRefreshButton.__init__(
            self, 'twitter-refresh-insensitive')

        self._metadata = None
        self._is_active = is_active
        self.set_tooltip(_('Twitter refresh'))
        self.set_sensitive(False)
        self.connect('clicked', self._twr_refresh_button_clicked_cb)
        self.show()

    def set_metadata(self, metadata):
        self._metadata = metadata
        if self._is_active:
            if self._metadata:
                if 'twr_object_id' in self._metadata:
                    self.set_sensitive(True)
                    self.set_icon_name('twitter-refresh')
                else:
                    self.set_sensitive(False)
                    self.set_icon_name('twitter-refresh-insensitive')

    def _twr_refresh_button_clicked_cb(self, button):
        logging.debug('_twr_refresh_button_clicked_cb')

        if self._metadata is None:
            logging.debug('_twr_refresh_button_clicked_cb called without metadata')
            return

        if 'twr_object_id' not in self._metadata:
            logging.debug('_twr_refresh_button_clicked_cb called without twr_object_id in metadata')
            return

        self.emit('transfer-state-changed', _('Download started'))

        timeline = TwrTimeline()
        timeline.connect('mentions-downloaded', self._twr_mentions_downloaded_cb)
        timeline.mentions_timeline(800, self._metadata['twr_object_id'])

    def _twr_mentions_downloaded_cb(self, timeline, data):
        logging.debug('_twr_mentions_downloaded_cb')

        ds_object = datastore.get(self._metadata['uid'])
        if not COMMENTS in ds_object.metadata:
            ds_comments = []
        else:
            ds_comments = json.loads(ds_object.metadata[COMMENTS])
        if not COMMENT_IDS in ds_object.metadata:
            ds_comment_ids = []
        else:
            ds_comment_ids = json.loads(ds_object.metadata[COMMENT_IDS])

        new_comment = False
        for comment in data:
            # XXX hope for a better API
            if comment['in_reply_to_user_id_str'] != self._metadata['twr_object_id']:
               continue

            if comment['id_str'] not in ds_comment_ids:
                ds_comments.append({'from': comment['user_mentions']['name'],
                                    'message': comment['text'],
                                    'icon': 'twitter-share'})
                ds_comment_ids.append(comment['id_str'])
                new_comment = True

        if new_comment:
            ds_object.metadata[COMMENTS] = json.dumps(ds_comments)
            ds_object.metadata[COMMENT_IDS] = json.dumps(ds_comment_ids)
            self.emit('comments-updated')

        datastore.write(ds_object, update_mtime=False)

    def _twr_comments_download_failed_cb(self, tweet, failed_reason):
        logging.debug('_twr_comments_download_failed_cb: %s' % (failed_reason))

def get_account():
    return TwitterOnlineAccount()
