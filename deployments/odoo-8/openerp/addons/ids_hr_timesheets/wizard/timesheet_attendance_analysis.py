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
import math

class timesheet_attendance_analysis(osv.osv):
    _name = 'timesheet.attendance.analysis'

    _columns = {
                'name':fields.char('Name'),
#                 'filter':fields.selection([('D','Department Wise'),('L','Location Wise'),('DI','Division Wise'),('E','Employee Wise')],'Filter' ),
                'filename': fields.char('Filename', size = 64, readonly=True),
                'date_from':fields.date('Date From',required=True),
                'date_to':fields.date('Date To',required=True),
                'filedata': fields.binary('File1', readonly=True),
                'filename1': fields.char('Filename1', size = 64, readonly=True),
                'filedata1': fields.binary('File2', readonly=True),
                'user':fields.many2one('res.users','USER'),
                'message':fields.text('Message'),
                'flag':fields.boolean('Flag'),
                'user_company':fields.many2one('res.company','USER Company',default=lambda self: self.env['res.company'].browse(self.env['res.company']._company_default_get('salary.register.wizard'))),
                #'analysis_line':fields.one2many('timesheet.analysis.line','name','Details')

                                
                }
    _defaults = {
        'user': lambda self, cr, uid, ctx: uid,

    }
    
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = self.browse(cr,uid,ids,context=context)
        date_from=datetime.strptime(data.date_from,"%Y-%m-%d")
        date_to=datetime.strptime(data.date_to,"%Y-%m-%d")
        company_id= data.user_company.id
        id = data.id
        cr.execute("delete from timesheet_analysis_line"); 
        for timesheet in self.pool.get('hr_timesheet_sheet.sheet').search(cr, uid, [('date_from','>=',date_from),('date_to','<=',date_to),('company_id','=',company_id)]):
            for timesheet_data in self.pool.get('hr_timesheet_sheet.sheet').browse(cr, uid, timesheet, context=None):
                emp_id=timesheet_data.employee_id.id
                id = timesheet_data.id
                emp_name=timesheet_data.employee_id.name_related
                emp_code=timesheet_data.employee_id.emp_code
                date = timesheet_data.date_from
                total_attendance = round(timesheet_data.total_attendance,2)
                total_timesheet = round(timesheet_data.total_timesheet,2)
                timeshee_id = timesheet_data.id
                total_hours = 0.0
                total_hours_r = 0.0 
                total_hours_nb = 0.0
                total_hours_nb_r = 0.0
                utilization = 0.0
                for line in self.pool.get('hr.analytic.timesheet').search(cr, uid, [('sheet_id','=',timeshee_id),('hour_type_id','=',1)]):
                    for line_data in self.pool.get('hr.analytic.timesheet').browse(cr, uid, line, context=None):
                        total_hours += line_data.unit_amount
                        total_hours_r = round(total_hours,2)
                for line1 in self.pool.get('hr.analytic.timesheet').search(cr, uid, [('sheet_id','=',timeshee_id),('hour_type_id','=',2)]):
                    for line_data1 in self.pool.get('hr.analytic.timesheet').browse(cr, uid, line1, context=None):
                        total_hours_nb += line_data1.unit_amount
                        total_hours_nb_r =  round(total_hours_nb,2)
                if total_timesheet>0:
                    utilization=math.ceil(round((total_hours/total_timesheet)*100,2))
                if utilization>100:
                    utilization=100.0
                cr.execute('Insert into timesheet_analysis_line(date,emp_code,employee_id,emp_name,name,total_attendance,total_timesheet,total_billable,total_nonbillable,utilization)Values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',(date,emp_code,emp_id,emp_name,id,total_attendance,total_timesheet,total_hours_r,total_hours_nb_r,utilization));
                cr.execute("select id from timesheet_analysis_line where employee_id=%s and date=%s",(emp_id,date));
                res=cr.fetchall()
                data3=0
                list3 = [int(i[0]) for i in res]
                if len(list3) <> 0:
                    data3 = list3[0]
                    print"data3======",data3,id
                cr.execute("update hr_analytic_timesheet set utl_rpt_id=%s WHERE sheet_id=%s",(data3,id));
                cr.execute("select distinct(employee_id) from timesheet_analysis_line");
                res=cr.fetchall()
                data=0.0
                data1=0.0
                data2=0.0
                final_data=0.0
                for values in res:
                    cr.execute("select count(*) from timesheet_analysis_line where employee_id=%s"%values);
                    res=cr.fetchall()
                    list2 = [int(i[0]) for i in res]
                    if len(list2) <> 0:
                        data2 = list2[0]
                    cr.execute("select id from timesheet_analysis_line where employee_id=%s order by id limit 1"%values);
                    res=cr.fetchall()
                    list1 = [int(i[0]) for i in res]
                    if len(list1) <> 0:
                        data1 = list1[0]
                    cr.execute("select sum(utilization::float) from timesheet_analysis_line where employee_id=%s"%values);
                    res=cr.fetchall()
                    list = [int(i[0]) for i in res]
                    if len(list) <> 0:
                        data = list[0]
                    final_data=data/data2
                    name='Report'
                    cr.execute("update timesheet_analysis_line set utilization_avg=%s,name=%s WHERE id=%s",(final_data,name,data1));
        self.write(cr, uid, ids , {'message': 'Report Generated successfully. Please click on View Report.','flag':True,'name':'Report'}, context=context)              
#         cr.execute('SELECT date,emp_code,emp_name,total_attendance,total_timesheet,total_billable,total_nonbillable,utilization from timesheet_analysis_line');
#         res = cr.fetchall()
#         fp = StringIO.StringIO()
#         writer = csv.writer(fp)
#         writer.writerow([ i[0] for i in cr.description ])
#         for data in res:
#             row = []
#             for d in data:
#                 if isinstance(d, basestring):
#                     d = d.replace('\n',' ').replace('\t',' ')
#                     try:
#                         d = d.encode('utf-8')
#                     except:
#                         pass
#                 if d is False: d = None
#                 row.append(d)
#             writer.writerow(row)
#         fp.seek(0)
#         data = fp.read()
#         fp.close()
#         out=base64.encodestring(data)
#         file_name = 'timesheet_analysis.csv'
#         self.write(cr, uid, ids, {'filedata':out, 'filename':file_name}, context=context)
        return {
                    'name':'Timesheet Analysis',
                    'res_model':'timesheet.attendance.analysis',
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
class timesheet_analysis_line(osv.Model):
    _name = 'timesheet.analysis.line'
    
    _columns = {
                'name':fields.char('Name'),
                'date':fields.char('Date'),
                'emp_code':fields.char('Employee Code'),
                'emp_name':fields.char('Employee Name'),
                'employee_id':fields.many2one('hr.employee','Employee'),
                'total_attendance':fields.float('Total Attendance'),
                'total_timesheet':fields.float('Total Timesheet'),
                'total_billable':fields.float('Total Billable'),
                'total_nonbillable':fields.float('Total Non Billable'),
                'utilization_avg':fields.float('Utilization(Average%)'),
                'utilization':fields.char('Utilization(%)'),
                'timesheet_lines':fields.one2many('hr.analytic.timesheet','utl_rpt_id','Details')
                
                }
    
