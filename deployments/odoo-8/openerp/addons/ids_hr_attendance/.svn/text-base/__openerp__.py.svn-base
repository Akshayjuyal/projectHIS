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
    'name': 'IDS HR Attendances',
    'version': '1.1',
    'category': 'Human Resources',
    'description': """
This module aims to manage employee's attendances.
==================================================

Keeps account of the attendances of the employees on the basis of the
actions(Sign in/Sign out) performed by them.
       """,
    'author': 'IDS',
    'images': [],
    'depends': ['hr','hr_attendance','hr_timesheet_sheet'],
    'data': [
        'view/ids_hr_attendance_view.xml',
        'view/schedule.xml',
        'wizard/attendance_report.xml',
        'security/hr_attendance_security.xml',
        'security/ir.model.access.csv',
        'ids_attendance_report.xml'                
    ],
    'installable': True,
    'auto_install': False,    
    
}
