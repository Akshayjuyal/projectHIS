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

from openerp.osv import osv,fields
import time
from openerp import netsvc

class ids_hr_employee_background_detail(osv.osv):
    _name = 'ids.hr.employee.background.detail'
    _description = "Employee Background Detail"           
    _columns = {
                'police_record':fields.boolean('Have you had any police records?'),
                'police_record_desc':fields.char('If yes, give details: ', size=200),
                'convicted_court':fields.boolean('Have you ever convicted by court of law?'),
                'convicted_court_desc':fields.char('If yes, give details: ', size=200),
                'work_shifts':fields.boolean('Are you willing to work in shifts?'),
                'applied_before':fields.boolean('Have you applied to IDS before?'),
                'applied_before_date':fields.date('If yes, date of application: '),
                'applied_before_test':fields.boolean('Were you called for Test? '),
                'applied_before_interview':fields.boolean('Were you selected for Interview? '),
                'applied_before_offer':fields.boolean('Were you made an Offer? '),
                'know_anyone_ids':fields.boolean('Do you know anyone working with IDS?'),
                'background_known_ids':fields.one2many('ids.hr.employee.background.known','background_detail_id', 'Known Details'),
               }
ids_hr_employee_background_detail()    
class ids_hr_employee_background_known(osv.osv):
    
    _name = 'ids.hr.employee.background.known'
    _description = "Employee Known People"               
    _columns = {
                'name':fields.char('Name', size=100, required=True),
                'name_test':fields.char('Name test', size=100, required=True),
                'designation':fields.char('Designation', size=100, required=True),
                'relationship':fields.char('Relationship', size=100, required=True),
                'background_detail_id':fields.many2one('ids.hr.employee.background.detail', 'Background Detail')
                }
ids_hr_employee_background_known()
