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

from gi.repository import Gtk
from gi.repository import GObject
from gi.repository import WebKit

import urllib
import urlparse

from gettext import gettext as _

from sugar3.graphics.icon import CanvasIcon
from sugar3.graphics import style

from jarabe.controlpanel.sectionview import SectionView


class WebServicesConfig(SectionView):
    FB_APP_ID = "172917389475707"
    FB_REDIRECT_URI = "http://www.sugarlabs.org"

    def __init__(self, model, alerts):
        SectionView.__init__(self)

        self._model = model
        self.restart_alerts = alerts

        vbox = Gtk.VBox()
        hbox = Gtk.HBox(style.DEFAULT_SPACING)

        # Web services get added to the hbox
        icon = CanvasIcon(icon_name='facebook-share')
        icon.connect('button_press_event', self._fb_authorization_request_cb)
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

        self._wkv = WebKit.WebView()
        workspace.add(self._wkv)
        workspace.show_all()
        vbox.show()

    def undo(self):
        pass

    # Web-service-specific callbacks go here

    def _fb_authorization_request_cb(self, widget, event):
        logging.debug('fb authorization request')
        self._wkv.load_uri(self._fb_auth_url())
        self._wkv.grab_focus()
        self._wkv.connect('navigation-policy-decision-requested',
                          self._fb_nav_policy_cb)

    def _fb_auth_url(self):
        url = 'http://www.facebook.com/dialog/oauth'
        params = [
            ('client_id', self.FB_APP_ID),
            ('redirect_uri', self.FB_REDIRECT_URI),
            ('response_type', 'token'),
            ('scope', 'publish_stream')
            ]

        return "%s?%s" % (url, urllib.urlencode(params))

    def _fb_nav_policy_cb(self, view, frame, req, action, param):
        uri = req.get_uri()
        if uri is None:
            return

        url_o = urlparse.urlparse(uri)
        params = urlparse.parse_qs(url_o.fragment)
        if params.has_key('access_token') and params.has_key('expires_in'):
            self._model.fb_save_access_token(params['access_token'][0],
                                          int(params['expires_in'][0]))
