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


class Comment(ObjectPlus):

    POST_URL = '/entries/%s/comments/'
    DELETE_URL = '/entries/%s/comments/%s'

    __gsignals__ = {
        'comment-posted':         (GObject.SignalFlags.RUN_FIRST,
                                  None, ([object])),
        'comment-posted-failed':  (GObject.SignalFlags.RUN_FIRST,
                                  None, ([str])),
        'comment-deleted':        (GObject.SignalFlags.RUN_FIRST,
                                  None, ([object])),
        'comment-deleted-failed': (GObject.SignalFlags.RUN_FIRST,
                                  None, ([str]))}

    def __init__(self, entry_id, comment_id=None):
        ObjectPlus.__init__(self, comment_id)
        self._entry_id = entry_id

    def post(self, text):
        self._check_is_not_created()
        GObject.idle_add(self._post,
                         self.POST_URL % self._entry_id,
                         self._params(text),
                         None,
                         'comment-posted',
                         'comment-posted-failed')

    def delete(self):
        self._check_is_created()
        GObject.idle_add(self._delete,
                         self.DELETE_URL % (self._entry_id, self._id),
                         'comment-deleted',
                         'comment-deleted-failed')

    def _params(self, text):
      params = []
      params +=  [('entry_id', (self._entry_id))]
      params +=  [('text', (text))]
      return params
