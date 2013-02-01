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

from gi.repository import Gtk
from gi.repository import GObject
from gi.repository import WebKit

import urllib
import urlparse

from gettext import gettext as _

from jarabe.controlpanel.sectionview import SectionView

class FacebookConfig(SectionView):
    APP_ID = "172917389475707"
    REDIRECT_URI = "http://www.sugarlabs.org"

    def __init__(self, model, alerts):
        SectionView.__init__(self)

        self._model = model
        self.restart_alerts = alerts

        scrolled = Gtk.ScrolledWindow()
        self.add(scrolled)
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.show()

        workspace = Gtk.VBox()
        scrolled.add_with_viewport(workspace)
        workspace.show()

        wkv = WebKit.WebView()
        wkv.load_uri(self._auth_url())
        wkv.grab_focus()
        wkv.connect('navigation-policy-decision-requested', self._nav_policy_cb)
        workspace.add(wkv)
        workspace.show_all()

    def undo(self):
        pass

    def _auth_url(self):
        url = 'http://www.facebook.com/dialog/oauth'
        params = [
            ('client_id', self.APP_ID),
            ('redirect_uri', self.REDIRECT_URI),
            ('response_type', 'token'),
            ('scope', 'publish_stream')
            ]

        return "%s?%s" % (url, urllib.urlencode(params))

    def _nav_policy_cb(self, view, frame, req, action, param):
        uri = req.get_uri()
        if uri is None:
            return

        url_o = urlparse.urlparse(uri)
        params = urlparse.parse_qs(url_o.fragment)
        if params.has_key('access_token') and params.has_key('expires_in'):
            self._model.save_access_token(params['access_token'][0],
                                          int(params['expires_in'][0]))
