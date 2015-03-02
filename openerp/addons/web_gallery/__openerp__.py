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

{
    'name': 'Web product gallery',
    'version': '0.8',
    'category': 'Others',
    'description': """
Web product gallery module allows to attach videos, images and documents to any product in a system.

Web product gallery takes place thanks to beautiful tools, such as:

- JW Player (http://developer.longtailvideo.com/trac)
- Tiny Carousel jQuery plugin (http://www.baijs.nl/tinycarousel)
- FancyBox (http://fancybox.net/)

After module installation you will be prompted to configure gallery behavior. Wizard configuration includes storage type (database side or file system) and caching settings.

You'll find Gallery tab at the product page (please, see the attached picture).

Optionally you may set category for any type of media content. Please, follow: Sales -> Configuration -> Product -> Gallery settings. It's not so far as It looks like :)
""",
    'author': 'Infosreda LLC',
    'website': 'http://infosreda.com/',
    'depends': ['base', 'product'],
    'init_xml': [],
    'update_xml': [
        'security/web_gallery_security.xml',
        'security/ir.model.access.csv',
        'web_gallery_view.xml',
        'product_gallery_view.xml',
        ],
    'installable': True,
    'active': False,
    'web': True,
    'images': ['images/g1.png', 'images/g2.png', 'images/g3.png'],
    'css': ['static/src/css/carousel.css'],
    'js': [
        'static/src/js/jquery.tinycarousel.js',
        'static/src/js/jwplayer.js',
        'static/src/js/web_gallery.js',
    ],
}
