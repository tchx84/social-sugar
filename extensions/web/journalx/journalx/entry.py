# Copyright (c) 2013 Martin Abente Lahaye. - tch@sugarlabs.org
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301 USA.

from gi.repository import GObject

from object_plus import ObjectPlus


class Entry(ObjectPlus):

    POST_URL = '/entries/'
    UPDATE_URL = '/entries/%s'
    GET_URL = '/entries/%s'
    DELETE_URL = '/entries/%s'
    COMMENTS_URL = '/entries/%s/comments/'
    SCREENSHOT_URL = '/entries/%s/screenshot'

    __gsignals__ = {
        'entry-posted':                 (GObject.SignalFlags.RUN_FIRST,
                                        None, ([object])),
        'entry-posted-failed':          (GObject.SignalFlags.RUN_FIRST,
                                        None, ([str])),
        'entry-updated':                (GObject.SignalFlags.RUN_FIRST,
                                        None, ([object])),
        'entry-updated-failed':         (GObject.SignalFlags.RUN_FIRST,
                                        None, ([str])),
        'entry-downloaded':             (GObject.SignalFlags.RUN_FIRST,
                                        None, ([object])),
        'entry-downloaded-failed':      (GObject.SignalFlags.RUN_FIRST,
                                        None, ([str])),
        'entry-deleted':                (GObject.SignalFlags.RUN_FIRST,
                                        None, ([object])),
        'entry-deleted-failed':         (GObject.SignalFlags.RUN_FIRST,
                                        None, ([str])),
        'comments-downloaded':          (GObject.SignalFlags.RUN_FIRST,
                                        None, ([object])),
        'comments-downloaded-failed':   (GObject.SignalFlags.RUN_FIRST,
                                        None, ([str])),
        'screenshot-downloaded':        (GObject.SignalFlags.RUN_FIRST,
                                        None, ([object])),
        'screenshot-downloaded-failed': (GObject.SignalFlags.RUN_FIRST,
                                        None, ([str]))}

    def post(self, title, desc, screenshot_path):
        self._check_is_not_created()
        GObject.idle_add(self._post,
                         self.POST_URL,
                         self._params(title, desc),
                         self._file('screenshot', screenshot_path),
                         'entry-posted',
                         'entry-posted-failed')

    def update(self, title=None, desc=None, screenshot_path=None):
        self._check_is_created()
        GObject.idle_add(self._post,
                         self.UPDATE_URL % self._id,
                         self._params(title, desc),
                         self._file('screenshot', screenshot_path),
                         'entry-updated',
                         'entry-updated-failed')

    def get(self):
        self._check_is_created()
        GObject.idle_add(self._get,
                         self.GET_URL % self._id,
                         None,
                         'entry-downloaded',
                         'entry-downloaded-failed')

    def delete(self):
        self._check_is_created()
        GObject.idle_add(self._delete,
                         self.DELETE_URL % self._id,
                         'entry-deleted',
                         'entry-deleted-failed')

    def comments(self):
        self._check_is_created()
        GObject.idle_add(self._get,
                         self.COMMENTS_URL % self._id,
                         None,
                         'comments-downloaded',
                         'comments-downloaded-failed')

    def screenshot(self):
        self._check_is_created()
        GObject.idle_add(self._get,
                         self.SCREENSHOT_URL % self._id,
                         None,
                         'screenshot-downloaded',
                         'screenshot-downloaded-failed')

    def _params(self, title=None, desc=None):
        params = []
        if title is not None:
          params += [('title', (title))]
        if desc is not None:
          params +=  [('desc', (desc))]

        return params
