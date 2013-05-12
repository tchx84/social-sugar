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
    stubs for five public methods that are used by online services
    '''

    def get_description(self):
        ''' get_description returns a brief description of the online
        service. The description is used in palette menuitems and on
        the webservices control panel.

        :returns: online-account name
        :rtype: string
        '''
        raise NotImplementedError

    def is_configured(self):
        ''' is_configured returns True if the service has been
        configured for use, e.g., an access token has been acquired.

        :returns: configuration status
        :rtype: bool
        '''
        raise NotImplementedError

    def is_active(self):
        ''' is_active returns True if the service is currently
        available, e.g., the access token has not expired.

        :returns: active status
        :rtype: bool
        '''
        raise NotImplementedError

    def get_share_menu(self):
        ''' get_share_menu returns a menu item used on the Copy To
        palette in the Journal and on the Journal detail-view toolbar.

        :param: journal_entry_metadata
        :type: dict
        :returns: MenuItem
        :rtype: MenuItem
        '''
        raise NotImplementedError

    def get_refresh_menu(self):
        ''' get_refresh_menu returns a menu item used on the Journal
        detail-view toolbar.

        :param: journal_entry_metadata
        :type: dict
        :returns: MenuItem
        :rtype: MenuItem
        '''
        raise NotImplementedError


class MenuItem(MenuItem):
    ''' This is a subclass of sugar3.graphics.menuitem.MenuItem

    The transfer signals are used to update progress of data transfer
    between Sugar and the online service. Signal handlers in the
    journaltoolbox manage a Notification Alert of this progress.

    'transfer-started' is emitted at the beginning of a transfer.

    'transfer-progress' is emitted periodically to indicate progress.

    :emits: total data to transfer
    :type: float
    :emits: quantity of data transfered
    :type: float
    :emits: message string
    :type: string

    'transfer-completed' is emitted at the successful completion of a
    transfer.

    :emits: message string
    :type: string

    'transfer-failed' is emitted at if the transfer fails.

    :emits: message string
    :type: string

    'transfer-state-changed' is emitted when the account manager wants
    to indicate a change in state.

    :emits: message string
    :type: string

    The comments-changed signal is emitted by the online service if
    changes to the 'comments' metadata have been made. The
    expandedentry of the Journal detail view displays these comments.

    :emits: metadata['comments']
    :type: string
    '''
    __gsignals__ = {
        'transfer-started': (GObject.SignalFlags.RUN_FIRST, None, ([])),
        'transfer-progress': (GObject.SignalFlags.RUN_FIRST, None,
                              ([int, int, str])),
        'transfer-completed': (GObject.SignalFlags.RUN_FIRST, None, ([str])),
        'transfer-failed': (GObject.SignalFlags.RUN_FIRST, None, ([str])),
        'transfer-state-changed': (GObject.SignalFlags.RUN_FIRST, None,
                                   ([str])),
        'comments-changed': (GObject.SignalFlags.RUN_FIRST, None, ([str]))
        }

    def set_metadata(self, metadata):
        ''' The online account uses this method to set metadata in the
        Sugar journal and provide a means of updating menuitem status,
        e.g., enabling the refresh menu after a successful transfer.

        :param: journal_entry_metadata
        :type: dict
        '''
        raise NotImplementedError
