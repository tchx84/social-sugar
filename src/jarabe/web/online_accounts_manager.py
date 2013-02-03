#!/usr/bin/env python
#
# Copyright (c) 2013 Walter Bender

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
