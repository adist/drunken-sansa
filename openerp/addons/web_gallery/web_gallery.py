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

import re
import uuid
import base64
import os

#from PIL import Image

from openerp.osv import osv, fields
 
BASE_URL = '/webgallery/get/'


def gen_name():
    path = re.sub(r'[\W]', '0', base64.b64encode(uuid.uuid4().bytes)[:9])
    return path[0], path[1:]

def gen_name_dirname_filename(ext, base_dir=None):
    name = gen_name()
    filename = '.'.join([name[1], 'jpg'])
    if base_dir is None:
        return name[0], filename
    dirname = os.path.join(base_dir, name[0])
    return name, dirname, filename

def save_file(b64, ext, base_dir):
    name, dirname, filename = gen_name_dirname_filename(ext, base_dir)
    
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    
    file_path = os.path.join(dirname, filename)
    bit_buffer = base64.decodestring(b64)
    with open(file_path, 'wb') as file_obj:
        file_obj.write(bit_buffer)
    return name[0], filename

def get_config_data(cr, uid, pool):
    model='web.gallery.images'
    ir_values_obj = pool.get('ir.values')
    params = ir_values_obj.get(cr, uid, 'default', False, [model])
    res = dict( ( (param[1], param[2]) for param in params) )
    return res

class web_gallery_base(osv.AbstractModel):
    _name = 'web.gallery.abstract'
    STORAGE_TYPE = 'db'
    MEDIA_PATH = None

    def __init__(self, pool, cr):
        self.set_config_data(pool, cr, 0)
        super(web_gallery_base, self).__init__(pool, cr)

    def set_config_data(self, pool, cr, uid):
        data = get_config_data(cr, uid, pool)
        self.__class__.STORAGE_TYPE = data.get('type_file_storage', 'db')
        self.__class__.MEDIA_PATH = data.get('directory_storage', None)

    def get_origin_file_data(self, cr, uid, id):
        each = self.read(cr, uid, id, ['name'])
        data = ''
        if each['name']:
            try:
                filename = os.path.join(self.MEDIA_PATH, self.DIRNAME,
                                        each['name'])
                f = open(filename , 'rb')
                data = base64.encodestring(f.read())
                f.close()
            except:
                pass

        return data

    def get_origin_db_data(self, cr, uid, id):
        each = self.read(cr, uid, id, ['data'])
        data = ''
        if each['data']:
            data = each['data']
        return data
    
    def _get_data(self, cr, uid, ids, field_name, value, arg, context={}):
        res = {}

        if self.STORAGE_TYPE == 'file':
            for each in ids:
                res[each] = self.get_origin_file_data(cr, uid, each)

        if self.STORAGE_TYPE == 'db':
            for each in ids:
                res[each] = self.get_origin_db_data(cr, uid, each)
        
        return res


    def save_data_file(self, cr, uid, ids, value, context={}):
        file = self.browse(cr, uid, ids, context=context)

        base_dir = os.path.join(self.MEDIA_PATH, self.DIRNAME,)

        dirname, filename = save_file(value, file.extention, base_dir)

        self.write(cr, uid, ids, {'name': os.path.join(dirname, filename)},
                   context=context)

    def save_data_db(self, cr, uid, ids, value, context={}):
        file = self.browse(cr, uid, ids, context=context)
        dirname, filename = gen_name_dirname_filename(file.extention)

        self.write(cr, uid, ids, {
                'name': os.path.join(dirname, filename),
                'data': value
            }, context=context)
        
    
    def _save_data(self, cr, uid, ids, field_name, value, arg, context={}):
        # TODO: Space does'n make sense.
        # When you edit an image the value is like ??.?? KB,
        # while you expect base64 buffer.
        if ' ' in value:
            return

        if self.STORAGE_TYPE == 'file':
            self.save_data_file(cr, uid, ids, value, context)

        if self.STORAGE_TYPE == 'db':
            self.save_data_db(cr, uid, ids, value, context)
    
    def _get_url(self, cr, uid, ids, field_name, arg, context):
        result = {}
        
        for file in self.browse(cr, uid, ids, context=context):
            result[file.id] = u'%s%s/%s' % (BASE_URL, self.DIRNAME, file.name)
        
        return result
    
    _columns = {
        'file': fields.function(_get_data,
                                fnct_inv=_save_data,
                                method=True,
                                type='binary',
                                string='File'),
        'name': fields.char('File path', size=30),
        'url': fields.function(_get_url,
                               type='char', method=True,
                               string=u'File url'),
        'comment': fields.text('Сommentary'),
        'extention': fields.char('Extention', size=10),
        'data': fields.binary('Data')
    }

    def get_data(self, cr, uid, name, context=None):
        ids = self.search(cr, uid, [('name','=',name)], limit=1,context=context)
        data = ''
        if ids:
            each = self.read(cr, uid, ids[0], ['file'])
            if each['file']:
                data = each['file']
        return data


    def unlink(self, cr, uid, ids, context=None):
        if self.STORAGE_TYPE == 'file':
            # remove file
            for r in self.browse(cr, uid, ids, context=context):
                filename = os.path.join(self.MEDIA_PATH, self.DIRNAME, r.name)
                if os.path.exists(filename):
                    os.unlink(filename)
        res = super(web_gallery_base, self).unlink(cr, uid, ids,
                                                                context=context)
        return res
    
