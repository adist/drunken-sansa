# -*- coding: utf-8 -*-

##############################################################################
#
#    Authors: Boris Timokhin, Alexey Samoukin, Dmitry Zhuravlev-Nevsky.
#    
#    Copyright InfoSreda LLC.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import mimetypes
import os
import time

import cherrypy

import base64
from openobject.tools import expose

from openerp.controllers import SecuredController
from openerp.utils import rpc

from openobject.widgets import JSLink, CSSLink
from openerp.widgets.form import Notebook

# add gallery media to Notebook widget
javascripts = [JSLink("web_gallery", "javascript/jwplayer.js"),
               JSLink("web_gallery", "javascript/jquery.tinycarousel.js"),
               JSLink("web_gallery", "javascript/web_gallery.js"),]
Notebook.javascript.extend(javascripts)
Notebook.css = [CSSLink("web_gallery", "css/carousel.css")]


DEFAULT_MIMETYPE = 'application/octet-stream'
CACHE_ENABLED = False
CACHE_DIR = None
READ_CONFIG = True
UPDATE_COUNFIG_TTL = None
LAST_UPDATE_CONFIG_TIME = None

class WebGallery(SecuredController):
    _cp_path = "/webgallery"

    def check_time_config(self):
        global READ_CONFIG
        if time.time() > LAST_UPDATE_CONFIG_TIME + UPDATE_COUNFIG_TTL:
            READ_CONFIG = True

    def get_config(self):
        global READ_CONFIG, CACHE_ENABLED, CACHE_DIR, UPDATE_COUNFIG_TTL,\
            LAST_UPDATE_CONFIG_TIME
        if not READ_CONFIG:
            return
        config_data = rpc.RPCProxy('web.gallery.images').get_web_config_data()
        CACHE_ENABLED = config_data.get('web_cache_enabled', False)
        CACHE_DIR = config_data.get('web_cache_dir', None)
        UPDATE_COUNFIG_TTL = config_data.get('web_update_config_ttl', 300)
        READ_CONFIG = False
        LAST_UPDATE_CONFIG_TIME = time.time()
        self.check_time_config()

    def get_from_server(self, file_type, file_path, cache_file):
        model = 'web.gallery.%s' % file_type
        data = rpc.RPCProxy(model).get_data(file_path, rpc.session.context)
        data = base64.decodestring(data)

        if CACHE_ENABLED and cache_file:
            try:
                with open(cache_file, 'wb') as f:
                    f.write(data)
            except IOError:
                pass
        return data

    def get_mime_type(self, file_name):
        mime_type = mimetypes.guess_type(file_name)[0]
        if mime_type is None:
            return DEFAULT_MIMETYPE
        return mime_type

    @expose()
    def get(self, file_type, folder, file_name):
        if not file_type in ('images', 'docs', 'videos'):
            return ''
        self.get_config()

        data = None
        cache_file = None
        if CACHE_ENABLED:
            cache_dir = os.path.join(CACHE_DIR, folder)
            if not os.path.exists(cache_dir):
                try:
                    os.makedirs(cache_dir)
                except IOError:
                    pass

            cache_file = os.path.join(cache_dir, file_name)
            if os.path.exists(cache_file):
                try:
                    data = open(cache_file, 'r').read()
                except IOError:
                    pass

        cherrypy.response.headers['Content-Type'] = self.get_mime_type(file_name)
        if data is None:
            data = self.get_from_server(file_type,
                                      '%s/%s' % (folder, file_name), cache_file)
        return data
