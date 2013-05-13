# Copyright (C) 2013, Walter Bender - Raul Gutierrez Segales
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
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA

import logging

from gi.repository import GConf
from gi.repository import Gtk
from gettext import gettext as _
from cpsection.webservices.web_service import WebService

HOSTNAME = '/desktop/sugar/collaboration/journalx_hostname'
CREDENTIAL = '/desktop/sugar/collaboration/journalx_credential'

class JxService(WebService):

    def get_icon_name(self):
        return 'school-server'

    def _get_value(self, key):
        client = GConf.Client.get_default()
        value = client.get_string(key)
        return value

    def _get_hostname(self):
        return self._get_value(HOSTNAME)

    def _get_credential(self):
        return self._get_value(CREDENTIAL)

    def config_service_cb(self, widget, event, container):
        logging.debug('config_service_jx')

        vbox = Gtk.VBox()

        host_hbox = Gtk.HBox()
        host_label =  Gtk.Label(label=_('Hostname:'))
        host_entry = Gtk.Entry()
        host_entry.set_text(self._get_hostname())

        credential_hbox = Gtk.HBox()
        credential_label =  Gtk.Label(label=_('Secret:'))
        credential_entry = Gtk.Entry()
        credential_entry.set_text(self._get_credential())
        credential_entry.set_invisible_char('*')
        credential_entry.set_visibility(False)

        update_button = Gtk.Button()
        update_button.set_label(_('Update'))
        update_button.connect('clicked', self.__updated_clicked,
                              host_entry, credential_entry)

        host_hbox.add(host_label)
        host_hbox.add(host_entry)
        credential_hbox.add(credential_label)
        credential_hbox.add(credential_entry)
        vbox.add(host_hbox)
        vbox.add(credential_hbox)
        vbox.add(update_button)

        for c in container.get_children():
            container.remove(c)

        container.add(vbox)
        container.show_all()

    def __updated_clicked(self, button, host_entry, credential_entry):
        client = GConf.Client.get_default()
        hostname = host_entry.get_text()
        credential = credential_entry.get_text()
        client.set_string(HOSTNAME, hostname)
        client.set_string(CREDENTIAL, credential)

def get_service():
    return JxService()
