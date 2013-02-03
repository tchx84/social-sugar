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

from gi.repository import GObject

from sugar3.graphics.menuitem import MenuItem
from sugar3.graphics.toolbutton import ToolButton

class OnlineAccount(GObject.GObject):
    def is_configured(self):
        raise Exception("Not defined")

    def is_active(self):
        raise Exception("Not defined")

    def get_share_menu(self):
        raise Exception("Not defined")

    def get_refresh_button(self):
        raise Exception("Not defined")


class OnlineShareMenu(MenuItem):
    pass


class OnlineRefreshButton(ToolButton):
    def set_metadata(self, metadata):
        raise Exception("Not defined")