# Categories go here.

class web_gallery_video_category(osv.osv):
    _name = 'web.gallery.video.category'
    _description = 'Video categories'
    _order = 'name'

    _columns = {
        'name': fields.char('Name', required=True, size=100),
    }

web_gallery_video_category()


class web_gallery_image_category(osv.osv):
    _name = 'web.gallery.image.category'
    _description = 'Image categories'
    _order = 'name'

    _columns = {
        'name': fields.char('Name', required=True, size=100),
    }

web_gallery_image_category()


class web_gallery_doc_category(osv.osv):
    _name = 'web.gallery.doc.category'
    _description = 'Document categories'
    _order = 'name'

    _columns = {
        'name': fields.char('Name', required=True, size=100),
    }

web_gallery_doc_category()


class web_gallery_images(web_gallery_base):
    DIRNAME = 'images'
    _name = "web.gallery.images"
    
    def __init__(self, pool, cr):
        self._columns['category'] = \
                     fields.many2one('web.gallery.image.category', 'Category')
        super(web_gallery_images, self).__init__(pool, cr)

    def get_web_config_data(self, cr, uid):
        config_data = get_config_data(cr, uid, self.pool)
        res_data = {}
        for name,value in config_data.items():
            if name.startswith('web_'):
                res_data[name] = value
        return res_data

web_gallery_images()


class web_gallery_videos(web_gallery_base):
    DIRNAME = 'videos'
    _name = 'web.gallery.videos'
    
    def __init__(self, pool, cr):
        self._columns['category'] = \
                     fields.many2one('web.gallery.video.category', 'Category')
        super(web_gallery_videos, self).__init__(pool, cr)

web_gallery_videos()


class web_gallery_docs(web_gallery_base):
    DIRNAME = 'docs'
    _name = 'web.gallery.docs'
    
    def __init__(self, pool, cr):
        self._columns['category'] = \
                       fields.many2one('web.gallery.doc.category', 'Category')
        super(web_gallery_docs, self).__init__(pool, cr)

web_gallery_docs()

class web_gallery_config(osv.osv_memory):
    _name = 'web.gallery.config'
    _inherit = 'res.config'

    _columns = {
        'name': fields.char('Name', size=64),
        'type_file_storage': fields.selection([
            ('db', 'Store files in database'),
            ('file', 'Store files at file system')
        ], 'Storage', required=True, help="Database or local file system"),

        'directory_storage': fields.text('Directory for storing files'),
        'web_cache_enabled': fields.boolean('Cache enabled'),
        'web_cache_dir': fields.text('Directory for cache files'),
        'web_update_config_ttl': fields.integer('Time to next update of settings '
                                                                    '(seconds)')
    }

    _defaults = {
        'type_file_storage': lambda obj, cr, uid, context: get_config_data(cr,
                                  uid, obj.pool).get('type_file_storage', 'db'),
        'directory_storage': lambda obj, cr, uid, context: get_config_data(cr,
                                  uid, obj.pool).get('directory_storage', None),
        'web_cache_enabled': lambda obj, cr, uid, context: get_config_data(cr,
                                 uid, obj.pool).get('web_cache_enabled', False),
        'web_cache_dir': lambda obj, cr, uid, context: get_config_data(cr,
                                      uid, obj.pool).get('web_cache_dir', None),
        'web_update_config_ttl':lambda obj, cr, uid, context:get_config_data(cr,
                               uid, obj.pool).get('web_update_config_ttl', 300),
    }

    def execute(self, cr, uid, ids, context=None):
        models = ('web.gallery.images',
                  'web.gallery.videos',
                  'web.gallery.docs')
        conf_models = [models[0]]
        ir_values_obj = self.pool.get('ir.values')

        for r in self.browse(cr, uid, ids, context=context):
            if r.type_file_storage == 'file':
                if not r.directory_storage or \
                      (r.directory_storage and not r.directory_storage.strip()):
                    raise osv.except_osv ('ERROR',
                                               'The directory is not specified')
                elif not os.path.exists(r.directory_storage):
                    try:
                        os.makedirs(r.directory_storage)
                    except Exception as e:
                        raise osv.except_osv ('ERROR', str(e))
            if r.web_cache_enabled:
                if not r.web_cache_dir or \
                      (r.web_cache_dir and not r.web_cache_dir.strip()):
                    raise osv.except_osv ('ERROR',
                                               'The directory is not specified')
            
            ir_values_obj.set(cr, uid, 'default', False, 'directory_storage',
                                               conf_models, r.directory_storage)
            ir_values_obj.set(cr, uid, 'default', False, 'type_file_storage',
                                               conf_models, r.type_file_storage)
            ir_values_obj.set(cr, uid, 'default', False, 'web_cache_enabled',
                                               conf_models, r.web_cache_enabled)
            ir_values_obj.set(cr, uid, 'default', False, 'web_cache_dir',
                                                   conf_models, r.web_cache_dir)
            ir_values_obj.set(cr, uid, 'default', False,'web_update_config_ttl',
                                           conf_models, r.web_update_config_ttl)
        for model in models:
            self.pool.get(model).set_config_data(self.pool, cr, uid)

web_gallery_config()
