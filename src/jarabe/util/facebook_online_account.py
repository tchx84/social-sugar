#!/usr/bin/env python
#
# Copyright (c) 2013 Walter Bender, Raul Gutierrez Segales

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

from gi.repository import Gtk
from gi.repository import GdkPixbuf
from gi.repository import GConf

from sugar3.datastore import datastore
from sugar3.graphics.alert import Alert, NotifyAlert
from sugar3.graphics.icon import Icon

from jarabe.journal import journalwindow
from jarabe.util import facebook
from jarabe.util import online_account

ACCOUNT_NEEDS_ATTENTION = 0
ACCOUNT_ACTIVE = 1


class FacebookOnlineAccount(online_account.OnlineAccount):

    ACCESS_TOKEN_KEY = "/desktop/sugar/collaboration/facebook_access_token"
    ACCESS_TOKEN_KEY_EXPIRATION_DATE = \
        "/desktop/sugar/collaboration/facebook_access_token_expiration_date"

    def __init__(self):
        online_account.OnlineAccount.__init__(self)
        self._client = GConf.Client.get_default()
        facebook.FbAccount.set_access_token(self._access_token())

    def is_configured(self):
        return self._access_token() is not None

    def is_active(self):
        expiration_date = \
            self._client.get_int(self.ACCESS_TOKEN_KEY_EXPIRATION_DATE)
        return expiration_date != 0 and expiration_date > time.time()

    def get_share_menu(self, journal_entry_metadata):
        if self.is_active():
            icon_name = 'facebook-share'
        else:
            icon_name = 'facebook-share-insensitive'
        fb_share_menu = FacebookShareMenu(journal_entry_metadata)
        fb_share_menu.set_image(Icon(icon_name=icon_name,
                                     icon_size=Gtk.IconSize.MENU))
        fb_share_menu.show()
        return fb_share_menu

    def get_refresh_button(self):
        return FacebookRefreshButton(self.is_active())

    def _access_token(self):
        return self._client.get_string(self.ACCESS_TOKEN_KEY)


class FacebookShareMenu(online_account.OnlineShareMenu):
    __gtype_name__ = 'JournalFacebookMenu'

    def __init__(self, metadata):
        online_account.OnlineShareMenu.__init__(self, _('Facebook'))

        self._metadata = metadata
        self._comment = '%s: %s' % (self._get_metadata_by_key('title'),
                                    self._get_metadata_by_key('description'))

        self.connect('activate', self._facebook_share_menu_cb)

    def _get_metadata_by_key(self, key, default_value=''):
        if key in self._metadata:
            return self._metadata[key]
        return default_value

    def _facebook_share_menu_cb(self, menu_item):
        logging.debug('_facebook_share_menu_cb')

        tmp_file = tempfile.mktemp()
        self._image_file_from_metadata(tmp_file)

        photo = facebook.FbPhoto()
        photo.connect('photo-created', self._photo_created_cb, tmp_file)
        photo.connect('photo-create-failed',
                      self._photo_create_failed_cb,
                      tmp_file)
        result = photo.create(tmp_file)

    def _photo_created_cb(self, fb_photo, fb_object_id, tmp_file):
        logging.debug("_photo_created_cb")

        if os.path.exists(tmp_file):
            os.unlink(tmp_file)

        fb_photo.connect('comment-added', self._comment_added_cb)
        fb_photo.connect('comment-add-failed', self._comment_add_failed_cb)
        fb_photo.add_comment(self._comment)

        try:
            ds_object = datastore.get(self._metadata['uid'])
            ds_object.metadata['fb_object_id'] = fb_object_id
            datastore.write(ds_object, update_mtime=False)
        except Exception as ex:
            logging.debug("_photo_created_cb failed to write to datastore: " % \
                              str(ex))

    def _photo_create_failed_cb(self, fb_photo, failed_reason, tmp_file):
        logging.debug("_photo_create_failed_cb")

        if os.path.exists(tmp_file):
            os.unlink(tmp_file)

        self._fb_notify(failed_reason)

    def _comment_added_cb(self, fb_photo, fb_comment_id):
        logging.debug("_comment_added_cb")
        self._fb_notify(_('Upload successful'))

    def _comment_add_failed_cb(self, fb_photo, failed_reason):
        logging.debug("_comment_add_failed_cb")
        self._fb_notify(failed_reason)

    def _fb_notify(self, message):
        alert = NotifyAlert()
        title_string = _('Facebook')
        alert.props.title = title_string
        alert.props.msg = message
        alert.connect('response', self._facebook_alert_response_cb)
        journalwindow.get_journal_window().add_alert(alert)
        alert.show()

    def _facebook_alert_response_cb(self, alert, response_id):
        journalwindow.get_journal_window().remove_alert(alert)

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


class FacebookRefreshButton(online_account.OnlineRefreshButton):
    def __init__(self, is_active):
        online_account.OnlineRefreshButton.__init__(self, 'facebook-refresh-insensitive')

        self._metadata = None
        self._is_active = is_active
        self.set_tooltip(_('Facebook refresh'))
        self.set_sensitive(False)
        self.connect('clicked', self._fb_refresh_button_clicked_cb)
        self.show()

    def set_metadata(self, metadata):
        self._metadata = metadata
        if self._is_active:
            if self._metadata and 'fb_object_id' in self._metadata:
                self.set_sensitive(True)
                self.set_icon_name('facebook-refresh')

    def _fb_refresh_button_clicked_cb(self, button):
        logging.debug('_fb_refresh_button_clicked_cb')

        if self._metadata is None:
            logging.debug('_fb_refresh_button_clicked_cb called without metadata')
            return

        fb_photo = facebook.FbPhoto(self._metadata['fb_object_id'])
        fb_photo.connect('comments-downloaded',
                         self._fb_comments_downloaded_cb)
        fb_photo.connect('comments-download-failed',
                         self._fb_comments_download_failed_cb)
        fb_photo.refresh_comments()

    def _fb_comments_downloaded_cb(self, fb_photo, comments):
        logging.debug('_fb_comments_downloaded_cb')

        ds_object = datastore.get(self._metadata['uid'])
        for comment in comments:
            c_str = "%s: %s" % (comment['from'], comment['message'])
            ds_object.metadata['description'] += c_str

        datastore.write(ds_object, update_mtime=False)

    def _fb_comments_download_failed_cb(self, fb_photo, failed_reason):
        logging.debug('_fb_comments_download_failed_cb: %s' % (failed_reason))
        alert = NotifyAlert()
        alert.props.title = _('Comments download')
        alert.props.msg = failed_reason
        alert.connect('response', self.__fb_refresh_offline_response_cb)
        journalwindow.get_journal_window().add_alert(alert)
        alert.show()

    def __fb_refresh_offline_response_cb(self, alert, alert_id):
        pass
