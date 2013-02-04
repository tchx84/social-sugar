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

import logging

from gi.repository import GObject

from sugar3.graphics.menuitem import MenuItem
from sugar3.graphics.toolbutton import ToolButton

class OnlineAccount(GObject.GObject):
    def get_description(self):
        raise Exception("Not defined")

    def is_configured(self):
        raise Exception("Not defined")

    def is_active(self):
        raise Exception("Not defined")

    def get_share_menu(self):
        raise Exception("Not defined")

    def get_refresh_button(self):
        raise Exception("Not defined")


'''
class _TransferWidget(GObject.GObject):
     __gsignals__ = {
        'transfer-started': (GObject.SignalFlags.RUN_FIRST, None, ([int, int])),
        'transfer-progress': (GObject.SignalFlags.RUN_FIRST, None, ([int, int, float])),
        'transfer-completed': (GObject.SignalFlags.RUN_FIRST, None, ([int, int])),
        'transfer-failed': (GObject.SignalFlags.RUN_FIRST, None, ([int, int, str])),
        'transfer-state-changed': (GObject.SignalFlags.RUN_FIRST, None, ([str])),
    }

    def _transfer_state_changed_cb(self, transfer_object, state):
        self.emit('transfer-state-changed', state)
'''

class OnlineShareMenu(MenuItem):
    __gsignals__ = {
        'transfer-started': (GObject.SignalFlags.RUN_FIRST, None, ([int, int])),
        'transfer-progress': (GObject.SignalFlags.RUN_FIRST, None, ([int, int, float])),
        'transfer-completed': (GObject.SignalFlags.RUN_FIRST, None, ([int, int])),
        'transfer-failed': (GObject.SignalFlags.RUN_FIRST, None, ([int, int, str])),
        'transfer-state-changed': (GObject.SignalFlags.RUN_FIRST, None, ([str])),
    }

    def _transfer_state_changed_cb(self, transfer_object, state):
        logging.debug('_transfer_state_changed_cb')
        self.emit('transfer-state-changed', state)


class OnlineRefreshButton(ToolButton):
    __gsignals__ = {
        'transfer-started': (GObject.SignalFlags.RUN_FIRST, None, ([int, int])),
        'transfer-progress': (GObject.SignalFlags.RUN_FIRST, None, ([int, int, float])),
        'transfer-completed': (GObject.SignalFlags.RUN_FIRST, None, ([int, int])),
        'transfer-failed': (GObject.SignalFlags.RUN_FIRST, None, ([int, int, str])),
        'transfer-state-changed': (GObject.SignalFlags.RUN_FIRST, None, ([str])),
    }

    def _transfer_state_changed_cb(self, transfer_object, state):
        logging.debug('_transfer_state_changed_cb')
        self.emit('transfer-state-changed', state)

    def set_metadata(self, metadata):
        raise Exception("Not defined")
