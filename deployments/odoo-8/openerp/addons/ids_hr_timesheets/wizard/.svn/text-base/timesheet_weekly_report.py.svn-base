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

class timesheet_weekly_wizard(osv.osv):
    _name = 'timesheet.weekly.wizard'
    
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
                'user_company':fields.many2one('res.company','USER Company',default=lambda self: self.env['res.company'].browse(self.env['res.company']._company_default_get('salary.register.wizard'))),
                'timesheet_line':fields.one2many('timesheet.weekly','name','Details')

                                
                }
    _defaults = {
        'user': lambda self, cr, uid, ctx: uid,

    }
    
    def print_report(self, cr, uid, ids, context=None):
        total=0
        data1=0
        value=0
        if context is None:
            context = {}
        for date in self.browse(cr,uid,ids,context=context):
            date_from=date.date_from
            datefrom=datetime.strptime(date_from,"%Y-%m-%d")
            week_from=datetime.date(datefrom).isocalendar()[1]
            week_no=week_from-1
            date_to=date.date_to
        cr.execute("truncate timesheet_weekly"); 
        employee_obj = self.pool.get('hr.employee')             
        for emp_id in self.pool.get('hr.employee').search(cr, uid, [('working_status','!=','exit'),('company_id','=',1)]):
            for emp_data in self.pool.get('hr.employee').browse(cr, uid, emp_id, context=None):
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
                weeks=0
                for data_id in self.pool.get('hr.analytic.timesheet').search(cr, uid, [('user_id','=',user_id)]):
                    for data in self.pool.get('hr.analytic.timesheet').browse(cr, uid, data_id, context=None):
                        date=data.date
                        dateget=datetime.strptime(date,"%Y-%m-%d")
                        weeks=datetime.date(dateget).isocalendar()[1]
                        a1=cr.execute("select a.date,a.user_id,sum(a.unit_amount) as total from  account_analytic_line as a inner join hr_analytic_timesheet h on h.line_id=a.id where a.user_id=%s and extract(week from a.date)=%s group by a.user_id,a.date"%(user_id,week_from))
                        res2=cr.fetchall()
                        total = [float(i[2]) for i in res2]
                        value=sum(total)
                cr.execute('Insert into timesheet_weekly (emp_code,emp_name,week,total_hours)Values (%s,%s,%s,%s)',(emp_code,name,week_no,value));
           
       
        cr.execute('SELECT emp_code,emp_name,week,total_hours from timesheet_weekly');
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
        file_name = 'timesheet_weekly.csv'
        self.write(cr, uid, ids, {'filedata':out, 'filename':file_name}, context=context)
        return {
                    'name':'Timesheet Weekly',
                    'res_model':'timesheet.weekly.wizard',
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
class timesheet_weekly(osv.Model):
    _name = 'timesheet.weekly'
    
    _columns = {
                'name':fields.many2one('timesheet.weekly.wizard','Name'),
                'emp_code':fields.char('Employee Code'),
                'emp_name':fields.char('Employee Name'),
                'total_hours':fields.char('Total Hours'),
                'week':fields.char('Week')
                }
    