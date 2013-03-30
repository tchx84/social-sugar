#!/usr/bin/env python
#
# Copyright (c) 2013 Walter Bender
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

from gi.repository import Gtk
from gi.repository import GObject
import logging
import os

from jarabe import config


class OnlineAccountsManager(GObject.GObject):
    @classmethod
    def all_accounts(cls):
        accounts = []

        icon_theme = Gtk.IconTheme.get_default()
        icon_search_path = icon_theme.get_search_path()

        web_path = os.path.join(config.ext_path, 'web')
        for d in os.listdir(web_path):
            dir_path = os.path.join(web_path, d)
            if os.path.isdir(dir_path):
                for f in os.listdir(dir_path):
                    if f.endswith('.py') and not f.startswith('__'):
                        module_name = f[:-3]
                        logging.debug("OnlineAccountsManager loading %s" % \
                                          (module_name))
                        try:
                            mod = __import__('web.' + d + '.' + module_name, globals(),
                                             locals(), [module_name])
                            if hasattr(mod, 'get_account'):
                                accounts.append(mod.get_account())
                        except Exception:
                            logging.exception('Exception while loading extension:')
                    elif f == 'icons':
                        icon_path = os.path.join(dir_path, f)
                        if os.path.isdir(icon_path) and \
                           icon_path not in icon_search_path:
                            logging.debug("OnelineAccountsManager adding %s to icon_theme" % (icon_path))
                            icon_theme.append_search_path(icon_path)

        return accounts

    @classmethod
    def configured_accounts(cls):
        return [a for a in cls.all_accounts() if a.is_configured()]

    @classmethod
    def active_accounts(cls):
        return [a for a in cls.all_accounts() if a.is_active()]
