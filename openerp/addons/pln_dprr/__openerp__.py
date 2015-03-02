# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'DPRR Analyze',
    'version': '0.1',
    'author': 'Adista N. Robbi',
    'website': 'http://www.bizoftenterprise.com',
    'summary': 'Analyze Piutang Ragu-ragu of PLN Customer',
    'description': """
DPRR Analyze
============

Mari menghitung daftar piutang ragu-ragu. 
    """,
    'images': [],
    'depends': [
        'base', 'hr'
    ], 
    'data': [
        'hr_employee_view.xml',
        'pln_dpiutangrr_view.xml',
        'pln_docprr_view.xml',   
        'res_partner_view.xml', 
        'security/base_plndprr_security.xml', 
    ], 
    'demo': [],
    'test': [],
    'css': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}