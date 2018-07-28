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
    'name': 'IDS Employee Exit',
    'version': '1.0',
    'category': 'Human Resource',
    'description': """
Employee Exit/Full amp&; Final
======================================

    """,
    'author':'IDS Infotech Ltd.',
    'website':'http://idsil.com',
    'depends': [
        'hr','ids_employee_separation','hr_holidays'
    ],
    'init_xml': [
    ],
    'update_xml': [ 
        'view/ids_employee_exit_view.xml',
        'view/exit_sequence_view.xml', 
        'security/ir.model.access.csv',
        'security/employee_exit_security.xml',           
    ],
    'test': [
    ],
    'demo_xml': [
    ],
    'installable': True,
    'active': False,
}
