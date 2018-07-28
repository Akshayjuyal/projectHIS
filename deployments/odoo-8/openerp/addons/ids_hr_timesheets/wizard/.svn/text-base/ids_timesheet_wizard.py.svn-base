#-*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
from openerp import SUPERUSER_ID, api
import time
import calendar
from datetime import date
from datetime import datetime
from datetime import timedelta as td
from dateutil import relativedelta
import os
from dateutil.relativedelta import relativedelta
from openerp import api, tools
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp.tools.safe_eval import safe_eval as eval

from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
import StringIO
import base64
import csv

class ids_timesheet_wizard(osv.osv):
    _name = 'ids.timesheet.wizard'
    
    _columns = {
                'name':fields.char('Name'),
#                 'filter':fields.selection([('D','Department Wise'),('L','Location Wise'),('DI','Division Wise'),('E','Employee Wise')],'Filter' ),
                'filename': fields.char('Filename', size = 64, readonly=True),
                'date_from':fields.date('Date From'),
                'date_to':fields.date('Date To'),
                'filedata': fields.binary('File1', readonly=True),
                'filename1': fields.char('Filename1', size = 64, readonly=True),
                'filedata1': fields.binary('File2', readonly=True),
                'user':fields.many2one('res.users','USER'),
                'user_company':fields.many2one('res.company','Company',required=1,default=lambda self: self.env['res.company'].browse(self.env['res.company']._company_default_get('salary.register.wizard'))),
                'timesheet_line':fields.one2many('ids.timesheet','name','Details')

                                
                }
    _defaults = {
        'user': lambda self, cr, uid, ctx: uid,

    }
    
    def print_timesheet_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        for date in self.browse(cr,uid,ids,context=context):
            datefrom=datetime.strptime(date.date_from,"%Y-%m-%d")
            dateto=datetime.strptime(date.date_to,"%Y-%m-%d")
        cr.execute("truncate ids_timesheet"); 
        employee_obj = self.pool.get('hr.employee')             
        for emp_id in employee_obj.search(cr, uid, [('working_status','!=','exit'),('company_id','=',date.user_company.id)]):
            for emp_data in employee_obj.browse(cr, uid, emp_id, context=None):
                name=emp_data.name_related
                emp_code=emp_data.emp_code
                user_id=emp_data.user_id.id
                cr.execute("select id from hr_employee where id=(select id from resource_resource where user_id=%s)"%uid);
                empid = cr.fetchone()
                emp_level = employee_obj.search(cr, uid, [('parent_id', '=', empid)], context=context)
                if emp_level:
                    if empid:
                        emp_level.extend((empid))
                if not emp_level:
                    uid = 1
                    
                emp_second_level = employee_obj.search(cr, uid, [('parent_id', '=', emp_level)], context=context)
                emp_level.extend((emp_second_level)) 
                emp_third_level = employee_obj.search(cr, uid, [('parent_id', '=', emp_second_level)], context=context)
                emp_level.extend((emp_third_level))
                for timesheet_ids in self.pool.get('hr_timesheet_sheet.sheet').search(cr, uid, [('state','=','done'),('date_from','>=',datefrom),('date_from','<=',dateto),('employee_id','=',emp_data.id)]):
                    for timesheet_data in self.pool.get('hr_timesheet_sheet.sheet').browse(cr, uid, timesheet_ids, context=None):
                        for data_id in self.pool.get('hr.analytic.timesheet').search(cr, uid, [('sheet_id','=',timesheet_data.id)]):
                            for data in self.pool.get('hr.analytic.timesheet').browse(cr, uid, data_id, context=None):
                                date=data.date
                                description=data.name
                                account=data.account_id.name
                                project_category=data.project_category_id.name
                                hour_type=data.hour_type_id.name
                                duration=data.unit_amount
                                cr.execute('Insert into ids_timesheet (emp_code,emp_name,date,description,project,tasks,hour_type,duration)Values (%s,%s,%s,%s,%s,%s,%s,%s)',(emp_code,name,date,description,account,project_category,hour_type,duration));
               
        cr.execute('SELECT emp_code,emp_name,date,description,project,tasks,hour_type,duration from ids_timesheet');
        res = cr.fetchall()
        fp = StringIO.StringIO()
        writer = csv.writer(fp)
        writer.writerow([ i[0] for i in cr.description ])
        for data in res:
            row = []
            for d in data:
                if isinstance(d, basestring):
                    d = d.replace('\n',' ').replace('\t',' ')
                    try:
                        d = d.encode('utf-8')
                    except:
                        pass
                if d is False: d = None
                row.append(d)
            writer.writerow(row)
        fp.seek(0)
        data = fp.read()
        fp.close()
        out=base64.encodestring(data)
        file_name = 'timesheet_report.csv'
        self.write(cr, uid, ids, {'filedata':out, 'filename':file_name}, context=context)
        return {
                    'name':'Timesheet Report',
                    'res_model':'ids.timesheet.wizard',
                    'type':'ir.actions.act_window',
                    'view_type':'form',
                    'view_mode':'form',
                    'nodestroy': True,
                    'context': context,
                    'res_id': ids and ids[0],
                    } 
#        """
#         To get the date and print the report
#         @param self: The object pointer.
#         @param cr: A database cursor
#         @param uid: ID of the user currently logged in
#         @param context: A standard dictionary
#         @return: return report
#        """
class ids_timesheet(osv.Model):
    _name = 'ids.timesheet'
    
    _columns = {
                'name':fields.many2one('ids.timesheet.wizard','Name'),
                'date': fields.date('Date'),
                'description':fields.char('Description'),
                'project':fields.char('Project'),
                'tasks':fields.char('Tasks'),
                'hour_type':fields.char('Hour Type'),
                'duration':fields.char('Duration'),
                'emp_code':fields.char('Employee Code'),
                'emp_name':fields.char('Employee Name'),
                }
    