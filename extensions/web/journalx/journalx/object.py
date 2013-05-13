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

import pycurl
import urllib

from gi.repository import GObject

from setting import Setting


class Object(GObject.GObject):

    __gsignals__ = {
        'transfer-completed': (GObject.SignalFlags.RUN_FIRST, None, ([object])),
        'transfer-progress': (GObject.SignalFlags.RUN_FIRST, None,
                             ([float, float, str])),
        'transfer-failed': (GObject.SignalFlags.RUN_FIRST, None, ([str])),
        'transfer-started': (GObject.SignalFlags.RUN_FIRST, None, ([]))}

    def _generate_header(self):
        return ['X-Sugar-Buddy: %s' % Setting.get_buddy_credential()]

    def _update_cb(self, down_total, down_done, up_total, up_done, states):

        if 2 in states:
            return

        total = up_total
        done = up_done
        mode = 'upload'

        if 1 in states:
            total = down_total
            done = down_done
            mode = 'download'

        if total == 0:
            return

        if 0 not in states:
            self.emit('transfer-started')
            states.append(0)

        self.emit('transfer-progress', total, done, mode)

        state = states[-1]
        if total == done and state in states and len(states) == state + 1:
            states.append(state + 1)

    def request(self, method, url, params=None, file=None):
        c = pycurl.Curl()

        if method == 'POST':
            c.setopt(c.POST, 1)
            if file is not None:
                params += [(file['field'], (c.FORM_FILE, file['path']))]
            if params is not None:
                c.setopt(c.HTTPPOST, params)
            else:
                c.setopt(c.POSTFIELDS, '')

        elif method == 'GET':
            c.setopt(c.HTTPGET, 1)
            if params:
                url += '?%s' % urllib.urlencode(params)

        elif method == 'DELETE':
            c.setopt(pycurl.CUSTOMREQUEST, 'DELETE')
        else:
            raise Exception('Object', 'Invalid method')

        # XXX hack to trace transfer states
        states = []
        def pre_update_cb(*args):
            args = list(args) + [states]
            self._update_cb(*args)

        #XXX hack to write multiple responses
        buffer = []
        def __write_cb(data):
            buffer.append(data)

        c.setopt(c.HTTPHEADER, self._generate_header())
        c.setopt(pycurl.SSL_VERIFYPEER, 0)   
        c.setopt(pycurl.SSL_VERIFYHOST, 0)
        c.setopt(c.URL, url)
        c.setopt(c.NOPROGRESS, 0)
        c.setopt(c.PROGRESSFUNCTION, pre_update_cb)
        c.setopt(c.WRITEFUNCTION, __write_cb)
        #c.setopt(c.VERBOSE, True)

        try:
            c.perform()
        except pycurl.error, e:
            self.emit('transfer-failed', str(e))
        else:
            code = c.getinfo(c.HTTP_CODE)
            if code != 200:
                self.emit('transfer-failed', 'HTTP code %s' % code)
        finally:
            self.emit('transfer-completed', ''.join(buffer))
            c.close()
