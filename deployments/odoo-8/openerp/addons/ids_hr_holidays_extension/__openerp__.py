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
    'name': 'IDS HR Holidays Extension',
    'version': '1.0',
    'category': 'Generic Modules/Human Resources',
    'description': """
Extended Capabilities for HR Holidays (Leaves)
==============================================

    * When calculating the number of leave days take into account the employee's schedule and
      public holidays
    * The 'Need Action' mechanism assumes the HR Manager approves leave requests
    * Rename 'Leave Requests' menu item to 'My Leaves' (which is closer to its intent)
    * Add a new menu item: All Leave Requests
    * New way of entering leaves based on the number of days requested, rather
      than by specifying a start and end date. You tell it how many days to
      grant and it calculates the start and end dates based on the employee's schedule.
    * Allow a manager to approve the leave requests of subordinates (manager must be
      immediate superior of employee or manager of employee's department and have
      leave approval rights)
    """,
    'author':'IDS',
    'website':'',
    'depends': [
        'hr_holidays',
        'ids_hr_public_holidays',        
    ],
    'init_xml': [
    ],
    'update_xml': [
        'view/hr_holidays_view.xml',
        'security/user_groups.xml',        
        'security/ir_rule.xml',
#         'security/ir.model.access.csv',
        'workflow/hr_holidays_workflow.xml'
    ],
    'test': [
    ],
    'demo_xml': [
    ],
    'installable': True,
    'active': False,
}
