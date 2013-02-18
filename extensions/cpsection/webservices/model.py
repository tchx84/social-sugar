# Copyright (C) 2013 Walter Bender - Raul Gutierrez Segales
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
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#

from gettext import gettext as _
from gi.repository import GConf

import os
import time

from web.fb import facebook_online_account as fboa

def fb_save_access_token(access_token, expires_in):
    client = GConf.Client.get_default()
    client.set_string(fboa.FacebookOnlineAccount.ACCESS_TOKEN_KEY, access_token)
    expiry_time = int(time.time()) + expires_in
    client.set_int(fboa.FacebookOnlineAccount.ACCESS_TOKEN_KEY_EXPIRATION_DATE,
                   expiry_time)
