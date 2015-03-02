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

from openerp.osv import osv, fields

class gallery_images(osv.osv):
    
    _name = "web.gallery.images"
    _inherit = "web.gallery.images"
    
    _columns = {
        'product_id': fields.many2one('product.product', "Product")
    }

gallery_images()


class gallery_docs(osv.osv):
    
    _name = "web.gallery.docs"
    _inherit = "web.gallery.docs"
    
    _columns = {
        'product_id': fields.many2one('product.product', "Product")

    }

gallery_docs()


class gallery_videos(osv.osv):

    _name = "web.gallery.videos"
    _inherit = "web.gallery.videos"

    _columns = {
        'product_id': fields.many2one('product.product', "Product")

    }

gallery_videos()


class product_product(osv.osv):
    _name = "product.product"
    _inherit = "product.product"

    _columns = {
        # galleries
        'web_gallery_image_ids': fields.one2many('web.gallery.images',
                                     'product_id',
                                     'Images'),

        'web_gallery_doc_ids': fields.one2many('web.gallery.docs',
                                   'product_id',
                                   'Documents'),

        'web_gallery_video_ids': fields.one2many('web.gallery.videos',
                                   'product_id',
                                   'Videos'),
    }

product_product()
