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

from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from openerp import netsvc
from openerp.osv import fields, osv
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools.translate import _
from openerp import SUPERUSER_ID

class hr_evaluation(osv.Model):
    
    
    _inherit = 'hr_evaluation.evaluation'
    _name = 'hr_evaluation.evaluation'    
    _description = 'Employee Appraisals'
    
    
    _columns = {        
        'emp_code': fields.related('employee_id', 'emp_code', type='char',
                                            relation='hr.employee', string='Employee Code',
                                            store=True, readonly=True),        
        'job_id': fields.many2one('hr.job', 'Current Position', readonly=True,
                               states={'draft': [('readonly',False)]}),
        'department_id': fields.related('employee_id', 'department_id', type='many2one',
                                            relation='hr.department', string='Department',
                                            store=True, readonly=True),
	    'joining_date': fields.related('employee_id', 'joining_date', type='date',
                                            relation='hr.employee', string='Joining Date',readonly=True),
        'note_hod': fields.text('HOD Notes', required=False, readonly=True, states={'progress': [('required',True)],'progress': [('readonly',False)]}, write=['ids_emp.group_business_head']),
        'rating': fields.selection([
            ('0','Significantly bellow expectations'),
            ('1','Did not meet expectations'),
            ('2','Meet expectations'),
            ('3','Exceeds expectations'),
            ('4','Significantly exceeds expectations'),
        ], "Appreciation", help="This is the appreciation on which the evaluation is summarized.", write=['ids_emp.group_business_head']),
    }
    
    _rec_name = 'emp_code'    
    
    def onchange_employee_id(self, cr, uid, ids, employee_id, context=None):
        """Get fields associated with onchange of employee_id from hr.employee. """
        vals = {}
        vals['plan_id'] = False
        if employee_id:
            employee_obj = self.pool.get('hr.employee')
            for employee in employee_obj.browse(cr, uid, [employee_id], context=context):
                if employee and employee.evaluation_plan_id and employee.evaluation_plan_id.id:
                    vals.update({'plan_id': employee.evaluation_plan_id.id})
		vals.update({'job_id': employee.job_id.id, 'department_id': employee.department_id.id, 'emp_code': employee.emp_code, 'joining_date': employee.joining_date})
        return {'value': vals}
    
