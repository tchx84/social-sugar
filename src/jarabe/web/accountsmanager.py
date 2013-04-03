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

import os
import logging

from gi.repository import Gtk

from jarabe import config


def get_all_accounts():
    accounts = []

    web_path = os.path.join(config.ext_path, 'web')
    if os.path.exists(web_path):
        for d in os.listdir(web_path):
            dir_path = os.path.join(web_path, d)
            module = _load_module(dir_path)
            if module is not None:
                accounts.append(module)
                _load_icon_path(dir_path)

    return accounts


def _load_module(dir_path):
    module = None
    if os.path.isdir(dir_path):
        for f in os.listdir(dir_path):
            if f.endswith('.py') and not f.startswith('__'):
                module_name = f[:-3]
                logging.debug('OnlineAccountsManager loading %s' % (
                        module_name))

                try:
                    mod = __import__(
                        'web.' + os.path.basename(dir_path) + '.' + \
                            module_name,
                        globals(),
                        locals(),
                        [module_name])
                    if hasattr(mod, 'get_account'):
                        module = mod.get_account()

                except Exception as e:
                    logging.exception('Exception while loading %s: %s' % (
                            module_name, str(e)))

    return module


def _load_icon_path(dir_path):
    icon_theme = Gtk.IconTheme.get_default()
    icon_search_path = icon_theme.get_search_path()

    if os.path.isdir(dir_path):
        for f in os.listdir(dir_path):
            if f == 'icons':
                icon_path = os.path.join(dir_path, f)
                if os.path.isdir(icon_path) and \
                        icon_path not in icon_search_path:
                    icon_theme.append_search_path(icon_path)


def get_configured_accounts():
    return [a for a in get_all_accounts() if a.is_configured()]


def get_active_accounts():
    return [a for a in get_all_accounts() if a.is_active()]
