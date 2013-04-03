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


class Account():
    ''' Account is a prototype class for online accounts. It provides
    stubs for five public methods that are used by online services:

    get_description returns a brief description of the online service
    used in palette menuitems and on the webservices control panel.

    is_configured returns True if the service has been configured for
    use, e.g., an access token has been acquired.

    is_active returns True if the service is currently available,
    e.g., the access token has not expired.

    get_share_menu returns a menu item used on the Copy To palette in
    the Journal and on the Journal detail view toolbar.

    get_refresh_menu returns a menu item used on the Journal detail
    view toolbar.
    '''

    def get_description(self):
        raise NotImplementedError

    def is_configured(self):
        raise NotImplementedError

    def is_active(self):
        raise NotImplementedError

    def get_share_menu(self):
        raise NotImplementedError

    def get_refresh_menu(self):
        raise NotImplementedError


class MenuItem(MenuItem):
    __gsignals__ = {
        'transfer-started': (GObject.SignalFlags.RUN_FIRST, None,
                             ([int, int])),
        'transfer-progress': (GObject.SignalFlags.RUN_FIRST, None,
                              ([int, int, float])),
        'transfer-completed': (GObject.SignalFlags.RUN_FIRST, None,
                               ([int, int])),
        'transfer-failed': (GObject.SignalFlags.RUN_FIRST, None,
                            ([int, int, str])),
        'transfer-state-changed': (GObject.SignalFlags.RUN_FIRST, None,
                                   ([str])),
        'comments-changed': (GObject.SignalFlags.RUN_FIRST, None, ([str])),
    }

    def set_metadata(self, metadata):
        raise NotImplementedError
