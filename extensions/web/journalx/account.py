# Copyright (C) 2013, Martin Abente Lahaye - tch@sugarlabs.org
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 
# 02110-1301  USA.

from gettext import gettext as _
import json
import tempfile
import logging

from gi.repository import Gtk
from gi.repository import GdkPixbuf
from gi.repository import GConf

from sugar3.datastore import datastore
from sugar3.graphics.icon import Icon

from jarabe.web.account import Account
from jarabe.web.account import MenuItem

from journalx.entry import Entry
from journalx.setting import Setting


ENTRY_ID = 'jx_entry_id'
COMMENTS_IDS = 'jx_comments_ids'
COMMENTS = 'comments'

HOSTNAME = '/desktop/sugar/collaboration/journalx_hostname'
CREDENTIAL = '/desktop/sugar/collaboration/journalx_credential'

ACCOUNT_NAME = _('Journal Exposer')
ICON = 'school-server'
PLACEHOLDER = 'journalx'

class JxAccount(Account):

    def __init__(self):
        hostname, credential = self._settings()
        Setting.set_url(hostname)
        Setting.set_buddy_credential(credential)

    def _settings(self):
        client = GConf.Client.get_default()
        hostname = client.get_string(HOSTNAME)
        credential = client.get_string(CREDENTIAL)
        return (hostname, credential)

    def get_description(self):
        return ACCOUNT_NAME

    def is_configured(self):
        return None not in self._settings()

    def is_active(self):
        return self.is_configured()

    def get_share_menu(self, metadata):
        return JxShareMenu(metadata, self.is_active())

    def get_refresh_menu(self):
        return JxRefreshMenu(self.is_active())

class MenuItemPlus(MenuItem):

    def __init__(self, metadata, is_active):
        MenuItem.__init__(self, ACCOUNT_NAME)
        self.set_image(Icon(icon_name=ICON, icon_size=Gtk.IconSize.MENU))
        self.show()
        self._metadata = metadata

    def _uid(self):
        return self._get_metadata('uid')

    def _get_metadata(self, key):
        if key in self._metadata:
            return self._metadata[key]
        return None

    def _set_metadata(self, values):
        object = datastore.get(self._uid())
        for (key, value) in values:
            object.metadata[key] = value
        datastore.write(object, update_mtime=False)

class JxShareMenu(MenuItemPlus):

    def __init__(self, metadata, is_active):
        MenuItemPlus.__init__(self, metadata, is_active)
        self.connect('activate', self.__activated_cb)

    def _get_screenshot_path(self):
        screenshot_path = None

        loader = GdkPixbuf.PixbufLoader.new_with_mime_type('image/png')
        loader.set_size(300, 225)

        try:
            loader.write(self._get_metadata('preview'))
        except:
            logging.error('Could not write screenshot from %s',
                          self._metadata['uid'])
        else:
            screenshot_path = tempfile.mktemp()
            buffer = loader.get_pixbuf()
            buffer.savev(screenshot_path, 'png', [], [])
        finally:
            loader.close()
        
        return screenshot_path

    def __activated_cb(self, menu_item):
        title = self._get_metadata('title')
        description = self._get_metadata('description')
        screenshot_path = self._get_screenshot_path()

        # XXX need to think where to put this
        if not title:
            tittle = ''
        if not description:
            description = ''
        if not screenshot_path:
            logging.error('Object %s is empty', self._uid())
            return

        self.emit('transfer-state-changed', _('Download started'))

        entry_id = self._get_metadata(ENTRY_ID)
        entry = Entry(entry_id)

        if entry_id:
            entry.connect('entry-updated', self.__posted_cb)
            entry.connect('entry-updated-failed', self.__posted_failed_cb)
            entry.update(title, description, screenshot_path)
        else:
            entry.connect('entry-posted', self.__posted_cb)
            entry.connect('entry-posted-failed', self.__posted_failed_cb)
            entry.post(title, description, screenshot_path)

    def __posted_cb(self, entry, response):
        if self._get_metadata(ENTRY_ID):
            logging.debug('Object %s updated with id %s',
                          self._uid(), entry._id)
        else:
            self._set_metadata([(ENTRY_ID, entry._id)])
            logging.debug('Object %s posted with id %s',
                          self._uid(), entry._id)

    def __posted_failed_cb(self, entry, message):
        logging.error('Object %s could not be shared: %s',
                      self._uid(), message)

class JxRefreshMenu(MenuItemPlus):

    def __init__(self, is_active):
        MenuItemPlus.__init__(self, None, is_active)
        self.connect('activate', self.__activated_cb)

    def set_metadata(self, metadata):
        self._metadata = metadata

    def __activated_cb(self, menu_item):
        entry_id = self._get_metadata(ENTRY_ID)

        if not entry_id:
            logging.error('Object %s is not shared', self._get_metdata('uid'))
            return

        entry = Entry(entry_id)
        entry.connect('comments-downloaded', self.__downloaded_cb)
        entry.connect('comments-downloaded-failed', self.__downloaded_failed_cb)
        entry.comments()

    def __downloaded_cb(self, entry, response):
        comments = self._get_metadata(COMMENTS)
        if comments:
            comments = json.loads(comments)
        else:
            comments = []

        comments_ids = self._get_metadata(COMMENTS_IDS)
        if comments_ids:
            comments_ids = json.loads(comments_ids)
        else:
          comments_ids = []

        new_comments = False
        for comment in response:
            if comment['id'] in comments_ids:
                continue
            comments_ids.append(comment['id'])
            comments.append({'from': PLACEHOLDER,
                             'message': comment['text'],
                             'icon': ICON})
            new_comments = True

        if new_comments:
            comments_ids = json.dumps(comments_ids)
            comments = json.dumps(comments)
            self._set_metadata([(COMMENTS, comments),
                                (COMMENTS_IDS, comments_ids)])
            self.emit('comments-changed', comments)
        else:
            logging.debug('No new comments for %s',
                          self._get_metadata(ENTRY_ID))

    def __downloaded_failed_cb(self, entry, message):
        logging.error('Could not get comments from Object %s: %s',
                      self._get_metadata['uid'], message)

def get_account():
    return JxAccount()
