#!/usr/bin/env python
#
# Copyright (c) 2013 Walter Bender, Raul Gutierrez Segales
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

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


class OnlineMenu(MenuItem):
    __gsignals__ = {
        'transfer-started': (GObject.SignalFlags.RUN_FIRST, None, ([int, int])),
        'transfer-progress': (GObject.SignalFlags.RUN_FIRST, None, ([int, int, float])),
        'transfer-completed': (GObject.SignalFlags.RUN_FIRST, None, ([int, int])),
        'transfer-failed': (GObject.SignalFlags.RUN_FIRST, None, ([int, int, str])),
        'transfer-state-changed': (GObject.SignalFlags.RUN_FIRST, None, ([str])),
        'comments-changed': (GObject.SignalFlags.RUN_FIRST, None, ([str])),
    }

    def _transfer_state_changed_cb(self, transfer_object, state):
        logging.debug('_transfer_state_changed_cb')
        self.emit('transfer-state-changed', state)

    def set_metadata(self, metadata):
        raise Exception("Not defined")
