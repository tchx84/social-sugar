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
import os

from gi.repository import Gtk
from gi.repository import GObject
from gettext import gettext as _
from jarabe import config
from jarabe.controlpanel.sectionview import SectionView
from sugar3.graphics.icon import CanvasIcon
from sugar3.graphics import style


class WebServicesConfig(SectionView):
    def __init__(self, model, alerts):
        SectionView.__init__(self)

        self._model = model
        self.restart_alerts = alerts

        vbox = Gtk.VBox()
        hbox = Gtk.HBox(style.DEFAULT_SPACING)

        self._service_config_box = Gtk.VBox()

        for service in self._get_services():
            icon = CanvasIcon(icon_name=service.get_icon_name())
            icon.connect('button_press_event',
                         service.config_service_cb,
                         self._service_config_box)
            icon.show()
            hbox.pack_start(icon, False, False, 0)

        hbox.show()
        vbox.pack_start(hbox, False, False, 0)

        scrolled = Gtk.ScrolledWindow()
        vbox.pack_start(scrolled, True, True, 0)

        self.add(vbox)
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.show()

        workspace = Gtk.VBox()
        scrolled.add_with_viewport(workspace)
        workspace.show()

        workspace.add(self._service_config_box)
        workspace.show_all()
        vbox.show()

    def undo(self):
        pass

    def _get_services(self):
        services = []
        path = os.path.join(config.ext_path,
                            'cpsection',
                            'webservices',
                            'services')
        folders = os.listdir(path)

        for f in folders:
            if not os.path.isdir(os.path.join(path, f)):
                continue

            if not os.path.exists(os.path.join(path, f, 'service.py')):
                continue

            try:
                mod_name = 'cpsection.webservices.services.%s.service' % (f)
                mod = __import__(mod_name,
                                 globals(),
                                 locals(),
                                 ['service'])
                if hasattr(mod, 'get_service'):
                    services.append(mod.get_service())
            except Exception as ex:
                logging.exception(
                    'Exception while loading extension: %s' % str(ex))

        return services
