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

class attendance_report_wizard(osv.osv):
    _name = 'attendance.report.wizard'
    
    _columns = {
                'name':fields.char('Name'),
                'month':fields.selection([('1','January'),('2','February'),('3','March'),
                                          ('4','April'),('5','May'),('6','June'),('7','July'),
                                          ('8','August'),('9','September'),('10','October'),('11','November'),
                                          ('12','December')],'Month' ),
                'year':fields.selection([(str(num), str(num)) for num in range((time.localtime().tm_year), (time.localtime().tm_year)-2, -1)],'Year' ),
                'company_id':fields.many2one('res.company','Company',required=True),
                'division_id':fields.many2one('division','Division'),
                'department_id':fields.many2one('hr.department','Department'),
#                 'filter':fields.selection([('D','Department Wise'),('L','Location Wise'),('DI','Division Wise'),('E','Employee Wise')],'Filter' ),
                'filename': fields.char('Filename', size = 64, readonly=True),
                'filedata': fields.binary('File1', readonly=True),
                'filename1': fields.char('Filename1', size = 64, readonly=True),
                'filedata1': fields.binary('File2', readonly=True),
                'user':fields.many2one('res.users','USER'),
                'user_company':fields.many2one('res.company','USER Company',default=lambda self: self.env['res.company'].browse(self.env['res.company']._company_default_get('salary.register.wizard'))),
                'mr_register_line':fields.one2many('muster.roll.register','name','Details')

                                
                }
    _defaults = {
        'user': lambda self, cr, uid, ctx: uid,

    }
    
    def print_report(self, cr, uid, ids, context=None):
        #raise osv.except_osv(_('Warning!'), _('Report is under progress please wait for some times!'))
        emp_obj=self.pool.get('hr.employee')
        if context is None:
            context = {}
        cr.execute("truncate muster_roll_register");
        for attendance in self.browse(cr,uid,ids,context=context):
            pre_month=pre_year=0
            month = int(attendance.month)
            year = int(attendance.year)
            id=attendance.id
            if month==1:
                pre_month=12
                pre_year=int(attendance.year)-1
            else:
                pre_month=int(month)-1
                pre_year=int(attendance.year)
            period_start=(date.today().replace(day=25,month=pre_month,year=pre_year))
            period_end=(date.today().replace(day=24,month=month,year=year))
            days_in_mth=calendar.monthrange(year,month)[1]
            days_in_last_mth=calendar.monthrange(pre_year,pre_month)[1]
            last_date=(date.today().replace(day=days_in_mth,month=month,year=year))
            first_date=(date.today().replace(day=1,month=month,year=year))
            #print"period======",period_start,period_end
            #print"month======,year====",month,year
            emp=0
            if attendance.department_id:
                emp=emp_obj.search(cr,uid,[('working_status','<>','exit'),('company_id','=',attendance.company_id.id),('department_id','=',attendance.department_id.id),('emp_code','<>',False)])
            if not attendance.department_id:
                emp=emp_obj.search(cr,uid,[('working_status','<>','exit'),('company_id','=',attendance.company_id.id),('division','=',attendance.division_id.id),('emp_code','<>',False)])
            for emp_id in emp_obj.browse(cr,uid,emp,context=None):
                employee_id = emp_id.id
                emp_code=emp_id.emp_code
                diff=0
                pre_month_days=cur_month_days=diff=0
                if month==1:
                    pre_month_days=calendar.monthrange(pre_year,pre_month)[1]
                    cur_month_days=calendar.monthrange(year,month)[1]
                    diff=cur_month_days-pre_month_days
                else:
                    pre_month_days=calendar.monthrange(year,int(month)-1)[1]
                    cur_month_days=calendar.monthrange(year,month)[1]
                    #updated on 27 mar-17
                    diff=cur_month_days-31
                    #####3
                difference=0
                joining_date=datetime.strptime(emp_id.joining_date, '%Y-%m-%d').date()
                if joining_date >= period_start and joining_date<=period_end:
                    print"joining_date",joining_date
                    joining_date1=(date.today().replace(day=joining_date.day,month=joining_date.month,year=joining_date.year))
                    difference=(joining_date1 - period_start).days
                    print"difference===",difference
                    if month==3:
                        difference=difference+3
                    if month in [5,7,10,12]:
                        difference=difference+1
                cr.execute('Insert into muster_roll_register (emp_code,emp_name,name,"DY_DIFF","IS_NIGHT","DEPT_CODE","DATE")Values (%s,%s,%s,%s,0,113,%s)',(emp_id.emp_code,emp_id.name,id,diff,last_date));
                value_new='N/A'
                if month==3:
                    cr.execute('update muster_roll_register set "DAY29"=%s where emp_code=%s',(value_new,emp_code));
                    cr.execute('update muster_roll_register set "DAY30"=%s where emp_code=%s',(value_new,emp_code));
                    cr.execute('update muster_roll_register set "DAY31"=%s where emp_code=%s',(value_new,emp_code));
                if month in [5,7,10,12]:
                    cr.execute('update muster_roll_register set "DAY31"=%s where emp_code=%s',(value_new,emp_code));
                d1 = date(year = pre_year, month = pre_month, day = 25)
                d2 = date(year = year, month = month, day = 24)
                delta = d2 - d1
                for i in range(delta.days + 1):
                    st_date=(d1 + td(days=i)).day
                    wk_day=(d1 + td(days=i)).weekday()
                    #print"date====",st_date,wk_day
                    value1='XTD'
                    value2='D'
                    #cr.execute('update muster_roll_register set "DAY25"=%s',(value1,));
                    if attendance.department_id.use_duty_roster==True:
                        for roster in self.pool.get('hr.roster').search(cr,uid,[('from_date','=',period_start),('to_date','=',period_end),('department_id','=',attendance.department_id.id)]):
                            for roster_data in self.pool.get('hr.roster').browse(cr,uid,roster,context=context):
                                data_id=roster_data.id
                                for roster_line in self.pool.get('hr.roster.line').search(cr,uid,[('employee_id','=',employee_id),('roster_id','=',data_id)]):
                                    for roster_line_data in self.pool.get('hr.roster.line').browse(cr,uid,roster_line,context=context):
                                        day_off=int(roster_line_data.off_day)
                                        extra_off_day=int(roster_line_data.extra_off_day)
                                        if st_date==25 and wk_day==day_off:
                                            cr.execute('update muster_roll_register set "DAY25"=%s where emp_code=%s',(value2,emp_code));
                                        if st_date==26 and wk_day==day_off:
                                            cr.execute('update muster_roll_register set "DAY26"=%s where emp_code=%s',(value2,emp_code));
                                        if st_date==27 and wk_day==day_off:
                                            cr.execute('update muster_roll_register set "DAY27"=%s where emp_code=%s',(value2,emp_code));
                                        if st_date==28 and wk_day==day_off:
                                            cr.execute('update muster_roll_register set "DAY28"=%s where emp_code=%s',(value2,emp_code));
                                        if st_date==29 and wk_day==day_off:
                                            cr.execute('update muster_roll_register set "DAY29"=%s where emp_code=%s',(value2,emp_code));
                                        if st_date==30 and wk_day==day_off:
                                            cr.execute('update muster_roll_register set "DAY30"=%s where emp_code=%s',(value2,emp_code));
                                        if st_date==31 and wk_day==day_off:
                                            cr.execute('update muster_roll_register set "DAY31"=%s where emp_code=%s',(value2,emp_code));
                                        if st_date==1 and wk_day==day_off:
                                            cr.execute('update muster_roll_register set "DAY1"=%s where emp_code=%s',(value2,emp_code));
                                        if st_date==2 and wk_day==day_off:
                                            cr.execute('update muster_roll_register set "DAY2"=%s where emp_code=%s',(value2,emp_code));
                                        if st_date==3 and wk_day==day_off:
                                            cr.execute('update muster_roll_register set "DAY3"=%s where emp_code=%s',(value2,emp_code));
                                        if st_date==4 and wk_day==day_off:
                                            cr.execute('update muster_roll_register set "DAY4"=%s where emp_code=%s',(value2,emp_code));
                                        if st_date==5 and wk_day==day_off:
                                            cr.execute('update muster_roll_register set "DAY5"=%s where emp_code=%s',(value2,emp_code));
                                        if st_date==6 and wk_day==day_off:
                                            cr.execute('update muster_roll_register set "DAY6"=%s where emp_code=%s',(value2,emp_code));
                                        if st_date==7 and wk_day==day_off:
                                            cr.execute('update muster_roll_register set "DAY7"=%s where emp_code=%s',(value2,emp_code));
                                        if st_date==8 and wk_day==day_off:
                                            cr.execute('update muster_roll_register set "DAY8"=%s where emp_code=%s',(value2,emp_code));
                                        if st_date==9 and wk_day==day_off:
                                            cr.execute('update muster_roll_register set "DAY9"=%s where emp_code=%s',(value2,emp_code));
                                        if st_date==10 and wk_day==day_off:
                                            cr.execute('update muster_roll_register set "DAY10"=%s where emp_code=%s',(value2,emp_code));
                                        if st_date==11 and wk_day==day_off:
                                            cr.execute('update muster_roll_register set "DAY11"=%s where emp_code=%s',(value2,emp_code));
                                        if st_date==12 and wk_day==day_off:
                                            cr.execute('update muster_roll_register set "DAY12"=%s where emp_code=%s',(value2,emp_code));
                                        if st_date==13 and wk_day==day_off:
                                            cr.execute('update muster_roll_register set "DAY13"=%s where emp_code=%s',(value2,emp_code));
                                        if st_date==14 and wk_day==day_off:
                                            cr.execute('update muster_roll_register set "DAY14"=%s where emp_code=%s',(value2,emp_code));
                                        if st_date==15 and wk_day==day_off:
                                            cr.execute('update muster_roll_register set "DAY15"=%s where emp_code=%s',(value2,emp_code));
                                        if st_date==16 and wk_day==day_off:
                                            cr.execute('update muster_roll_register set "DAY16"=%s where emp_code=%s',(value2,emp_code));
                                        if st_date==17 and wk_day==day_off:
                                            cr.execute('update muster_roll_register set "DAY17"=%s where emp_code=%s',(value2,emp_code));
                                        if st_date==18 and wk_day==day_off:
                                            cr.execute('update muster_roll_register set "DAY18"=%s where emp_code=%s',(value2,emp_code));
                                        if st_date==19 and wk_day==day_off:
                                            cr.execute('update muster_roll_register set "DAY19"=%s where emp_code=%s',(value2,emp_code));
                                        if st_date==20 and wk_day==day_off:
                                            cr.execute('update muster_roll_register set "DAY20"=%s where emp_code=%s',(value2,emp_code));
                                        if st_date==21 and wk_day==day_off:
                                            cr.execute('update muster_roll_register set "DAY21"=%s where emp_code=%s',(value2,emp_code));
                                        if st_date==22 and wk_day==day_off:
                                            cr.execute('update muster_roll_register set "DAY22"=%s where emp_code=%s',(value2,emp_code));
                                        if st_date==23 and wk_day==day_off:
                                            cr.execute('update muster_roll_register set "DAY23"=%s where emp_code=%s',(value2,emp_code));
                                        if st_date==24 and wk_day==day_off:
                                            cr.execute('update muster_roll_register set "DAY24"=%s where emp_code=%s',(value2,emp_code));
                                        
                                        
                                        if st_date==25 and wk_day==extra_off_day:
                                            cr.execute('update muster_roll_register set "DAY25"=%s where emp_code=%s',(value1,emp_code));
                                        if st_date==26 and wk_day==extra_off_day:
                                            cr.execute('update muster_roll_register set "DAY26"=%s where emp_code=%s',(value1,emp_code));
                                        if st_date==27 and wk_day==extra_off_day:
                                            cr.execute('update muster_roll_register set "DAY27"=%s where emp_code=%s',(value1,emp_code));
                                        if st_date==28 and wk_day==extra_off_day:
                                            cr.execute('update muster_roll_register set "DAY28"=%s where emp_code=%s',(value1,emp_code));
                                        if st_date==29 and wk_day==extra_off_day:
                                            cr.execute('update muster_roll_register set "DAY29"=%s where emp_code=%s',(value1,emp_code));
                                        if st_date==30 and wk_day==extra_off_day:
                                            cr.execute('update muster_roll_register set "DAY30"=%s where emp_code=%s',(value1,emp_code));
                                        if st_date==31 and wk_day==extra_off_day:
                                            cr.execute('update muster_roll_register set "DAY31"=%s where emp_code=%s',(value1,emp_code));
                                        if st_date==1 and wk_day==extra_off_day:
                                            cr.execute('update muster_roll_register set "DAY1"=%s where emp_code=%s',(value1,emp_code));
                                        if st_date==2 and wk_day==extra_off_day:
                                            cr.execute('update muster_roll_register set "DAY2"=%s where emp_code=%s',(value1,emp_code));
                                        if st_date==3 and wk_day==extra_off_day:
                                            cr.execute('update muster_roll_register set "DAY3"=%s where emp_code=%s',(value1,emp_code));
                                        if st_date==4 and wk_day==extra_off_day:
                                            cr.execute('update muster_roll_register set "DAY4"=%s where emp_code=%s',(value1,emp_code));
                                        if st_date==5 and wk_day==extra_off_day:
                                            cr.execute('update muster_roll_register set "DAY5"=%s where emp_code=%s',(value1,emp_code));
                                        if st_date==6 and wk_day==extra_off_day:
                                            cr.execute('update muster_roll_register set "DAY6"=%s where emp_code=%s',(value1,emp_code));
                                        if st_date==7 and wk_day==extra_off_day:
                                            cr.execute('update muster_roll_register set "DAY7"=%s where emp_code=%s',(value1,emp_code));
                                        if st_date==8 and wk_day==extra_off_day:
                                            cr.execute('update muster_roll_register set "DAY8"=%s where emp_code=%s',(value1,emp_code));
                                        if st_date==9 and wk_day==extra_off_day:
                                            cr.execute('update muster_roll_register set "DAY9"=%s where emp_code=%s',(value1,emp_code));
                                        if st_date==10 and wk_day==extra_off_day:
                                            cr.execute('update muster_roll_register set "DAY10"=%s where emp_code=%s',(value1,emp_code));
                                        if st_date==11 and wk_day==extra_off_day:
                                            cr.execute('update muster_roll_register set "DAY11"=%s where emp_code=%s',(value1,emp_code));
                                        if st_date==12 and wk_day==extra_off_day:
                                            cr.execute('update muster_roll_register set "DAY12"=%s where emp_code=%s',(value1,emp_code));
                                        if st_date==13 and wk_day==extra_off_day:
                                            cr.execute('update muster_roll_register set "DAY13"=%s where emp_code=%s',(value1,emp_code));
                                        if st_date==14 and wk_day==extra_off_day:
                                            cr.execute('update muster_roll_register set "DAY14"=%s where emp_code=%s',(value1,emp_code));
                                        if st_date==15 and wk_day==extra_off_day:
                                            cr.execute('update muster_roll_register set "DAY15"=%s where emp_code=%s',(value1,emp_code));
                                        if st_date==16 and wk_day==extra_off_day:
                                            cr.execute('update muster_roll_register set "DAY16"=%s where emp_code=%s',(value1,emp_code));
                                        if st_date==17 and wk_day==extra_off_day:
                                            cr.execute('update muster_roll_register set "DAY17"=%s where emp_code=%s',(value1,emp_code));
                                        if st_date==18 and wk_day==extra_off_day:
                                            cr.execute('update muster_roll_register set "DAY18"=%s where emp_code=%s',(value1,emp_code));
                                        if st_date==19 and wk_day==extra_off_day:
                                            cr.execute('update muster_roll_register set "DAY19"=%s where emp_code=%s',(value1,emp_code));
                                        if st_date==20 and wk_day==extra_off_day:
                                            cr.execute('update muster_roll_register set "DAY20"=%s where emp_code=%s',(value1,emp_code));
                                        if st_date==21 and wk_day==extra_off_day:
                                            cr.execute('update muster_roll_register set "DAY21"=%s where emp_code=%s',(value1,emp_code));
                                        if st_date==22 and wk_day==extra_off_day:
                                            cr.execute('update muster_roll_register set "DAY22"=%s where emp_code=%s',(value1,emp_code));
                                        if st_date==23 and wk_day==extra_off_day:
                                            cr.execute('update muster_roll_register set "DAY23"=%s where emp_code=%s',(value1,emp_code));
                                        if st_date==24 and wk_day==extra_off_day:
                                            cr.execute('update muster_roll_register set "DAY24"=%s where emp_code=%s',(value1,emp_code));
                        
                    if attendance.department_id.working_schedule=='5' and attendance.department_id.use_duty_roster==False:
                        if st_date==25 and wk_day==5:
                            cr.execute('update muster_roll_register set "DAY25"=%s where emp_code=%s',(value1,emp_code));
                        if st_date==26 and wk_day==5:
                            cr.execute('update muster_roll_register set "DAY26"=%s where emp_code=%s',(value1,emp_code));
                        if st_date==27 and wk_day==5:
                            cr.execute('update muster_roll_register set "DAY27"=%s where emp_code=%s',(value1,emp_code));
                        if st_date==28 and wk_day==5:
                            cr.execute('update muster_roll_register set "DAY28"=%s where emp_code=%s',(value1,emp_code));
                        if st_date==29 and wk_day==5:
                            cr.execute('update muster_roll_register set "DAY29"=%s where emp_code=%s',(value1,emp_code));
                        if st_date==30 and wk_day==5:
                            cr.execute('update muster_roll_register set "DAY30"=%s where emp_code=%s',(value1,emp_code));
                        if st_date==31 and wk_day==5:
                            cr.execute('update muster_roll_register set "DAY31"=%s where emp_code=%s',(value1,emp_code));
                        if st_date==1 and wk_day==5:
                            cr.execute('update muster_roll_register set "DAY1"=%s where emp_code=%s',(value1,emp_code));
                        if st_date==2 and wk_day==5:
                            cr.execute('update muster_roll_register set "DAY2"=%s where emp_code=%s',(value1,emp_code));
                        if st_date==3 and wk_day==5:
                            cr.execute('update muster_roll_register set "DAY3"=%s where emp_code=%s',(value1,emp_code));
                        if st_date==4 and wk_day==5:
                            cr.execute('update muster_roll_register set "DAY4"=%s where emp_code=%s',(value1,emp_code));
                        if st_date==5 and wk_day==5:
                            cr.execute('update muster_roll_register set "DAY5"=%s where emp_code=%s',(value1,emp_code));
                        if st_date==6 and wk_day==5:
                            cr.execute('update muster_roll_register set "DAY6"=%s where emp_code=%s',(value1,emp_code));
                        if st_date==7 and wk_day==5:
                            cr.execute('update muster_roll_register set "DAY7"=%s where emp_code=%s',(value1,emp_code));
                        if st_date==8 and wk_day==5:
                            cr.execute('update muster_roll_register set "DAY8"=%s where emp_code=%s',(value1,emp_code));
                        if st_date==9 and wk_day==5:
                            cr.execute('update muster_roll_register set "DAY9"=%s where emp_code=%s',(value1,emp_code));
                        if st_date==10 and wk_day==5:
                            cr.execute('update muster_roll_register set "DAY10"=%s where emp_code=%s',(value1,emp_code));
                        if st_date==11 and wk_day==5:
                            cr.execute('update muster_roll_register set "DAY11"=%s where emp_code=%s',(value1,emp_code));
                        if st_date==12 and wk_day==5:
                            cr.execute('update muster_roll_register set "DAY12"=%s where emp_code=%s',(value1,emp_code));
                        if st_date==13 and wk_day==5:
                            cr.execute('update muster_roll_register set "DAY13"=%s where emp_code=%s',(value1,emp_code));
                        if st_date==14 and wk_day==5:
                            cr.execute('update muster_roll_register set "DAY14"=%s where emp_code=%s',(value1,emp_code));
                        if st_date==15 and wk_day==5:
                            cr.execute('update muster_roll_register set "DAY15"=%s where emp_code=%s',(value1,emp_code));
                        if st_date==16 and wk_day==5:
                            cr.execute('update muster_roll_register set "DAY16"=%s where emp_code=%s',(value1,emp_code));
                        if st_date==17 and wk_day==5:
                            cr.execute('update muster_roll_register set "DAY17"=%s where emp_code=%s',(value1,emp_code));
                        if st_date==18 and wk_day==5:
                            cr.execute('update muster_roll_register set "DAY18"=%s where emp_code=%s',(value1,emp_code));
                        if st_date==19 and wk_day==5:
                            cr.execute('update muster_roll_register set "DAY19"=%s where emp_code=%s',(value1,emp_code));
                        if st_date==20 and wk_day==5:
                            cr.execute('update muster_roll_register set "DAY20"=%s where emp_code=%s',(value1,emp_code));
                        if st_date==21 and wk_day==5:
                            cr.execute('update muster_roll_register set "DAY21"=%s where emp_code=%s',(value1,emp_code));
                        if st_date==22 and wk_day==5:
                            cr.execute('update muster_roll_register set "DAY22"=%s where emp_code=%s',(value1,emp_code));
                        if st_date==23 and wk_day==5:
                            cr.execute('update muster_roll_register set "DAY23"=%s where emp_code=%s',(value1,emp_code));
                        if st_date==24 and wk_day==5:
                            cr.execute('update muster_roll_register set "DAY24"=%s where emp_code=%s',(value1,emp_code));
                    if attendance.department_id.working_schedule in ['5','6'] and attendance.department_id.use_duty_roster==False:
                        if st_date==25 and wk_day==6:
                            cr.execute('update muster_roll_register set "DAY25"=%s where emp_code=%s',(value2,emp_code));
                        if st_date==26 and wk_day==6:
                            cr.execute('update muster_roll_register set "DAY26"=%s where emp_code=%s',(value2,emp_code));
                        if st_date==27 and wk_day==6:
                            cr.execute('update muster_roll_register set "DAY27"=%s where emp_code=%s',(value2,emp_code));
                        if st_date==28 and wk_day==6:
                            cr.execute('update muster_roll_register set "DAY28"=%s where emp_code=%s',(value2,emp_code));
                        if st_date==29 and wk_day==6:
                            cr.execute('update muster_roll_register set "DAY29"=%s where emp_code=%s',(value2,emp_code));
                        if st_date==30 and wk_day==6:
                            cr.execute('update muster_roll_register set "DAY30"=%s where emp_code=%s',(value2,emp_code));
                        if st_date==31 and wk_day==6:
                            cr.execute('update muster_roll_register set "DAY31"=%s where emp_code=%s',(value2,emp_code));
                        if st_date==1 and wk_day==6:
                            cr.execute('update muster_roll_register set "DAY1"=%s where emp_code=%s',(value2,emp_code));
                        if st_date==2 and wk_day==6:
                            cr.execute('update muster_roll_register set "DAY2"=%s where emp_code=%s',(value2,emp_code));
                        if st_date==3 and wk_day==6:
                            cr.execute('update muster_roll_register set "DAY3"=%s where emp_code=%s',(value2,emp_code));
                        if st_date==4 and wk_day==6:
                            cr.execute('update muster_roll_register set "DAY4"=%s where emp_code=%s',(value2,emp_code));
                        if st_date==5 and wk_day==6:
                            cr.execute('update muster_roll_register set "DAY5"=%s where emp_code=%s',(value2,emp_code));
                        if st_date==6 and wk_day==6:
                            cr.execute('update muster_roll_register set "DAY6"=%s where emp_code=%s',(value2,emp_code));
                        if st_date==7 and wk_day==6:
                            cr.execute('update muster_roll_register set "DAY7"=%s where emp_code=%s',(value2,emp_code));
                        if st_date==8 and wk_day==6:
                            cr.execute('update muster_roll_register set "DAY8"=%s where emp_code=%s',(value2,emp_code));
                        if st_date==9 and wk_day==6:
                            cr.execute('update muster_roll_register set "DAY9"=%s where emp_code=%s',(value2,emp_code));
                        if st_date==10 and wk_day==6:
                            cr.execute('update muster_roll_register set "DAY10"=%s where emp_code=%s',(value2,emp_code));
                        if st_date==11 and wk_day==6:
                            cr.execute('update muster_roll_register set "DAY11"=%s where emp_code=%s',(value2,emp_code));
                        if st_date==12 and wk_day==6:
                            cr.execute('update muster_roll_register set "DAY12"=%s where emp_code=%s',(value2,emp_code));
                        if st_date==13 and wk_day==6:
                            cr.execute('update muster_roll_register set "DAY13"=%s where emp_code=%s',(value2,emp_code));
                        if st_date==14 and wk_day==6:
                            cr.execute('update muster_roll_register set "DAY14"=%s where emp_code=%s',(value2,emp_code));
                        if st_date==15 and wk_day==6:
                            cr.execute('update muster_roll_register set "DAY15"=%s where emp_code=%s',(value2,emp_code));
                        if st_date==16 and wk_day==6:
                            cr.execute('update muster_roll_register set "DAY16"=%s where emp_code=%s',(value2,emp_code));
                        if st_date==17 and wk_day==6:
                            cr.execute('update muster_roll_register set "DAY17"=%s where emp_code=%s',(value2,emp_code));
                        if st_date==18 and wk_day==6:
                            cr.execute('update muster_roll_register set "DAY18"=%s where emp_code=%s',(value2,emp_code));
                        if st_date==19 and wk_day==6:
                            cr.execute('update muster_roll_register set "DAY19"=%s where emp_code=%s',(value2,emp_code));
                        if st_date==20 and wk_day==6:
                            cr.execute('update muster_roll_register set "DAY20"=%s where emp_code=%s',(value2,emp_code));
                        if st_date==21 and wk_day==6:
                            cr.execute('update muster_roll_register set "DAY21"=%s where emp_code=%s',(value2,emp_code));
                        if st_date==22 and wk_day==6:
                            cr.execute('update muster_roll_register set "DAY22"=%s where emp_code=%s',(value2,emp_code));
                        if st_date==23 and wk_day==6:
                            cr.execute('update muster_roll_register set "DAY23"=%s where emp_code=%s',(value2,emp_code));
                        if st_date==24 and wk_day==6:
                            cr.execute('update muster_roll_register set "DAY24"=%s where emp_code=%s',(value2,emp_code));
                day_nhd=0
                for holiday in self.pool.get('ids.hr.public.holidays').search(cr,uid,[('year','=',str(year)),('department_ids','=',attendance.department_id.id)]):
                    for holiday_data in self.pool.get('ids.hr.public.holidays').browse(cr,uid,holiday,context=context):
                        holiday_id=holiday_data.id
                        for holiday_line in self.pool.get('ids.hr.public.holidays.line').search(cr,uid,[('date','>=',period_start),('date','<=',period_end),('holidays_id','=',holiday_id)], order='date'):
                            for holiday_data_line in self.pool.get('ids.hr.public.holidays.line').browse(cr,uid,holiday_line,context=context):
                                employee_id = emp_id.id
                                emp_code=emp_id.emp_code
                                value='NHD'
                                day=datetime.strptime(holiday_data_line.date,'%Y-%m-%d').day
                                day_nhd=datetime.strptime(holiday_data_line.date,'%Y-%m-%d').day
                                print"day_nhd====",day_nhd
                                if day==25:
                                    cr.execute('update muster_roll_register set "DAY25"=%s where emp_code=%s',(value,emp_code));
                                if day==26:
                                    cr.execute('update muster_roll_register set "DAY26"=%s where emp_code=%s',(value,emp_code));
                                if day==27:
                                    cr.execute('update muster_roll_register set "DAY27"=%s where emp_code=%s',(value,emp_code));
                                if day==28:
                                    cr.execute('update muster_roll_register set "DAY28"=%s where emp_code=%s',(value,emp_code));
                                if day==29:
                                    cr.execute('update muster_roll_register set "DAY29"=%s where emp_code=%s',(value,emp_code));
                                if day==30:
                                    cr.execute('update muster_roll_register set "DAY30"=%s where emp_code=%s',(value,emp_code));
                                if day==31:
                                    cr.execute('update muster_roll_register set "DAY31"=%s where emp_code=%s',(value,emp_code));
                                if day==1:
                                    cr.execute('update muster_roll_register set "DAY1"=%s where emp_code=%s',(value,emp_code));
                                if day==2:
                                    cr.execute('update muster_roll_register set "DAY2"=%s where emp_code=%s',(value,emp_code));
                                if day==3:
                                    cr.execute('update muster_roll_register set "DAY3"=%s where emp_code=%s',(value,emp_code));
                                if day==4:
                                    cr.execute('update muster_roll_register set "DAY4"=%s where emp_code=%s',(value,emp_code));
                                if day==5:
                                    cr.execute('update muster_roll_register set "DAY5"=%s where emp_code=%s',(value,emp_code));
                                if day==6:
                                    cr.execute('update muster_roll_register set "DAY6"=%s where emp_code=%s',(value,emp_code));
                                if day==7:
                                    cr.execute('update muster_roll_register set "DAY7"=%s where emp_code=%s',(value,emp_code));
                                if day==8:
                                    cr.execute('update muster_roll_register set "DAY8"=%s where emp_code=%s',(value,emp_code));
                                if day==9:
                                    cr.execute('update muster_roll_register set "DAY9"=%s where emp_code=%s',(value,emp_code));
                                if day==10:
                                    cr.execute('update muster_roll_register set "DAY10"=%s where emp_code=%s',(value,emp_code));
                                if day==11:
                                    cr.execute('update muster_roll_register set "DAY11"=%s where emp_code=%s',(value,emp_code));
                                if day==12:
                                    cr.execute('update muster_roll_register set "DAY12"=%s where emp_code=%s',(value,emp_code));
                                if day==13:
                                    cr.execute('update muster_roll_register set "DAY13"=%s where emp_code=%s',(value,emp_code));
                                if day==14:
                                    cr.execute('update muster_roll_register set "DAY14"=%s where emp_code=%s',(value,emp_code));
                                if day==15:
                                    cr.execute('update muster_roll_register set "DAY15"=%s where emp_code=%s',(value,emp_code));
                                if day==16:
                                    cr.execute('update muster_roll_register set "DAY16"=%s where emp_code=%s',(value,emp_code));
                                if day==17:
                                    cr.execute('update muster_roll_register set "DAY17"=%s where emp_code=%s',(value,emp_code));
                                if day==18:
                                    cr.execute('update muster_roll_register set "DAY18"=%s where emp_code=%s',(value,emp_code));
                                if day==19:
                                    cr.execute('update muster_roll_register set "DAY19"=%s where emp_code=%s',(value,emp_code));
                                if day==20:
                                    cr.execute('update muster_roll_register set "DAY20"=%s where emp_code=%s',(value,emp_code));
                                if day==21:
                                    cr.execute('update muster_roll_register set "DAY21"=%s where emp_code=%s',(value,emp_code));
                                if day==22:
                                    cr.execute('update muster_roll_register set "DAY22"=%s where emp_code=%s',(value,emp_code));
                                if day==23:
                                    cr.execute('update muster_roll_register set "DAY23"=%s where emp_code=%s',(value,emp_code));
                                if day==24:
                                    cr.execute('update muster_roll_register set "DAY24"=%s where emp_code=%s',(value,emp_code));
                if attendance.department_id.half_day_applicable== '7':
                    for punch in self.pool.get('final.punch').search(cr,uid,[('employee_id','=',employee_id),('date','>=',period_start),('date','<=',period_end),('worked_hours','>=',4.00),('worked_hours','<=',7.00)], order='date'):
                        for data in self.pool.get('final.punch').browse(cr,uid,punch,context=context):
                            emp_code=data.employee_id.emp_code
                            emp_name=data.employee_id.name
                            value='H.LWP'
                            day=datetime.strptime(data.date,'%Y-%m-%d').day
                            wk_day=datetime.strptime(data.date,'%Y-%m-%d').weekday()
    #                             day_nhd=0
                            day_off=7
                            extra_day_off=0
                            for roster in self.pool.get('hr.roster').search(cr,uid,[('from_date','=',period_start),('to_date','=',period_end),('department_id','=',attendance.department_id.id)]):
                                for roster_data in self.pool.get('hr.roster').browse(cr,uid,roster,context=context):
                                    data_id=roster_data.id
                                    for roster_line in self.pool.get('hr.roster.line').search(cr,uid,[('employee_id','=',employee_id),('roster_id','=',data_id)]):
                                        for roster_line_data in self.pool.get('hr.roster.line').browse(cr,uid,roster_line,context=context):
                                            day_off=int(roster_line_data.off_day)
                                            extra_day_off=int(roster_line_data.extra_off_day)
                            if attendance.department_id.use_duty_roster==True and wk_day==day_off:
                                value='DP'
                            if attendance.department_id.use_duty_roster==True and wk_day==extra_day_off:
                                value='XTDP'
                            if attendance.department_id.working_schedule=='5' and wk_day==5 and attendance.department_id.use_duty_roster==False:
                                value='XTDP'
                            if wk_day==6 and attendance.department_id.use_duty_roster==False:
                                value='DP'
    #                             for holiday in self.pool.get('ids.hr.public.holidays.line').search(cr,uid,[('date','>=',period_start),('date','<=',period_end)], order='date'):
    #                                 for holiday_data in self.pool.get('ids.hr.public.holidays.line').browse(cr,uid,holiday,context=context):
    #                                     day_nhd=datetime.strptime(holiday_data.date,'%Y-%m-%d').day
                            if day==day_nhd:
                                value='NHDP'
                            if day==25:
                                cr.execute('update muster_roll_register set "DAY25"=%s where emp_code=%s',(value,emp_code));
                            if day==26:
                                cr.execute('update muster_roll_register set "DAY26"=%s where emp_code=%s',(value,emp_code));
                            if day==27:
                                cr.execute('update muster_roll_register set "DAY27"=%s where emp_code=%s',(value,emp_code));
                            if day==28:
                                cr.execute('update muster_roll_register set "DAY28"=%s where emp_code=%s',(value,emp_code));
                            if day==29:
                                cr.execute('update muster_roll_register set "DAY29"=%s where emp_code=%s',(value,emp_code));
                            if day==30:
                                cr.execute('update muster_roll_register set "DAY30"=%s where emp_code=%s',(value,emp_code));
                            if day==31:
                                cr.execute('update muster_roll_register set "DAY31"=%s where emp_code=%s',(value,emp_code));
                            if day==1:
                                cr.execute('update muster_roll_register set "DAY1"=%s where emp_code=%s',(value,emp_code));
                            if day==2:
                                cr.execute('update muster_roll_register set "DAY2"=%s where emp_code=%s',(value,emp_code));
                            if day==3:
                                cr.execute('update muster_roll_register set "DAY3"=%s where emp_code=%s',(value,emp_code));
                            if day==4:
                                cr.execute('update muster_roll_register set "DAY4"=%s where emp_code=%s',(value,emp_code));
                            if day==5:
                                cr.execute('update muster_roll_register set "DAY5"=%s where emp_code=%s',(value,emp_code));
                            if day==6:
                                cr.execute('update muster_roll_register set "DAY6"=%s where emp_code=%s',(value,emp_code));
                            if day==7:
                                cr.execute('update muster_roll_register set "DAY7"=%s where emp_code=%s',(value,emp_code));
                            if day==8:
                                cr.execute('update muster_roll_register set "DAY8"=%s where emp_code=%s',(value,emp_code));
                            if day==9:
                                cr.execute('update muster_roll_register set "DAY9"=%s where emp_code=%s',(value,emp_code));
                            if day==10:
                                cr.execute('update muster_roll_register set "DAY10"=%s where emp_code=%s',(value,emp_code));
                            if day==11:
                                cr.execute('update muster_roll_register set "DAY11"=%s where emp_code=%s',(value,emp_code));
                            if day==12:
                                cr.execute('update muster_roll_register set "DAY12"=%s where emp_code=%s',(value,emp_code));
                            if day==13:
                                cr.execute('update muster_roll_register set "DAY13"=%s where emp_code=%s',(value,emp_code));
                            if day==14:
                                cr.execute('update muster_roll_register set "DAY14"=%s where emp_code=%s',(value,emp_code));
                            if day==15:
                                cr.execute('update muster_roll_register set "DAY15"=%s where emp_code=%s',(value,emp_code));
                            if day==16:
                                cr.execute('update muster_roll_register set "DAY16"=%s where emp_code=%s',(value,emp_code));
                            if day==17:
                                cr.execute('update muster_roll_register set "DAY17"=%s where emp_code=%s',(value,emp_code));
                            if day==18:
                                cr.execute('update muster_roll_register set "DAY18"=%s where emp_code=%s',(value,emp_code));
                            if day==19:
                                cr.execute('update muster_roll_register set "DAY19"=%s where emp_code=%s',(value,emp_code));
                            if day==20:
                                cr.execute('update muster_roll_register set "DAY20"=%s where emp_code=%s',(value,emp_code));
                            if day==21:
                                cr.execute('update muster_roll_register set "DAY21"=%s where emp_code=%s',(value,emp_code));
                            if day==22:
                                cr.execute('update muster_roll_register set "DAY22"=%s where emp_code=%s',(value,emp_code));
                            if day==23:
                                cr.execute('update muster_roll_register set "DAY23"=%s where emp_code=%s',(value,emp_code));
                            if day==24:
                                cr.execute('update muster_roll_register set "DAY24"=%s where emp_code=%s',(value,emp_code));

                if attendance.department_id.half_day_applicable== '6':
                    for punch in self.pool.get('final.punch').search(cr,uid,[('employee_id','=',employee_id),('date','>=',period_start),('date','<=',period_end),('worked_hours','>=',4.00),('worked_hours','<=',6.00)], order='date'):
                        for data in self.pool.get('final.punch').browse(cr,uid,punch,context=context):
                            emp_code=data.employee_id.emp_code
                            emp_name=data.employee_id.name
                            value='H.LWP'
                            day=datetime.strptime(data.date,'%Y-%m-%d').day
                            wk_day=datetime.strptime(data.date,'%Y-%m-%d').weekday()
    #                             day_nhd=0
                            day_off=7
                            extra_day_off=0
                            for roster in self.pool.get('hr.roster').search(cr,uid,[('from_date','=',period_start),('to_date','=',period_end),('department_id','=',attendance.department_id.id)]):
                                for roster_data in self.pool.get('hr.roster').browse(cr,uid,roster,context=context):
                                    data_id=roster_data.id
                                    for roster_line in self.pool.get('hr.roster.line').search(cr,uid,[('employee_id','=',employee_id),('roster_id','=',data_id)]):
                                        for roster_line_data in self.pool.get('hr.roster.line').browse(cr,uid,roster_line,context=context):
                                            day_off=int(roster_line_data.off_day)
                                            extra_day_off=int(roster_line_data.extra_off_day)
                            if attendance.department_id.use_duty_roster==True and wk_day==day_off:
                                value='DP'
                            if attendance.department_id.use_duty_roster==True and wk_day==extra_day_off:
                                value='XTDP'
                            if attendance.department_id.working_schedule=='5' and wk_day==5 and attendance.department_id.use_duty_roster==False:
                                value='XTDP'
                            if wk_day==6 and attendance.department_id.use_duty_roster==False:
                                value='DP'
    #                             for holiday in self.pool.get('ids.hr.public.holidays.line').search(cr,uid,[('date','>=',period_start),('date','<=',period_end)], order='date'):
    #                                 for holiday_data in self.pool.get('ids.hr.public.holidays.line').browse(cr,uid,holiday,context=context):
    #                                     day_nhd=datetime.strptime(holiday_data.date,'%Y-%m-%d').day
                            if day==day_nhd:
                                value='NHDP'
                            if day==25:
                                cr.execute('update muster_roll_register set "DAY25"=%s where emp_code=%s',(value,emp_code));
                            if day==26:
                                cr.execute('update muster_roll_register set "DAY26"=%s where emp_code=%s',(value,emp_code));
                            if day==27:
                                cr.execute('update muster_roll_register set "DAY27"=%s where emp_code=%s',(value,emp_code));
                            if day==28:
                                cr.execute('update muster_roll_register set "DAY28"=%s where emp_code=%s',(value,emp_code));
                            if day==29:
                                cr.execute('update muster_roll_register set "DAY29"=%s where emp_code=%s',(value,emp_code));
                            if day==30:
                                cr.execute('update muster_roll_register set "DAY30"=%s where emp_code=%s',(value,emp_code));
                            if day==31:
                                cr.execute('update muster_roll_register set "DAY31"=%s where emp_code=%s',(value,emp_code));
                            if day==1:
                                cr.execute('update muster_roll_register set "DAY1"=%s where emp_code=%s',(value,emp_code));
                            if day==2:
                                cr.execute('update muster_roll_register set "DAY2"=%s where emp_code=%s',(value,emp_code));
                            if day==3:
                                cr.execute('update muster_roll_register set "DAY3"=%s where emp_code=%s',(value,emp_code));
                            if day==4:
                                cr.execute('update muster_roll_register set "DAY4"=%s where emp_code=%s',(value,emp_code));
                            if day==5:
                                cr.execute('update muster_roll_register set "DAY5"=%s where emp_code=%s',(value,emp_code));
                            if day==6:
                                cr.execute('update muster_roll_register set "DAY6"=%s where emp_code=%s',(value,emp_code));
                            if day==7:
                                cr.execute('update muster_roll_register set "DAY7"=%s where emp_code=%s',(value,emp_code));
                            if day==8:
                                cr.execute('update muster_roll_register set "DAY8"=%s where emp_code=%s',(value,emp_code));
                            if day==9:
                                cr.execute('update muster_roll_register set "DAY9"=%s where emp_code=%s',(value,emp_code));
                            if day==10:
                                cr.execute('update muster_roll_register set "DAY10"=%s where emp_code=%s',(value,emp_code));
                            if day==11:
                                cr.execute('update muster_roll_register set "DAY11"=%s where emp_code=%s',(value,emp_code));
                            if day==12:
                                cr.execute('update muster_roll_register set "DAY12"=%s where emp_code=%s',(value,emp_code));
                            if day==13:
                                cr.execute('update muster_roll_register set "DAY13"=%s where emp_code=%s',(value,emp_code));
                            if day==14:
                                cr.execute('update muster_roll_register set "DAY14"=%s where emp_code=%s',(value,emp_code));
                            if day==15:
                                cr.execute('update muster_roll_register set "DAY15"=%s where emp_code=%s',(value,emp_code));
                            if day==16:
                                cr.execute('update muster_roll_register set "DAY16"=%s where emp_code=%s',(value,emp_code));
                            if day==17:
                                cr.execute('update muster_roll_register set "DAY17"=%s where emp_code=%s',(value,emp_code));
                            if day==18:
                                cr.execute('update muster_roll_register set "DAY18"=%s where emp_code=%s',(value,emp_code));
                            if day==19:
                                cr.execute('update muster_roll_register set "DAY19"=%s where emp_code=%s',(value,emp_code));
                            if day==20:
                                cr.execute('update muster_roll_register set "DAY20"=%s where emp_code=%s',(value,emp_code));
                            if day==21:
                                cr.execute('update muster_roll_register set "DAY21"=%s where emp_code=%s',(value,emp_code));
                            if day==22:
                                cr.execute('update muster_roll_register set "DAY22"=%s where emp_code=%s',(value,emp_code));
                            if day==23:
                                cr.execute('update muster_roll_register set "DAY23"=%s where emp_code=%s',(value,emp_code));
                            if day==24:
                                cr.execute('update muster_roll_register set "DAY24"=%s where emp_code=%s',(value,emp_code));
                
                if attendance.department_id.half_day_applicable== '6':    
                    for punch in self.pool.get('final.punch').search(cr,uid,[('employee_id','=',employee_id),('date','>=',period_start),('date','<=',period_end),('worked_hours','>=',6.00)], order='date'):
                        for data in self.pool.get('final.punch').browse(cr,uid,punch,context=context):
                            emp_code=data.employee_id.emp_code
                            emp_name=data.employee_id.name
                            value='P'
                            day=datetime.strptime(data.date,'%Y-%m-%d').day
                            od=data.od_check
                            wk_day=datetime.strptime(data.date,'%Y-%m-%d').weekday()
    #                             day_nhd=0
                            day_off=7
                            extra_day_off=0
                            for roster in self.pool.get('hr.roster').search(cr,uid,[('from_date','=',period_start),('to_date','=',period_end),('department_id','=',attendance.department_id.id)]):
                                for roster_data in self.pool.get('hr.roster').browse(cr,uid,roster,context=context):
                                    data_id=roster_data.id
                                    for roster_line in self.pool.get('hr.roster.line').search(cr,uid,[('employee_id','=',employee_id),('roster_id','=',data_id)]):
                                        for roster_line_data in self.pool.get('hr.roster.line').browse(cr,uid,roster_line,context=context):
                                            day_off=int(roster_line_data.off_day)
                                            extra_day_off=int(roster_line_data.extra_off_day)
                            if attendance.department_id.use_duty_roster==True and wk_day==day_off:
                                value='DP'
                            if attendance.department_id.use_duty_roster==True and wk_day==extra_day_off:
                                value='XTDP'
                            if attendance.department_id.working_schedule=='5' and wk_day==5 and attendance.department_id.use_duty_roster==False:
                                value='XTDP'
                            if wk_day==6 and attendance.department_id.use_duty_roster==False:
                                value='DP'
                            if od==True:
                                value='OD'
    #                             for holiday in self.pool.get('ids.hr.public.holidays.line').search(cr,uid,[('date','>=',period_start),('date','<=',period_end)], order='date'):
    #                                 for holiday_data in self.pool.get('ids.hr.public.holidays.line').browse(cr,uid,holiday,context=context):
    #                                     day_nhd=datetime.strptime(holiday_data.date,'%Y-%m-%d').day
                            if day==day_nhd:
                                value='NHDP'
                            if day==25:
                                cr.execute('update muster_roll_register set "DAY25"=%s where emp_code=%s',(value,emp_code));
                            if day==26:
                                cr.execute('update muster_roll_register set "DAY26"=%s where emp_code=%s',(value,emp_code));
                            if day==27:
                                cr.execute('update muster_roll_register set "DAY27"=%s where emp_code=%s',(value,emp_code));
                            if day==28:
                                cr.execute('update muster_roll_register set "DAY28"=%s where emp_code=%s',(value,emp_code));
                            if day==29:
                                cr.execute('update muster_roll_register set "DAY29"=%s where emp_code=%s',(value,emp_code));
                            if day==30:
                                cr.execute('update muster_roll_register set "DAY30"=%s where emp_code=%s',(value,emp_code));
                            if day==31:
                                cr.execute('update muster_roll_register set "DAY31"=%s where emp_code=%s',(value,emp_code));
                            if day==1:
                                cr.execute('update muster_roll_register set "DAY1"=%s where emp_code=%s',(value,emp_code));
                            if day==2:
                                cr.execute('update muster_roll_register set "DAY2"=%s where emp_code=%s',(value,emp_code));
                            if day==3:
                                cr.execute('update muster_roll_register set "DAY3"=%s where emp_code=%s',(value,emp_code));
                            if day==4:
                                cr.execute('update muster_roll_register set "DAY4"=%s where emp_code=%s',(value,emp_code));
                            if day==5:
                                cr.execute('update muster_roll_register set "DAY5"=%s where emp_code=%s',(value,emp_code));
                            if day==6:
                                cr.execute('update muster_roll_register set "DAY6"=%s where emp_code=%s',(value,emp_code));
                            if day==7:
                                cr.execute('update muster_roll_register set "DAY7"=%s where emp_code=%s',(value,emp_code));
                            if day==8:
                                cr.execute('update muster_roll_register set "DAY8"=%s where emp_code=%s',(value,emp_code));
                            if day==9:
                                cr.execute('update muster_roll_register set "DAY9"=%s where emp_code=%s',(value,emp_code));
                            if day==10:
                                cr.execute('update muster_roll_register set "DAY10"=%s where emp_code=%s',(value,emp_code));
                            if day==11:
                                cr.execute('update muster_roll_register set "DAY11"=%s where emp_code=%s',(value,emp_code));
                            if day==12:
                                cr.execute('update muster_roll_register set "DAY12"=%s where emp_code=%s',(value,emp_code));
                            if day==13:
                                cr.execute('update muster_roll_register set "DAY13"=%s where emp_code=%s',(value,emp_code));
                            if day==14:
                                cr.execute('update muster_roll_register set "DAY14"=%s where emp_code=%s',(value,emp_code));
                            if day==15:
                                cr.execute('update muster_roll_register set "DAY15"=%s where emp_code=%s',(value,emp_code));
                            if day==16:
                                cr.execute('update muster_roll_register set "DAY16"=%s where emp_code=%s',(value,emp_code));
                            if day==17:
                                cr.execute('update muster_roll_register set "DAY17"=%s where emp_code=%s',(value,emp_code));
                            if day==18:
                                cr.execute('update muster_roll_register set "DAY18"=%s where emp_code=%s',(value,emp_code));
                            if day==19:
                                cr.execute('update muster_roll_register set "DAY19"=%s where emp_code=%s',(value,emp_code));
                            if day==20:
                                cr.execute('update muster_roll_register set "DAY20"=%s where emp_code=%s',(value,emp_code));
                            if day==21:
                                cr.execute('update muster_roll_register set "DAY21"=%s where emp_code=%s',(value,emp_code));
                            if day==22:
                                cr.execute('update muster_roll_register set "DAY22"=%s where emp_code=%s',(value,emp_code));
                            if day==23:
                                cr.execute('update muster_roll_register set "DAY23"=%s where emp_code=%s',(value,emp_code));
                            if day==24:
                                cr.execute('update muster_roll_register set "DAY24"=%s where emp_code=%s',(value,emp_code));
                
                if attendance.department_id.half_day_applicable== '7':    
                    for punch in self.pool.get('final.punch').search(cr,uid,[('employee_id','=',employee_id),('date','>=',period_start),('date','<=',period_end),('worked_hours','>=',7.00)], order='date'):
                        for data in self.pool.get('final.punch').browse(cr,uid,punch,context=context):
                            emp_code=data.employee_id.emp_code
                            emp_name=data.employee_id.name
                            value='P'
                            day=datetime.strptime(data.date,'%Y-%m-%d').day
                            od=data.od_check
                            wk_day=datetime.strptime(data.date,'%Y-%m-%d').weekday()
    #                             day_nhd=0
                            day_off=7
                            extra_day_off=0
                            for roster in self.pool.get('hr.roster').search(cr,uid,[('from_date','=',period_start),('to_date','=',period_end),('department_id','=',attendance.department_id.id)]):
                                for roster_data in self.pool.get('hr.roster').browse(cr,uid,roster,context=context):
                                    data_id=roster_data.id
                                    for roster_line in self.pool.get('hr.roster.line').search(cr,uid,[('employee_id','=',employee_id),('roster_id','=',data_id)]):
                                        for roster_line_data in self.pool.get('hr.roster.line').browse(cr,uid,roster_line,context=context):
                                            day_off=int(roster_line_data.off_day)
                                            extra_day_off=int(roster_line_data.extra_off_day)
                            if attendance.department_id.use_duty_roster==True and wk_day==day_off:
                                value='DP'
                            if attendance.department_id.use_duty_roster==True and wk_day==extra_day_off:
                                value='XTDP'
                            if attendance.department_id.working_schedule=='5' and wk_day==5 and attendance.department_id.use_duty_roster==False:
                                value='XTDP'
                            if wk_day==6 and attendance.department_id.use_duty_roster==False:
                                value='DP'
                            if od==True:
                                value='OD'
    #                             for holiday in self.pool.get('ids.hr.public.holidays.line').search(cr,uid,[('date','>=',period_start),('date','<=',period_end)], order='date'):
    #                                 for holiday_data in self.pool.get('ids.hr.public.holidays.line').browse(cr,uid,holiday,context=context):
    #                                     day_nhd=datetime.strptime(holiday_data.date,'%Y-%m-%d').day
                            if day==day_nhd:
                                value='NHDP'
                            if day==25:
                                cr.execute('update muster_roll_register set "DAY25"=%s where emp_code=%s',(value,emp_code));
                            if day==26:
                                cr.execute('update muster_roll_register set "DAY26"=%s where emp_code=%s',(value,emp_code));
                            if day==27:
                                cr.execute('update muster_roll_register set "DAY27"=%s where emp_code=%s',(value,emp_code));
                            if day==28:
                                cr.execute('update muster_roll_register set "DAY28"=%s where emp_code=%s',(value,emp_code));
                            if day==29:
                                cr.execute('update muster_roll_register set "DAY29"=%s where emp_code=%s',(value,emp_code));
                            if day==30:
                                cr.execute('update muster_roll_register set "DAY30"=%s where emp_code=%s',(value,emp_code));
                            if day==31:
                                cr.execute('update muster_roll_register set "DAY31"=%s where emp_code=%s',(value,emp_code));
                            if day==1:
                                cr.execute('update muster_roll_register set "DAY1"=%s where emp_code=%s',(value,emp_code));
                            if day==2:
                                cr.execute('update muster_roll_register set "DAY2"=%s where emp_code=%s',(value,emp_code));
                            if day==3:
                                cr.execute('update muster_roll_register set "DAY3"=%s where emp_code=%s',(value,emp_code));
                            if day==4:
                                cr.execute('update muster_roll_register set "DAY4"=%s where emp_code=%s',(value,emp_code));
                            if day==5:
                                cr.execute('update muster_roll_register set "DAY5"=%s where emp_code=%s',(value,emp_code));
                            if day==6:
                                cr.execute('update muster_roll_register set "DAY6"=%s where emp_code=%s',(value,emp_code));
                            if day==7:
                                cr.execute('update muster_roll_register set "DAY7"=%s where emp_code=%s',(value,emp_code));
                            if day==8:
                                cr.execute('update muster_roll_register set "DAY8"=%s where emp_code=%s',(value,emp_code));
                            if day==9:
                                cr.execute('update muster_roll_register set "DAY9"=%s where emp_code=%s',(value,emp_code));
                            if day==10:
                                cr.execute('update muster_roll_register set "DAY10"=%s where emp_code=%s',(value,emp_code));
                            if day==11:
                                cr.execute('update muster_roll_register set "DAY11"=%s where emp_code=%s',(value,emp_code));
                            if day==12:
                                cr.execute('update muster_roll_register set "DAY12"=%s where emp_code=%s',(value,emp_code));
                            if day==13:
                                cr.execute('update muster_roll_register set "DAY13"=%s where emp_code=%s',(value,emp_code));
                            if day==14:
                                cr.execute('update muster_roll_register set "DAY14"=%s where emp_code=%s',(value,emp_code));
                            if day==15:
                                cr.execute('update muster_roll_register set "DAY15"=%s where emp_code=%s',(value,emp_code));
                            if day==16:
                                cr.execute('update muster_roll_register set "DAY16"=%s where emp_code=%s',(value,emp_code));
                            if day==17:
                                cr.execute('update muster_roll_register set "DAY17"=%s where emp_code=%s',(value,emp_code));
                            if day==18:
                                cr.execute('update muster_roll_register set "DAY18"=%s where emp_code=%s',(value,emp_code));
                            if day==19:
                                cr.execute('update muster_roll_register set "DAY19"=%s where emp_code=%s',(value,emp_code));
                            if day==20:
                                cr.execute('update muster_roll_register set "DAY20"=%s where emp_code=%s',(value,emp_code));
                            if day==21:
                                cr.execute('update muster_roll_register set "DAY21"=%s where emp_code=%s',(value,emp_code));
                            if day==22:
                                cr.execute('update muster_roll_register set "DAY22"=%s where emp_code=%s',(value,emp_code));
                            if day==23:
                                cr.execute('update muster_roll_register set "DAY23"=%s where emp_code=%s',(value,emp_code));
                            if day==24:
                                cr.execute('update muster_roll_register set "DAY24"=%s where emp_code=%s',(value,emp_code));
                
                
                
                for leave in self.pool.get('hr.holidays').search(cr,uid,[('employee_id','=',employee_id),('date_from_temp','>=',period_start),('date_to_temp','<=',period_end),('type','=','remove'),('state','=','validate')], order='date_from_temp'):
                    for leave_data in self.pool.get('hr.holidays').browse(cr,uid,leave,context=context):
                        
                        emp_code=leave_data.employee_id.emp_code
                        emp_name=leave_data.employee_id.name
                        leave_type=leave_data.holiday_status_id.code
                        day1=datetime.strptime(leave_data.date_from_temp,'%Y-%m-%d').day
                        month1=datetime.strptime(leave_data.date_from_temp,'%Y-%m-%d').month
                        year1=datetime.strptime(leave_data.date_from_temp,'%Y-%m-%d').year
                        day2=datetime.strptime(leave_data.date_to_temp,'%Y-%m-%d').day
                        month2=datetime.strptime(leave_data.date_to_temp,'%Y-%m-%d').month
                        year2=datetime.strptime(leave_data.date_to_temp,'%Y-%m-%d').year
                        d1 = date(year = year1, month = month1, day = day1)
                        d2 = date(year = year2, month = month2, day = day2)
                        delta = d2 - d1
                        present_day=0
                        day=0
                        punch=self.pool.get('final.punch').search(cr,uid,[('date','=',leave_data.date_from_temp),('employee_id','=',leave_data.employee_id.id)], order='date')
                        data = self.pool.get('final.punch').browse(cr,uid,punch,context=context)
                        punch1=self.pool.get('final.punch').search(cr,uid,[('date','=',leave_data.date_to_temp),('employee_id','=',leave_data.employee_id.id)], order='date')
                        data1 = self.pool.get('final.punch').browse(cr,uid,punch1,context=context)
                        if data:
                            present_day=datetime.strptime(data.date,'%Y-%m-%d').day
                        if data1:
                            present_day=datetime.strptime(data1.date,'%Y-%m-%d').day
                        if d1==d2 and (leave_data.second_half_temp==True or leave_data.first_half_temp==True):
                            leave_type = 'H.' + str(leave_data.holiday_status_id.code)
                        for i in range(delta.days + 1):
                            day=(d1 + td(days=i)).day
                            if day==present_day:
                                leave_type = 'H.' + str(leave_data.holiday_status_id.code)
                            else:
                                leave_type=leave_data.holiday_status_id.code
                            if day==25:
                                cr.execute('update muster_roll_register set "DAY25"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==26:
                                cr.execute('update muster_roll_register set "DAY26"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==27:
                                cr.execute('update muster_roll_register set "DAY27"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==28:
                                cr.execute('update muster_roll_register set "DAY28"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==29:
                                cr.execute('update muster_roll_register set "DAY29"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==30:
                                cr.execute('update muster_roll_register set "DAY30"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==31:
                                cr.execute('update muster_roll_register set "DAY31"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==1:
                                cr.execute('update muster_roll_register set "DAY1"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==2:
                                cr.execute('update muster_roll_register set "DAY2"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==3:
                                cr.execute('update muster_roll_register set "DAY3"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==4:
                                cr.execute('update muster_roll_register set "DAY4"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==5:
                                cr.execute('update muster_roll_register set "DAY5"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==6:
                                cr.execute('update muster_roll_register set "DAY6"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==7:
                                cr.execute('update muster_roll_register set "DAY7"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==8:
                                cr.execute('update muster_roll_register set "DAY8"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==9:
                                cr.execute('update muster_roll_register set "DAY9"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==10:
                                cr.execute('update muster_roll_register set "DAY10"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==11:
                                cr.execute('update muster_roll_register set "DAY11"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==12:
                                cr.execute('update muster_roll_register set "DAY12"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==13:
                                cr.execute('update muster_roll_register set "DAY13"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==14:
                                cr.execute('update muster_roll_register set "DAY14"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==15:
                                cr.execute('update muster_roll_register set "DAY15"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==16:
                                cr.execute('update muster_roll_register set "DAY16"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==17:
                                cr.execute('update muster_roll_register set "DAY17"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==18:
                                cr.execute('update muster_roll_register set "DAY18"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==19:
                                cr.execute('update muster_roll_register set "DAY19"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==20:
                                cr.execute('update muster_roll_register set "DAY20"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==21:
                                cr.execute('update muster_roll_register set "DAY21"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==22:
                                cr.execute('update muster_roll_register set "DAY22"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==23:
                                cr.execute('update muster_roll_register set "DAY23"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==24:
                                cr.execute('update muster_roll_register set "DAY24"=%s where emp_code=%s',(leave_type,emp_code));

                for leave in self.pool.get('hr.holidays').search(cr,uid,[('employee_id','=',employee_id),('date_from_temp','>=',period_start),('date_to_temp','<=',period_end),('type','=','remove'),('state','=','validate'),('active','=',False)], order='date_from_temp'):
                    for leave_data in self.pool.get('hr.holidays').browse(cr,uid,leave,context=context):
                        
                        emp_code=leave_data.employee_id.emp_code
                        emp_name=leave_data.employee_id.name
                        leave_type=leave_data.holiday_status_id.code
                        day1=datetime.strptime(leave_data.date_from_temp,'%Y-%m-%d').day
                        month1=datetime.strptime(leave_data.date_from_temp,'%Y-%m-%d').month
                        year1=datetime.strptime(leave_data.date_from_temp,'%Y-%m-%d').year
                        day2=datetime.strptime(leave_data.date_to_temp,'%Y-%m-%d').day
                        month2=datetime.strptime(leave_data.date_to_temp,'%Y-%m-%d').month
                        year2=datetime.strptime(leave_data.date_to_temp,'%Y-%m-%d').year
                        d1 = date(year = year1, month = month1, day = day1)
                        d2 = date(year = year2, month = month2, day = day2)
                        delta = d2 - d1
                        present_day=0
                        day=0
                        punch=self.pool.get('final.punch').search(cr,uid,[('date','=',leave_data.date_from_temp),('employee_id','=',leave_data.employee_id.id)], order='date')
                        data = self.pool.get('final.punch').browse(cr,uid,punch,context=context)
                        punch1=self.pool.get('final.punch').search(cr,uid,[('date','=',leave_data.date_to_temp),('employee_id','=',leave_data.employee_id.id)], order='date')
                        data1 = self.pool.get('final.punch').browse(cr,uid,punch1,context=context)
                        if data:
                            present_day=datetime.strptime(data.date,'%Y-%m-%d').day
                        if data1:
                            present_day=datetime.strptime(data1.date,'%Y-%m-%d').day
                        if d1==d2 and (leave_data.second_half_temp==True or leave_data.first_half_temp==True):
                            leave_type = 'H.' + str(leave_data.holiday_status_id.code)
                        for i in range(delta.days + 1):
                            day=(d1 + td(days=i)).day
                            if day==present_day:
                                leave_type = 'H.' + str(leave_data.holiday_status_id.code)
                            else:
                                leave_type=leave_data.holiday_status_id.code
                            if day==25:
                                cr.execute('update muster_roll_register set "DAY25"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==26:
                                cr.execute('update muster_roll_register set "DAY26"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==27:
                                cr.execute('update muster_roll_register set "DAY27"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==28:
                                cr.execute('update muster_roll_register set "DAY28"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==29:
                                cr.execute('update muster_roll_register set "DAY29"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==30:
                                cr.execute('update muster_roll_register set "DAY30"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==31:
                                cr.execute('update muster_roll_register set "DAY31"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==1:
                                cr.execute('update muster_roll_register set "DAY1"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==2:
                                cr.execute('update muster_roll_register set "DAY2"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==3:
                                cr.execute('update muster_roll_register set "DAY3"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==4:
                                cr.execute('update muster_roll_register set "DAY4"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==5:
                                cr.execute('update muster_roll_register set "DAY5"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==6:
                                cr.execute('update muster_roll_register set "DAY6"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==7:
                                cr.execute('update muster_roll_register set "DAY7"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==8:
                                cr.execute('update muster_roll_register set "DAY8"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==9:
                                cr.execute('update muster_roll_register set "DAY9"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==10:
                                cr.execute('update muster_roll_register set "DAY10"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==11:
                                cr.execute('update muster_roll_register set "DAY11"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==12:
                                cr.execute('update muster_roll_register set "DAY12"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==13:
                                cr.execute('update muster_roll_register set "DAY13"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==14:
                                cr.execute('update muster_roll_register set "DAY14"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==15:
                                cr.execute('update muster_roll_register set "DAY15"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==16:
                                cr.execute('update muster_roll_register set "DAY16"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==17:
                                cr.execute('update muster_roll_register set "DAY17"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==18:
                                cr.execute('update muster_roll_register set "DAY18"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==19:
                                cr.execute('update muster_roll_register set "DAY19"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==20:
                                cr.execute('update muster_roll_register set "DAY20"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==21:
                                cr.execute('update muster_roll_register set "DAY21"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==22:
                                cr.execute('update muster_roll_register set "DAY22"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==23:
                                cr.execute('update muster_roll_register set "DAY23"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==24:
                                cr.execute('update muster_roll_register set "DAY24"=%s where emp_code=%s',(leave_type,emp_code));


                for leave in self.pool.get('hr.holidays').search(cr,uid,[('employee_id','=',employee_id),('date_to_temp','>=',period_start),('date_from_temp','<=',period_start),('type','=','remove'),('state','=','validate')], order='date_from_temp'):
                    for leave_data in self.pool.get('hr.holidays').browse(cr,uid,leave,context=context):
                        
                        emp_code=leave_data.employee_id.emp_code
                        emp_name=leave_data.employee_id.name
                        leave_type=leave_data.holiday_status_id.code
                        day1=datetime.strptime(leave_data.date_from_temp,'%Y-%m-%d').day
                        month1=datetime.strptime(leave_data.date_from_temp,'%Y-%m-%d').month
                        year1=datetime.strptime(leave_data.date_from_temp,'%Y-%m-%d').year
                        day2=datetime.strptime(leave_data.date_to_temp,'%Y-%m-%d').day
                        month2=datetime.strptime(leave_data.date_to_temp,'%Y-%m-%d').month
                        year2=datetime.strptime(leave_data.date_to_temp,'%Y-%m-%d').year
                        d1 = date(year = year1, month = month1, day = 25)
                        d2 = date(year = year2, month = month2, day = day2)
                        delta = d2 - d1
                        present_day=0
                        day=0
                        punch=self.pool.get('final.punch').search(cr,uid,[('date','=',leave_data.date_from_temp),('employee_id','=',leave_data.employee_id.id)], order='date')
                        data = self.pool.get('final.punch').browse(cr,uid,punch,context=context)
                        punch1=self.pool.get('final.punch').search(cr,uid,[('date','=',leave_data.date_to_temp),('employee_id','=',leave_data.employee_id.id)], order='date')
                        data1 = self.pool.get('final.punch').browse(cr,uid,punch1,context=context)
                        if data:
                            present_day=datetime.strptime(data.date,'%Y-%m-%d').day
                        if data1:
                            present_day=datetime.strptime(data1.date,'%Y-%m-%d').day
                        if d1==d2 and (leave_data.second_half_temp==True or leave_data.first_half_temp==True):
                            leave_type = 'H.' + str(leave_data.holiday_status_id.code)
                        for i in range(delta.days + 1):
                            day=(d1 + td(days=i)).day
                            if day==present_day:
                                leave_type = 'H.' + str(leave_data.holiday_status_id.code)
                            else:
                                leave_type=leave_data.holiday_status_id.code
                            if day==25:
                                cr.execute('update muster_roll_register set "DAY25"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==26:
                                cr.execute('update muster_roll_register set "DAY26"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==27:
                                cr.execute('update muster_roll_register set "DAY27"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==28:
                                cr.execute('update muster_roll_register set "DAY28"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==29:
                                cr.execute('update muster_roll_register set "DAY29"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==30:
                                cr.execute('update muster_roll_register set "DAY30"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==31:
                                cr.execute('update muster_roll_register set "DAY31"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==1:
                                cr.execute('update muster_roll_register set "DAY1"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==2:
                                cr.execute('update muster_roll_register set "DAY2"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==3:
                                cr.execute('update muster_roll_register set "DAY3"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==4:
                                cr.execute('update muster_roll_register set "DAY4"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==5:
                                cr.execute('update muster_roll_register set "DAY5"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==6:
                                cr.execute('update muster_roll_register set "DAY6"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==7:
                                cr.execute('update muster_roll_register set "DAY7"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==8:
                                cr.execute('update muster_roll_register set "DAY8"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==9:
                                cr.execute('update muster_roll_register set "DAY9"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==10:
                                cr.execute('update muster_roll_register set "DAY10"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==11:
                                cr.execute('update muster_roll_register set "DAY11"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==12:
                                cr.execute('update muster_roll_register set "DAY12"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==13:
                                cr.execute('update muster_roll_register set "DAY13"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==14:
                                cr.execute('update muster_roll_register set "DAY14"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==15:
                                cr.execute('update muster_roll_register set "DAY15"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==16:
                                cr.execute('update muster_roll_register set "DAY16"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==17:
                                cr.execute('update muster_roll_register set "DAY17"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==18:
                                cr.execute('update muster_roll_register set "DAY18"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==19:
                                cr.execute('update muster_roll_register set "DAY19"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==20:
                                cr.execute('update muster_roll_register set "DAY20"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==21:
                                cr.execute('update muster_roll_register set "DAY21"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==22:
                                cr.execute('update muster_roll_register set "DAY22"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==23:
                                cr.execute('update muster_roll_register set "DAY23"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==24:
                                cr.execute('update muster_roll_register set "DAY24"=%s where emp_code=%s',(leave_type,emp_code));

                for leave in self.pool.get('hr.holidays').search(cr,uid,[('employee_id','=',employee_id),('date_to_temp','>=',period_end),('date_from_temp','<=',period_end),('type','=','remove'),('state','=','validate')], order='date_from_temp'):
                    for leave_data in self.pool.get('hr.holidays').browse(cr,uid,leave,context=context):
                        
                        emp_code=leave_data.employee_id.emp_code
                        emp_name=leave_data.employee_id.name
                        leave_type=leave_data.holiday_status_id.code
                        day1=datetime.strptime(leave_data.date_from_temp,'%Y-%m-%d').day
                        month1=datetime.strptime(leave_data.date_from_temp,'%Y-%m-%d').month
                        year1=datetime.strptime(leave_data.date_from_temp,'%Y-%m-%d').year
                        day2=datetime.strptime(leave_data.date_to_temp,'%Y-%m-%d').day
                        month2=datetime.strptime(leave_data.date_to_temp,'%Y-%m-%d').month
                        year2=datetime.strptime(leave_data.date_to_temp,'%Y-%m-%d').year
                        d1 = date(year = year1, month = month1, day = day1)
                        d2 = date(year = year2, month = month2, day = 24)
                        delta = d2 - d1
                        present_day=0
                        day=0
                        punch=self.pool.get('final.punch').search(cr,uid,[('date','=',leave_data.date_from_temp),('employee_id','=',leave_data.employee_id.id)], order='date')
                        data = self.pool.get('final.punch').browse(cr,uid,punch,context=context)
                        punch1=self.pool.get('final.punch').search(cr,uid,[('date','=',leave_data.date_to_temp),('employee_id','=',leave_data.employee_id.id)], order='date')
                        data1 = self.pool.get('final.punch').browse(cr,uid,punch1,context=context)
                        if data:
                            present_day=datetime.strptime(data.date,'%Y-%m-%d').day
                        if data1:
                            present_day=datetime.strptime(data1.date,'%Y-%m-%d').day
                        if d1==d2 and (leave_data.second_half_temp==True or leave_data.first_half_temp==True):
                            leave_type = 'H.' + str(leave_data.holiday_status_id.code)
                        for i in range(delta.days + 1):
                            day=(d1 + td(days=i)).day
                            if day==present_day:
                                leave_type = 'H.' + str(leave_data.holiday_status_id.code)
                            else:
                                leave_type=leave_data.holiday_status_id.code
                            if day==25:
                                cr.execute('update muster_roll_register set "DAY25"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==26:
                                cr.execute('update muster_roll_register set "DAY26"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==27:
                                cr.execute('update muster_roll_register set "DAY27"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==28:
                                cr.execute('update muster_roll_register set "DAY28"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==29:
                                cr.execute('update muster_roll_register set "DAY29"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==30:
                                cr.execute('update muster_roll_register set "DAY30"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==31:
                                cr.execute('update muster_roll_register set "DAY31"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==1:
                                cr.execute('update muster_roll_register set "DAY1"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==2:
                                cr.execute('update muster_roll_register set "DAY2"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==3:
                                cr.execute('update muster_roll_register set "DAY3"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==4:
                                cr.execute('update muster_roll_register set "DAY4"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==5:
                                cr.execute('update muster_roll_register set "DAY5"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==6:
                                cr.execute('update muster_roll_register set "DAY6"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==7:
                                cr.execute('update muster_roll_register set "DAY7"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==8:
                                cr.execute('update muster_roll_register set "DAY8"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==9:
                                cr.execute('update muster_roll_register set "DAY9"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==10:
                                cr.execute('update muster_roll_register set "DAY10"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==11:
                                cr.execute('update muster_roll_register set "DAY11"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==12:
                                cr.execute('update muster_roll_register set "DAY12"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==13:
                                cr.execute('update muster_roll_register set "DAY13"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==14:
                                cr.execute('update muster_roll_register set "DAY14"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==15:
                                cr.execute('update muster_roll_register set "DAY15"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==16:
                                cr.execute('update muster_roll_register set "DAY16"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==17:
                                cr.execute('update muster_roll_register set "DAY17"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==18:
                                cr.execute('update muster_roll_register set "DAY18"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==19:
                                cr.execute('update muster_roll_register set "DAY19"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==20:
                                cr.execute('update muster_roll_register set "DAY20"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==21:
                                cr.execute('update muster_roll_register set "DAY21"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==22:
                                cr.execute('update muster_roll_register set "DAY22"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==23:
                                cr.execute('update muster_roll_register set "DAY23"=%s where emp_code=%s',(leave_type,emp_code));
                            if day==24:
                                cr.execute('update muster_roll_register set "DAY24"=%s where emp_code=%s',(leave_type,emp_code));

                for mr_reg in self.pool.get('muster.roll.register').search(cr,uid,[]):
                    for mr_reg_data in self.pool.get('muster.roll.register').browse(cr,uid,mr_reg,context=context):
                        emp_code=mr_reg_data.emp_code
                        
                        value1='CL'
                        value_hcl='H.CL'
                        cr.execute('Select Case When "DAY25" = %s Then 1 Else 0 End + \
                                            Case When "DAY26" = %s Then 1 Else 0 End + \
                                            Case When "DAY27" = %s Then 1 Else 0 End + \
                                            Case When "DAY28" = %s Then 1 Else 0 End + \
                                            Case When "DAY29" = %s Then 1 Else 0 End + \
                                            Case When "DAY30" = %s Then 1 Else 0 End + \
                                            Case When "DAY31" = %s Then 1 Else 0 End + \
                                            Case When "DAY1" = %s Then 1 Else 0 End + \
                                            Case When "DAY2" = %s Then 1 Else 0 End + \
                                            Case When "DAY3" = %s Then 1 Else 0 End + \
                                            Case When "DAY4" = %s Then 1 Else 0 End + \
                                            Case When "DAY5" = %s Then 1 Else 0 End + \
                                            Case When "DAY6" = %s Then 1 Else 0 End + \
                                            Case When "DAY7" = %s Then 1 Else 0 End + \
                                            Case When "DAY8" = %s Then 1 Else 0 End + \
                                            Case When "DAY9" = %s Then 1 Else 0 End + \
                                            Case When "DAY10" = %s Then 1 Else 0 End + \
                                            Case When "DAY11" = %s Then 1 Else 0 End + \
                                            Case When "DAY12" = %s Then 1 Else 0 End + \
                                            Case When "DAY13" = %s Then 1 Else 0 End + \
                                            Case When "DAY14" = %s Then 1 Else 0 End + \
                                            Case When "DAY15" = %s Then 1 Else 0 End + \
                                            Case When "DAY16" = %s Then 1 Else 0 End + \
                                            Case When "DAY17" = %s Then 1 Else 0 End + \
                                            Case When "DAY18" = %s Then 1 Else 0 End + \
                                            Case When "DAY19" = %s Then 1 Else 0 End + \
                                            Case When "DAY20" = %s Then 1 Else 0 End + \
                                            Case When "DAY21" = %s Then 1 Else 0 End + \
                                            Case When "DAY22" = %s Then 1 Else 0 End + \
                                            Case When "DAY23" = %s Then 1 Else 0 End + \
                                            Case When "DAY24" = %s Then 1 Else 0 End as count \
                                        From muster_roll_register where emp_code=%s',(value1,value1,value1,value1,value1,value1,value1,value1,value1,value1,value1,value1,value1,value1,value1,value1,value1,value1,value1,value1,value1,value1,value1,value1,value1,value1,value1,value1,value1,value1,value1,emp_code));
                        c1 = cr.fetchall()
                        cr.execute('Select Case When "DAY25" = %s Then 1 Else 0 End + \
                                            Case When "DAY26" = %s Then 1 Else 0 End + \
                                            Case When "DAY27" = %s Then 1 Else 0 End + \
                                            Case When "DAY28" = %s Then 1 Else 0 End + \
                                            Case When "DAY29" = %s Then 1 Else 0 End + \
                                            Case When "DAY30" = %s Then 1 Else 0 End + \
                                            Case When "DAY31" = %s Then 1 Else 0 End + \
                                            Case When "DAY1" = %s Then 1 Else 0 End + \
                                            Case When "DAY2" = %s Then 1 Else 0 End + \
                                            Case When "DAY3" = %s Then 1 Else 0 End + \
                                            Case When "DAY4" = %s Then 1 Else 0 End + \
                                            Case When "DAY5" = %s Then 1 Else 0 End + \
                                            Case When "DAY6" = %s Then 1 Else 0 End + \
                                            Case When "DAY7" = %s Then 1 Else 0 End + \
                                            Case When "DAY8" = %s Then 1 Else 0 End + \
                                            Case When "DAY9" = %s Then 1 Else 0 End + \
                                            Case When "DAY10" = %s Then 1 Else 0 End + \
                                            Case When "DAY11" = %s Then 1 Else 0 End + \
                                            Case When "DAY12" = %s Then 1 Else 0 End + \
                                            Case When "DAY13" = %s Then 1 Else 0 End + \
                                            Case When "DAY14" = %s Then 1 Else 0 End + \
                                            Case When "DAY15" = %s Then 1 Else 0 End + \
                                            Case When "DAY16" = %s Then 1 Else 0 End + \
                                            Case When "DAY17" = %s Then 1 Else 0 End + \
                                            Case When "DAY18" = %s Then 1 Else 0 End + \
                                            Case When "DAY19" = %s Then 1 Else 0 End + \
                                            Case When "DAY20" = %s Then 1 Else 0 End + \
                                            Case When "DAY21" = %s Then 1 Else 0 End + \
                                            Case When "DAY22" = %s Then 1 Else 0 End + \
                                            Case When "DAY23" = %s Then 1 Else 0 End + \
                                            Case When "DAY24" = %s Then 1 Else 0 End as count \
                                        From muster_roll_register where emp_code=%s',(value_hcl,value_hcl,value_hcl,value_hcl,value_hcl,value_hcl,value_hcl,value_hcl,value_hcl,value_hcl,value_hcl,value_hcl,value_hcl,value_hcl,value_hcl,value_hcl,value_hcl,value_hcl,value_hcl,value_hcl,value_hcl,value_hcl,value_hcl,value_hcl,value_hcl,value_hcl,value_hcl,value_hcl,value_hcl,value_hcl,value_hcl,emp_code));
                        c1_hcl = cr.fetchall()
                        list1 = [int(i[0]) for i in c1]
                        list1_hcl = [int(i[0]) for i in c1_hcl]
                        data1=0
                        data1_hcl=0.0
                        final_data=0.0
                        if len(list1) <> 0:
                            data1 = list1[0]
                        if len(list1_hcl) <> 0:
                            data1_hcl = list1_hcl[0]
                            ex_data1_hcl=float(data1_hcl)/float(2)
                        final_data1=data1+ex_data1_hcl
                        cr.execute('update muster_roll_register set "LEAVE_CL"=%s where emp_code=%s',(final_data1,emp_code));
                        value2='SL'
                        value_sl='H.SL'
                        cr.execute('Select Case When "DAY25" = %s Then 1 Else 0 End + \
                                            Case When "DAY26" = %s Then 1 Else 0 End + \
                                            Case When "DAY27" = %s Then 1 Else 0 End + \
                                            Case When "DAY28" = %s Then 1 Else 0 End + \
                                            Case When "DAY29" = %s Then 1 Else 0 End + \
                                            Case When "DAY30" = %s Then 1 Else 0 End + \
                                            Case When "DAY31" = %s Then 1 Else 0 End + \
                                            Case When "DAY1" = %s Then 1 Else 0 End + \
                                            Case When "DAY2" = %s Then 1 Else 0 End + \
                                            Case When "DAY3" = %s Then 1 Else 0 End + \
                                            Case When "DAY4" = %s Then 1 Else 0 End + \
                                            Case When "DAY5" = %s Then 1 Else 0 End + \
                                            Case When "DAY6" = %s Then 1 Else 0 End + \
                                            Case When "DAY7" = %s Then 1 Else 0 End + \
                                            Case When "DAY8" = %s Then 1 Else 0 End + \
                                            Case When "DAY9" = %s Then 1 Else 0 End + \
                                            Case When "DAY10" = %s Then 1 Else 0 End + \
                                            Case When "DAY11" = %s Then 1 Else 0 End + \
                                            Case When "DAY12" = %s Then 1 Else 0 End + \
                                            Case When "DAY13" = %s Then 1 Else 0 End + \
                                            Case When "DAY14" = %s Then 1 Else 0 End + \
                                            Case When "DAY15" = %s Then 1 Else 0 End + \
                                            Case When "DAY16" = %s Then 1 Else 0 End + \
                                            Case When "DAY17" = %s Then 1 Else 0 End + \
                                            Case When "DAY18" = %s Then 1 Else 0 End + \
                                            Case When "DAY19" = %s Then 1 Else 0 End + \
                                            Case When "DAY20" = %s Then 1 Else 0 End + \
                                            Case When "DAY21" = %s Then 1 Else 0 End + \
                                            Case When "DAY22" = %s Then 1 Else 0 End + \
                                            Case When "DAY23" = %s Then 1 Else 0 End + \
                                            Case When "DAY24" = %s Then 1 Else 0 End as count \
                                        From muster_roll_register where emp_code=%s',(value2,value2,value2,value2,value2,value2,value2,value2,value2,value2,value2,value2,value2,value2,value2,value2,value2,value2,value2,value2,value2,value2,value2,value2,value2,value2,value2,value2,value2,value2,value2,emp_code));
                        c2 = cr.fetchall()
                        cr.execute('Select Case When "DAY25" = %s Then 1 Else 0 End + \
                                            Case When "DAY26" = %s Then 1 Else 0 End + \
                                            Case When "DAY27" = %s Then 1 Else 0 End + \
                                            Case When "DAY28" = %s Then 1 Else 0 End + \
                                            Case When "DAY29" = %s Then 1 Else 0 End + \
                                            Case When "DAY30" = %s Then 1 Else 0 End + \
                                            Case When "DAY31" = %s Then 1 Else 0 End + \
                                            Case When "DAY1" = %s Then 1 Else 0 End + \
                                            Case When "DAY2" = %s Then 1 Else 0 End + \
                                            Case When "DAY3" = %s Then 1 Else 0 End + \
                                            Case When "DAY4" = %s Then 1 Else 0 End + \
                                            Case When "DAY5" = %s Then 1 Else 0 End + \
                                            Case When "DAY6" = %s Then 1 Else 0 End + \
                                            Case When "DAY7" = %s Then 1 Else 0 End + \
                                            Case When "DAY8" = %s Then 1 Else 0 End + \
                                            Case When "DAY9" = %s Then 1 Else 0 End + \
                                            Case When "DAY10" = %s Then 1 Else 0 End + \
                                            Case When "DAY11" = %s Then 1 Else 0 End + \
                                            Case When "DAY12" = %s Then 1 Else 0 End + \
                                            Case When "DAY13" = %s Then 1 Else 0 End + \
                                            Case When "DAY14" = %s Then 1 Else 0 End + \
                                            Case When "DAY15" = %s Then 1 Else 0 End + \
                                            Case When "DAY16" = %s Then 1 Else 0 End + \
                                            Case When "DAY17" = %s Then 1 Else 0 End + \
                                            Case When "DAY18" = %s Then 1 Else 0 End + \
                                            Case When "DAY19" = %s Then 1 Else 0 End + \
                                            Case When "DAY20" = %s Then 1 Else 0 End + \
                                            Case When "DAY21" = %s Then 1 Else 0 End + \
                                            Case When "DAY22" = %s Then 1 Else 0 End + \
                                            Case When "DAY23" = %s Then 1 Else 0 End + \
                                            Case When "DAY24" = %s Then 1 Else 0 End as count \
                                        From muster_roll_register where emp_code=%s',(value_sl,value_sl,value_sl,value_sl,value_sl,value_sl,value_sl,value_sl,value_sl,value_sl,value_sl,value_sl,value_sl,value_sl,value_sl,value_sl,value_sl,value_sl,value_sl,value_sl,value_sl,value_sl,value_sl,value_sl,value_sl,value_sl,value_sl,value_sl,value_sl,value_sl,value_sl,emp_code));
                        c2_sl = cr.fetchall()
                        list2 = [int(i[0]) for i in c2]
                        list2_sl = [int(i[0]) for i in c2_sl]
                        data2=0
                        data2_sl=0.0
                        final_data=0.0
                        if len(list2) <> 0:
                            data2 = list2[0]
                        if len(list2_sl) <> 0:
                            data2_sl = list2_sl[0]
                            ex_data2_sl=float(data2_sl)/float(2)
                        final_data2=data2+ex_data2_sl
                        cr.execute('update muster_roll_register set "LEAVE_SL"=%s where emp_code=%s',(final_data2,emp_code));
                        value3='PL'
                        value_hpl='H.PL'
                        cr.execute('Select Case When "DAY25" = %s Then 1 Else 0 End + \
                                            Case When "DAY26" = %s Then 1 Else 0 End + \
                                            Case When "DAY27" = %s Then 1 Else 0 End + \
                                            Case When "DAY28" = %s Then 1 Else 0 End + \
                                            Case When "DAY29" = %s Then 1 Else 0 End + \
                                            Case When "DAY30" = %s Then 1 Else 0 End + \
                                            Case When "DAY31" = %s Then 1 Else 0 End + \
                                            Case When "DAY1" = %s Then 1 Else 0 End + \
                                            Case When "DAY2" = %s Then 1 Else 0 End + \
                                            Case When "DAY3" = %s Then 1 Else 0 End + \
                                            Case When "DAY4" = %s Then 1 Else 0 End + \
                                            Case When "DAY5" = %s Then 1 Else 0 End + \
                                            Case When "DAY6" = %s Then 1 Else 0 End + \
                                            Case When "DAY7" = %s Then 1 Else 0 End + \
                                            Case When "DAY8" = %s Then 1 Else 0 End + \
                                            Case When "DAY9" = %s Then 1 Else 0 End + \
                                            Case When "DAY10" = %s Then 1 Else 0 End + \
                                            Case When "DAY11" = %s Then 1 Else 0 End + \
                                            Case When "DAY12" = %s Then 1 Else 0 End + \
                                            Case When "DAY13" = %s Then 1 Else 0 End + \
                                            Case When "DAY14" = %s Then 1 Else 0 End + \
                                            Case When "DAY15" = %s Then 1 Else 0 End + \
                                            Case When "DAY16" = %s Then 1 Else 0 End + \
                                            Case When "DAY17" = %s Then 1 Else 0 End + \
                                            Case When "DAY18" = %s Then 1 Else 0 End + \
                                            Case When "DAY19" = %s Then 1 Else 0 End + \
                                            Case When "DAY20" = %s Then 1 Else 0 End + \
                                            Case When "DAY21" = %s Then 1 Else 0 End + \
                                            Case When "DAY22" = %s Then 1 Else 0 End + \
                                            Case When "DAY23" = %s Then 1 Else 0 End + \
                                            Case When "DAY24" = %s Then 1 Else 0 End as count \
                                        From muster_roll_register where emp_code=%s',(value3,value3,value3,value3,value3,value3,value3,value3,value3,value3,value3,value3,value3,value3,value3,value3,value3,value3,value3,value3,value3,value3,value3,value3,value3,value3,value3,value3,value3,value3,value3,emp_code));
                        c3 = cr.fetchall()
                        cr.execute('Select Case When "DAY25" = %s Then 1 Else 0 End + \
                                            Case When "DAY26" = %s Then 1 Else 0 End + \
                                            Case When "DAY27" = %s Then 1 Else 0 End + \
                                            Case When "DAY28" = %s Then 1 Else 0 End + \
                                            Case When "DAY29" = %s Then 1 Else 0 End + \
                                            Case When "DAY30" = %s Then 1 Else 0 End + \
                                            Case When "DAY31" = %s Then 1 Else 0 End + \
                                            Case When "DAY1" = %s Then 1 Else 0 End + \
                                            Case When "DAY2" = %s Then 1 Else 0 End + \
                                            Case When "DAY3" = %s Then 1 Else 0 End + \
                                            Case When "DAY4" = %s Then 1 Else 0 End + \
                                            Case When "DAY5" = %s Then 1 Else 0 End + \
                                            Case When "DAY6" = %s Then 1 Else 0 End + \
                                            Case When "DAY7" = %s Then 1 Else 0 End + \
                                            Case When "DAY8" = %s Then 1 Else 0 End + \
                                            Case When "DAY9" = %s Then 1 Else 0 End + \
                                            Case When "DAY10" = %s Then 1 Else 0 End + \
                                            Case When "DAY11" = %s Then 1 Else 0 End + \
                                            Case When "DAY12" = %s Then 1 Else 0 End + \
                                            Case When "DAY13" = %s Then 1 Else 0 End + \
                                            Case When "DAY14" = %s Then 1 Else 0 End + \
                                            Case When "DAY15" = %s Then 1 Else 0 End + \
                                            Case When "DAY16" = %s Then 1 Else 0 End + \
                                            Case When "DAY17" = %s Then 1 Else 0 End + \
                                            Case When "DAY18" = %s Then 1 Else 0 End + \
                                            Case When "DAY19" = %s Then 1 Else 0 End + \
                                            Case When "DAY20" = %s Then 1 Else 0 End + \
                                            Case When "DAY21" = %s Then 1 Else 0 End + \
                                            Case When "DAY22" = %s Then 1 Else 0 End + \
                                            Case When "DAY23" = %s Then 1 Else 0 End + \
                                            Case When "DAY24" = %s Then 1 Else 0 End as count \
                                        From muster_roll_register where emp_code=%s',(value_hpl,value_hpl,value_hpl,value_hpl,value_hpl,value_hpl,value_hpl,value_hpl,value_hpl,value_hpl,value_hpl,value_hpl,value_hpl,value_hpl,value_hpl,value_hpl,value_hpl,value_hpl,value_hpl,value_hpl,value_hpl,value_hpl,value_hpl,value_hpl,value_hpl,value_hpl,value_hpl,value_hpl,value_hpl,value_hpl,value_hpl,emp_code));
                        c3_hpl = cr.fetchall()
                        list3 = [int(i[0]) for i in c3]
                        list3_hpl = [int(i[0]) for i in c3_hpl]
                        data3=0
                        data3_hpl=0.0
                        final_data=0.0
                        if len(list3) <> 0:
                            data3 = list3[0]
                        if len(list3_hpl) <> 0:
                            data3_hpl = list3_hpl[0]
                            ex_data3_hpl=float(data3_hpl)/float(2)
                        final_data3=data3+ex_data3_hpl
                        cr.execute('update muster_roll_register set "LEAVE_PL"=%s where emp_code=%s',(final_data3,emp_code));
                        value4='CMP'
                        value_hcmp='H.CMP'
                        cr.execute('Select Case When "DAY25" = %s Then 1 Else 0 End + \
                                            Case When "DAY26" = %s Then 1 Else 0 End + \
                                            Case When "DAY27" = %s Then 1 Else 0 End + \
                                            Case When "DAY28" = %s Then 1 Else 0 End + \
                                            Case When "DAY29" = %s Then 1 Else 0 End + \
                                            Case When "DAY30" = %s Then 1 Else 0 End + \
                                            Case When "DAY31" = %s Then 1 Else 0 End + \
                                            Case When "DAY1" = %s Then 1 Else 0 End + \
                                            Case When "DAY2" = %s Then 1 Else 0 End + \
                                            Case When "DAY3" = %s Then 1 Else 0 End + \
                                            Case When "DAY4" = %s Then 1 Else 0 End + \
                                            Case When "DAY5" = %s Then 1 Else 0 End + \
                                            Case When "DAY6" = %s Then 1 Else 0 End + \
                                            Case When "DAY7" = %s Then 1 Else 0 End + \
                                            Case When "DAY8" = %s Then 1 Else 0 End + \
                                            Case When "DAY9" = %s Then 1 Else 0 End + \
                                            Case When "DAY10" = %s Then 1 Else 0 End + \
                                            Case When "DAY11" = %s Then 1 Else 0 End + \
                                            Case When "DAY12" = %s Then 1 Else 0 End + \
                                            Case When "DAY13" = %s Then 1 Else 0 End + \
                                            Case When "DAY14" = %s Then 1 Else 0 End + \
                                            Case When "DAY15" = %s Then 1 Else 0 End + \
                                            Case When "DAY16" = %s Then 1 Else 0 End + \
                                            Case When "DAY17" = %s Then 1 Else 0 End + \
                                            Case When "DAY18" = %s Then 1 Else 0 End + \
                                            Case When "DAY19" = %s Then 1 Else 0 End + \
                                            Case When "DAY20" = %s Then 1 Else 0 End + \
                                            Case When "DAY21" = %s Then 1 Else 0 End + \
                                            Case When "DAY22" = %s Then 1 Else 0 End + \
                                            Case When "DAY23" = %s Then 1 Else 0 End + \
                                            Case When "DAY24" = %s Then 1 Else 0 End as count \
                                        From muster_roll_register where emp_code=%s',(value4,value4,value4,value4,value4,value4,value4,value4,value4,value4,value4,value4,value4,value4,value4,value4,value4,value4,value4,value4,value4,value4,value4,value4,value4,value4,value4,value4,value4,value4,value4,emp_code));
                        c4 = cr.fetchall()
                        cr.execute('Select Case When "DAY25" = %s Then 1 Else 0 End + \
                                            Case When "DAY26" = %s Then 1 Else 0 End + \
                                            Case When "DAY27" = %s Then 1 Else 0 End + \
                                            Case When "DAY28" = %s Then 1 Else 0 End + \
                                            Case When "DAY29" = %s Then 1 Else 0 End + \
                                            Case When "DAY30" = %s Then 1 Else 0 End + \
                                            Case When "DAY31" = %s Then 1 Else 0 End + \
                                            Case When "DAY1" = %s Then 1 Else 0 End + \
                                            Case When "DAY2" = %s Then 1 Else 0 End + \
                                            Case When "DAY3" = %s Then 1 Else 0 End + \
                                            Case When "DAY4" = %s Then 1 Else 0 End + \
                                            Case When "DAY5" = %s Then 1 Else 0 End + \
                                            Case When "DAY6" = %s Then 1 Else 0 End + \
                                            Case When "DAY7" = %s Then 1 Else 0 End + \
                                            Case When "DAY8" = %s Then 1 Else 0 End + \
                                            Case When "DAY9" = %s Then 1 Else 0 End + \
                                            Case When "DAY10" = %s Then 1 Else 0 End + \
                                            Case When "DAY11" = %s Then 1 Else 0 End + \
                                            Case When "DAY12" = %s Then 1 Else 0 End + \
                                            Case When "DAY13" = %s Then 1 Else 0 End + \
                                            Case When "DAY14" = %s Then 1 Else 0 End + \
                                            Case When "DAY15" = %s Then 1 Else 0 End + \
                                            Case When "DAY16" = %s Then 1 Else 0 End + \
                                            Case When "DAY17" = %s Then 1 Else 0 End + \
                                            Case When "DAY18" = %s Then 1 Else 0 End + \
                                            Case When "DAY19" = %s Then 1 Else 0 End + \
                                            Case When "DAY20" = %s Then 1 Else 0 End + \
                                            Case When "DAY21" = %s Then 1 Else 0 End + \
                                            Case When "DAY22" = %s Then 1 Else 0 End + \
                                            Case When "DAY23" = %s Then 1 Else 0 End + \
                                            Case When "DAY24" = %s Then 1 Else 0 End as count \
                                        From muster_roll_register where emp_code=%s',(value_hcmp,value_hcmp,value_hcmp,value_hcmp,value_hcmp,value_hcmp,value_hcmp,value_hcmp,value_hcmp,value_hcmp,value_hcmp,value_hcmp,value_hcmp,value_hcmp,value_hcmp,value_hcmp,value_hcmp,value_hcmp,value_hcmp,value_hcmp,value_hcmp,value_hcmp,value_hcmp,value_hcmp,value_hcmp,value_hcmp,value_hcmp,value_hcmp,value_hcmp,value_hcmp,value_hcmp,emp_code));
                        c4_cmp = cr.fetchall()
                        list4 = [int(i[0]) for i in c4]
                        list4_hcmp = [int(i[0]) for i in c4_cmp]
                        data4=0
                        data4_hcmp=0.0
                        final_data=0.0
                        if len(list4) <> 0:
                            data4 = list4[0]
                        if len(list4_hcmp) <> 0:
                            data4_hcmp = list4_hcmp[0]
                            ex_data4_hcmp=float(data4_hcmp)/float(2)
                        final_data4=data4+ex_data4_hcmp
                        cr.execute('update muster_roll_register set "LEAVE_CMP"=%s where emp_code=%s',(final_data4,emp_code));
                        value5='NHD'
                        cr.execute('Select Case When "DAY25" = %s Then 1 Else 0 End + \
                                            Case When "DAY26" = %s Then 1 Else 0 End + \
                                            Case When "DAY27" = %s Then 1 Else 0 End + \
                                            Case When "DAY28" = %s Then 1 Else 0 End + \
                                            Case When "DAY29" = %s Then 1 Else 0 End + \
                                            Case When "DAY30" = %s Then 1 Else 0 End + \
                                            Case When "DAY31" = %s Then 1 Else 0 End + \
                                            Case When "DAY1" = %s Then 1 Else 0 End + \
                                            Case When "DAY2" = %s Then 1 Else 0 End + \
                                            Case When "DAY3" = %s Then 1 Else 0 End + \
                                            Case When "DAY4" = %s Then 1 Else 0 End + \
                                            Case When "DAY5" = %s Then 1 Else 0 End + \
                                            Case When "DAY6" = %s Then 1 Else 0 End + \
                                            Case When "DAY7" = %s Then 1 Else 0 End + \
                                            Case When "DAY8" = %s Then 1 Else 0 End + \
                                            Case When "DAY9" = %s Then 1 Else 0 End + \
                                            Case When "DAY10" = %s Then 1 Else 0 End + \
                                            Case When "DAY11" = %s Then 1 Else 0 End + \
                                            Case When "DAY12" = %s Then 1 Else 0 End + \
                                            Case When "DAY13" = %s Then 1 Else 0 End + \
                                            Case When "DAY14" = %s Then 1 Else 0 End + \
                                            Case When "DAY15" = %s Then 1 Else 0 End + \
                                            Case When "DAY16" = %s Then 1 Else 0 End + \
                                            Case When "DAY17" = %s Then 1 Else 0 End + \
                                            Case When "DAY18" = %s Then 1 Else 0 End + \
                                            Case When "DAY19" = %s Then 1 Else 0 End + \
                                            Case When "DAY20" = %s Then 1 Else 0 End + \
                                            Case When "DAY21" = %s Then 1 Else 0 End + \
                                            Case When "DAY22" = %s Then 1 Else 0 End + \
                                            Case When "DAY23" = %s Then 1 Else 0 End + \
                                            Case When "DAY24" = %s Then 1 Else 0 End as count \
                                        From muster_roll_register where emp_code=%s',(value5,value5,value5,value5,value5,value5,value5,value5,value5,value5,value5,value5,value5,value5,value5,value5,value5,value5,value5,value5,value5,value5,value5,value5,value5,value5,value5,value5,value5,value5,value5,emp_code));
                        c5 = cr.fetchall()
                        list5 = [int(i[0]) for i in c5]
                        data5=0
                        if len(list5) <> 0:
                            data5 = list5[0]
                        cr.execute('update muster_roll_register set "TOLAL_OFF_NHD"=%s where emp_code=%s',(data5,emp_code));
                        value6='P'
                        cr.execute('Select Case When "DAY25" = %s Then 1 Else 0 End + \
                                            Case When "DAY26" = %s Then 1 Else 0 End + \
                                            Case When "DAY27" = %s Then 1 Else 0 End + \
                                            Case When "DAY28" = %s Then 1 Else 0 End + \
                                            Case When "DAY29" = %s Then 1 Else 0 End + \
                                            Case When "DAY30" = %s Then 1 Else 0 End + \
                                            Case When "DAY31" = %s Then 1 Else 0 End + \
                                            Case When "DAY1" = %s Then 1 Else 0 End + \
                                            Case When "DAY2" = %s Then 1 Else 0 End + \
                                            Case When "DAY3" = %s Then 1 Else 0 End + \
                                            Case When "DAY4" = %s Then 1 Else 0 End + \
                                            Case When "DAY5" = %s Then 1 Else 0 End + \
                                            Case When "DAY6" = %s Then 1 Else 0 End + \
                                            Case When "DAY7" = %s Then 1 Else 0 End + \
                                            Case When "DAY8" = %s Then 1 Else 0 End + \
                                            Case When "DAY9" = %s Then 1 Else 0 End + \
                                            Case When "DAY10" = %s Then 1 Else 0 End + \
                                            Case When "DAY11" = %s Then 1 Else 0 End + \
                                            Case When "DAY12" = %s Then 1 Else 0 End + \
                                            Case When "DAY13" = %s Then 1 Else 0 End + \
                                            Case When "DAY14" = %s Then 1 Else 0 End + \
                                            Case When "DAY15" = %s Then 1 Else 0 End + \
                                            Case When "DAY16" = %s Then 1 Else 0 End + \
                                            Case When "DAY17" = %s Then 1 Else 0 End + \
                                            Case When "DAY18" = %s Then 1 Else 0 End + \
                                            Case When "DAY19" = %s Then 1 Else 0 End + \
                                            Case When "DAY20" = %s Then 1 Else 0 End + \
                                            Case When "DAY21" = %s Then 1 Else 0 End + \
                                            Case When "DAY22" = %s Then 1 Else 0 End + \
                                            Case When "DAY23" = %s Then 1 Else 0 End + \
                                            Case When "DAY24" = %s Then 1 Else 0 End as count \
                                        From muster_roll_register where emp_code=%s',(value6,value6,value6,value6,value6,value6,value6,value6,value6,value6,value6,value6,value6,value6,value6,value6,value6,value6,value6,value6,value6,value6,value6,value6,value6,value6,value6,value6,value6,value6,value6,emp_code));
                        c6 = cr.fetchall()
                        list6 = [int(i[0]) for i in c6]
                        data6=0
                        if len(list6) <> 0:
                            data6 = list6[0]
                        cr.execute('update muster_roll_register set "TOTAL_P"=%s,"TWD"=%s where emp_code=%s',(data6,data6,emp_code));
                        data7 = data6+data1+data2+data3+data4
                twd1=31-(final_data1+final_data2+final_data3+difference)
                twd2=31-(-diff)-(final_data1+final_data2+final_data3+difference)
                tdp=twd2+(final_data1+final_data2+final_data3)
                if difference>0:
                    val='N/A'
                    joining_day=datetime.strptime(emp_id.joining_date, '%Y-%m-%d').day
                    if joining_day==26:
                        cr.execute('update muster_roll_register set "DAY25"=%s where emp_code=%s',(val,emp_code));
                    if joining_day==27:
                        cr.execute('update muster_roll_register set "DAY25"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY26"=%s where emp_code=%s',(val,emp_code));
                    if joining_day==28:
                        cr.execute('update muster_roll_register set "DAY25"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY26"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY27"=%s where emp_code=%s',(val,emp_code));
                    if joining_day==29:
                        cr.execute('update muster_roll_register set "DAY25"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY26"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY27"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY28"=%s where emp_code=%s',(val,emp_code));
                    if joining_day==30:
                        cr.execute('update muster_roll_register set "DAY25"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY26"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY27"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY28"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY29"=%s where emp_code=%s',(val,emp_code));
                    if joining_day==31:
                        cr.execute('update muster_roll_register set "DAY25"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY26"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY27"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY28"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY29"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY30"=%s where emp_code=%s',(val,emp_code));
                    if joining_day==1:
                        cr.execute('update muster_roll_register set "DAY25"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY26"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY27"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY28"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY29"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY30"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY31"=%s where emp_code=%s',(val,emp_code));
                    if joining_day==2:
                        cr.execute('update muster_roll_register set "DAY25"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY26"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY27"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY28"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY29"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY30"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY31"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY1"=%s where emp_code=%s',(val,emp_code));
                    if joining_day==3:
                        cr.execute('update muster_roll_register set "DAY25"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY26"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY27"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY28"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY29"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY30"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY31"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY1"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY2"=%s where emp_code=%s',(val,emp_code));
                    if joining_day==4:
                        cr.execute('update muster_roll_register set "DAY25"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY26"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY27"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY28"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY29"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY30"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY31"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY1"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY2"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY3"=%s where emp_code=%s',(val,emp_code));
                    if joining_day==5:
                        cr.execute('update muster_roll_register set "DAY25"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY26"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY27"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY28"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY29"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY30"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY31"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY1"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY2"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY3"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY4"=%s where emp_code=%s',(val,emp_code));
                    if joining_day==6:
                        cr.execute('update muster_roll_register set "DAY25"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY26"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY27"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY28"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY29"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY30"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY31"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY1"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY2"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY3"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY4"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY5"=%s where emp_code=%s',(val,emp_code));
                    if joining_day==7:
                        cr.execute('update muster_roll_register set "DAY25"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY26"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY27"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY28"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY29"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY30"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY31"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY1"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY2"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY3"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY4"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY5"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY6"=%s where emp_code=%s',(val,emp_code));
                    if joining_day==8:
                        cr.execute('update muster_roll_register set "DAY25"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY26"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY27"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY28"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY29"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY30"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY31"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY1"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY2"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY3"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY4"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY5"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY6"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY7"=%s where emp_code=%s',(val,emp_code));
                    if joining_day==9:
                        cr.execute('update muster_roll_register set "DAY25"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY26"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY27"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY28"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY29"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY30"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY31"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY1"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY2"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY3"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY4"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY5"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY6"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY7"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY8"=%s where emp_code=%s',(val,emp_code));
                    if joining_day==10:
                        cr.execute('update muster_roll_register set "DAY25"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY26"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY27"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY28"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY29"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY30"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY31"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY1"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY2"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY3"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY4"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY5"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY6"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY7"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY8"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY9"=%s where emp_code=%s',(val,emp_code));
                    if joining_day==11:
                        cr.execute('update muster_roll_register set "DAY25"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY26"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY27"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY28"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY29"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY30"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY31"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY1"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY2"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY3"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY4"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY5"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY6"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY7"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY8"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY9"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY10"=%s where emp_code=%s',(val,emp_code));
                    if joining_day==12:
                        cr.execute('update muster_roll_register set "DAY25"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY26"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY27"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY28"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY29"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY30"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY31"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY1"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY2"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY3"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY4"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY5"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY6"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY7"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY8"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY9"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY10"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY11"=%s where emp_code=%s',(val,emp_code));
                    if joining_day==13:
                        cr.execute('update muster_roll_register set "DAY25"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY26"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY27"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY28"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY29"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY30"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY31"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY1"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY2"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY3"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY4"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY5"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY6"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY7"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY8"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY9"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY10"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY11"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY12"=%s where emp_code=%s',(val,emp_code));
                        
                    if joining_day==14:
                        cr.execute('update muster_roll_register set "DAY25"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY26"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY27"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY28"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY29"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY30"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY31"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY1"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY2"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY3"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY4"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY5"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY6"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY7"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY8"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY9"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY10"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY11"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY12"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY13"=%s where emp_code=%s',(val,emp_code));
                    if joining_day==15:
                        cr.execute('update muster_roll_register set "DAY25"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY26"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY27"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY28"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY29"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY30"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY31"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY1"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY2"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY3"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY4"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY5"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY6"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY7"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY8"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY9"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY10"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY11"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY12"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY13"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY14"=%s where emp_code=%s',(val,emp_code));
                    if joining_day==16:
                        cr.execute('update muster_roll_register set "DAY25"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY26"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY27"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY28"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY29"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY30"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY31"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY1"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY2"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY3"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY4"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY5"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY6"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY7"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY8"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY9"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY10"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY11"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY12"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY13"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY14"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY15"=%s where emp_code=%s',(val,emp_code));
                        
                    if joining_day==17:
                        cr.execute('update muster_roll_register set "DAY25"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY26"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY27"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY28"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY29"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY30"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY31"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY1"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY2"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY3"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY4"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY5"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY6"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY7"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY8"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY9"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY10"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY11"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY12"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY13"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY14"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY15"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY16"=%s where emp_code=%s',(val,emp_code));
                    if joining_day==18:
                        cr.execute('update muster_roll_register set "DAY25"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY26"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY27"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY28"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY29"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY30"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY31"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY1"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY2"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY3"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY4"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY5"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY6"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY7"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY8"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY9"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY10"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY11"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY12"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY13"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY14"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY15"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY16"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY17"=%s where emp_code=%s',(val,emp_code));
                    if joining_day==19:
                        cr.execute('update muster_roll_register set "DAY25"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY26"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY27"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY28"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY29"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY30"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY31"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY1"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY2"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY3"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY4"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY5"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY6"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY7"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY8"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY9"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY10"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY11"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY12"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY13"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY14"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY15"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY16"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY17"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY18"=%s where emp_code=%s',(val,emp_code));
                    if joining_day==20:
                        cr.execute('update muster_roll_register set "DAY25"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY26"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY27"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY28"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY29"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY30"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY31"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY1"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY2"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY3"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY4"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY5"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY6"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY7"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY8"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY9"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY10"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY11"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY12"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY13"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY14"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY15"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY16"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY17"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY18"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY19"=%s where emp_code=%s',(val,emp_code));
                    if joining_day==21:
                        cr.execute('update muster_roll_register set "DAY25"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY26"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY27"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY28"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY29"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY30"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY31"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY1"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY2"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY3"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY4"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY5"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY6"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY7"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY8"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY9"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY10"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY11"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY12"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY13"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY14"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY15"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY16"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY17"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY18"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY19"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY20"=%s where emp_code=%s',(val,emp_code));
                    if joining_day==22:
                        cr.execute('update muster_roll_register set "DAY25"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY26"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY27"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY28"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY29"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY30"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY31"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY1"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY2"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY3"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY4"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY5"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY6"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY7"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY8"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY9"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY10"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY11"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY12"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY13"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY14"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY15"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY16"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY17"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY18"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY19"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY20"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY21"=%s where emp_code=%s',(val,emp_code));
                    if joining_day==23:
                        cr.execute('update muster_roll_register set "DAY25"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY26"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY27"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY28"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY29"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY30"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY31"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY1"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY2"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY3"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY4"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY5"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY6"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY7"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY8"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY9"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY10"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY11"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY12"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY13"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY14"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY15"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY16"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY17"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY18"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY19"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY20"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY21"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY22"=%s where emp_code=%s',(val,emp_code));
                    if joining_day==24:
                        cr.execute('update muster_roll_register set "DAY25"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY26"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY27"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY28"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY29"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY30"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY31"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY1"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY2"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY3"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY4"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY5"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY6"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY7"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY8"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY9"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY10"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY11"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY12"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY13"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY14"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY15"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY16"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY17"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY18"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY19"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY20"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY21"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY22"=%s where emp_code=%s',(val,emp_code));
                        cr.execute('update muster_roll_register set "DAY23"=%s where emp_code=%s',(val,emp_code));
                    remarks='New joinee as on date' + ' ' + str(joining_date)
                    cr.execute('update muster_roll_register set "TWD1"=%s,"TWD2"=%s,"TDP"=%s,"REMARKS"=%s where emp_code=%s',(twd1,twd2,tdp,remarks,emp_code));
                value='LWP'
                cr.execute('update muster_roll_register set "DAY25"=%s where emp_code=%s and "DAY25" is null',(value,emp_code));
                cr.execute('update muster_roll_register set "DAY26"=%s where emp_code=%s and "DAY26" is null',(value,emp_code));
                cr.execute('update muster_roll_register set "DAY27"=%s where emp_code=%s and "DAY27" is null',(value,emp_code));
                cr.execute('update muster_roll_register set "DAY28"=%s where emp_code=%s and "DAY28" is null',(value,emp_code));
                cr.execute('update muster_roll_register set "DAY29"=%s where emp_code=%s and "DAY29" is null',(value,emp_code));
                cr.execute('update muster_roll_register set "DAY30"=%s where emp_code=%s and "DAY30" is null',(value,emp_code));
                cr.execute('update muster_roll_register set "DAY31"=%s where emp_code=%s and "DAY31" is null',(value,emp_code));
                cr.execute('update muster_roll_register set "DAY1"=%s where emp_code=%s and "DAY1" is null',(value,emp_code));
                cr.execute('update muster_roll_register set "DAY2"=%s where emp_code=%s and "DAY2" is null',(value,emp_code));
                cr.execute('update muster_roll_register set "DAY3"=%s where emp_code=%s and "DAY3" is null',(value,emp_code));
                cr.execute('update muster_roll_register set "DAY4"=%s where emp_code=%s and "DAY4" is null',(value,emp_code));
                cr.execute('update muster_roll_register set "DAY5"=%s where emp_code=%s and "DAY5" is null',(value,emp_code));
                cr.execute('update muster_roll_register set "DAY6"=%s where emp_code=%s and "DAY6" is null',(value,emp_code));
                cr.execute('update muster_roll_register set "DAY7"=%s where emp_code=%s and "DAY7" is null',(value,emp_code));
                cr.execute('update muster_roll_register set "DAY8"=%s where emp_code=%s and "DAY8" is null',(value,emp_code));
                cr.execute('update muster_roll_register set "DAY9"=%s where emp_code=%s and "DAY9" is null',(value,emp_code));
                cr.execute('update muster_roll_register set "DAY10"=%s where emp_code=%s and "DAY10" is null',(value,emp_code));
                cr.execute('update muster_roll_register set "DAY11"=%s where emp_code=%s and "DAY11" is null',(value,emp_code));
                cr.execute('update muster_roll_register set "DAY12"=%s where emp_code=%s and "DAY12" is null',(value,emp_code));
                cr.execute('update muster_roll_register set "DAY13"=%s where emp_code=%s and "DAY13" is null',(value,emp_code));
                cr.execute('update muster_roll_register set "DAY14"=%s where emp_code=%s and "DAY14" is null',(value,emp_code));
                cr.execute('update muster_roll_register set "DAY15"=%s where emp_code=%s and "DAY15" is null',(value,emp_code));
                cr.execute('update muster_roll_register set "DAY16"=%s where emp_code=%s and "DAY16" is null',(value,emp_code));
                cr.execute('update muster_roll_register set "DAY17"=%s where emp_code=%s and "DAY17" is null',(value,emp_code));
                cr.execute('update muster_roll_register set "DAY18"=%s where emp_code=%s and "DAY18" is null',(value,emp_code));
                cr.execute('update muster_roll_register set "DAY19"=%s where emp_code=%s and "DAY19" is null',(value,emp_code));
                cr.execute('update muster_roll_register set "DAY20"=%s where emp_code=%s and "DAY20" is null',(value,emp_code));
                cr.execute('update muster_roll_register set "DAY21"=%s where emp_code=%s and "DAY21" is null',(value,emp_code));
                cr.execute('update muster_roll_register set "DAY22"=%s where emp_code=%s and "DAY22" is null',(value,emp_code));
                cr.execute('update muster_roll_register set "DAY23"=%s where emp_code=%s and "DAY23" is null',(value,emp_code));
                cr.execute('update muster_roll_register set "DAY24"=%s where emp_code=%s and "DAY24" is null',(value,emp_code));
                ################################################
                day_val='LWP'
                day_val_sat='XTD'
                day_val_sun='D'
                if month in [5,7,10,12]:
                    cr.execute('update muster_roll_register set "DAY26"=%s,"DAY27"=%s where "DAY25"=%s and "DAY28"=%s and "DAY26"=%s and "DAY27"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY27"=%s,"DAY28"=%s where "DAY26"=%s and "DAY29"=%s and "DAY27"=%s and "DAY28"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY28"=%s,"DAY29"=%s where "DAY27"=%s and "DAY30"=%s and "DAY28"=%s and "DAY29"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY29"=%s,"DAY30"=%s where "DAY28"=%s and "DAY1"=%s and "DAY29"=%s and "DAY30"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY30"=%s,"DAY1"=%s where "DAY29"=%s and "DAY2"=%s and "DAY30"=%s and "DAY1"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY1"=%s,"DAY2"=%s where "DAY30"=%s and "DAY3"=%s and "DAY1"=%s and "DAY2"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY2"=%s,"DAY3"=%s where "DAY1"=%s and "DAY4"=%s and "DAY2"=%s and "DAY3"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY3"=%s,"DAY4"=%s where "DAY2"=%s and "DAY5"=%s and "DAY3"=%s and "DAY4"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY4"=%s,"DAY5"=%s where "DAY3"=%s and "DAY6"=%s and "DAY4"=%s and "DAY5"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY5"=%s,"DAY6"=%s where "DAY4"=%s and "DAY7"=%s and "DAY5"=%s and "DAY6"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY6"=%s,"DAY7"=%s where "DAY5"=%s and "DAY8"=%s and "DAY6"=%s and "DAY7"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY7"=%s,"DAY8"=%s where "DAY6"=%s and "DAY9"=%s and "DAY7"=%s and "DAY8"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY8"=%s,"DAY9"=%s where "DAY7"=%s and "DAY10"=%s and "DAY8"=%s and "DAY9"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY9"=%s,"DAY10"=%s where "DAY8"=%s and "DAY11"=%s and "DAY9"=%s and "DAY10"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY10"=%s,"DAY11"=%s where "DAY9"=%s and "DAY12"=%s and "DAY10"=%s and "DAY11"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY11"=%s,"DAY12"=%s where "DAY10"=%s and "DAY13"=%s and "DAY11"=%s and "DAY12"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY12"=%s,"DAY13"=%s where "DAY11"=%s and "DAY14"=%s and "DAY12"=%s and "DAY13"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY13"=%s,"DAY14"=%s where "DAY12"=%s and "DAY15"=%s and "DAY13"=%s and "DAY14"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY14"=%s,"DAY15"=%s where "DAY13"=%s and "DAY16"=%s and "DAY14"=%s and "DAY15"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY15"=%s,"DAY16"=%s where "DAY14"=%s and "DAY17"=%s and "DAY15"=%s and "DAY16"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY16"=%s,"DAY17"=%s where "DAY15"=%s and "DAY18"=%s and "DAY16"=%s and "DAY17"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY17"=%s,"DAY18"=%s where "DAY16"=%s and "DAY19"=%s and "DAY17"=%s and "DAY18"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY18"=%s,"DAY19"=%s where "DAY17"=%s and "DAY20"=%s and "DAY18"=%s and "DAY19"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY19"=%s,"DAY20"=%s where "DAY18"=%s and "DAY21"=%s and "DAY19"=%s and "DAY20"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY20"=%s,"DAY21"=%s where "DAY19"=%s and "DAY22"=%s and "DAY20"=%s and "DAY21"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY21"=%s,"DAY22"=%s where "DAY20"=%s and "DAY23"=%s and "DAY21"=%s and "DAY22"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY22"=%s,"DAY23"=%s where "DAY21"=%s and "DAY24"=%s and "DAY22"=%s and "DAY23"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                if month not in [3,5,7,10,12]:
                    cr.execute('update muster_roll_register set "DAY26"=%s,"DAY27"=%s where "DAY25"=%s and "DAY28"=%s and "DAY26"=%s and "DAY27"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY27"=%s,"DAY28"=%s where "DAY26"=%s and "DAY29"=%s and "DAY27"=%s and "DAY28"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY28"=%s,"DAY29"=%s where "DAY27"=%s and "DAY30"=%s and "DAY28"=%s and "DAY29"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY29"=%s,"DAY30"=%s where "DAY28"=%s and "DAY31"=%s and "DAY29"=%s and "DAY30"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY30"=%s,"DAY31"=%s where "DAY29"=%s and "DAY1"=%s and "DAY30"=%s and "DAY31"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY31"=%s,"DAY1"=%s where "DAY30"=%s and "DAY2"=%s and "DAY31"=%s and "DAY1"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY1"=%s,"DAY2"=%s where "DAY31"=%s and "DAY3"=%s and "DAY1"=%s and "DAY2"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY2"=%s,"DAY3"=%s where "DAY1"=%s and "DAY4"=%s and "DAY2"=%s and "DAY3"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY3"=%s,"DAY4"=%s where "DAY2"=%s and "DAY5"=%s and "DAY3"=%s and "DAY4"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY4"=%s,"DAY5"=%s where "DAY3"=%s and "DAY6"=%s and "DAY4"=%s and "DAY5"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY5"=%s,"DAY6"=%s where "DAY4"=%s and "DAY7"=%s and "DAY5"=%s and "DAY6"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY6"=%s,"DAY7"=%s where "DAY5"=%s and "DAY8"=%s and "DAY6"=%s and "DAY7"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY7"=%s,"DAY8"=%s where "DAY6"=%s and "DAY9"=%s and "DAY7"=%s and "DAY8"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY8"=%s,"DAY9"=%s where "DAY7"=%s and "DAY10"=%s and "DAY8"=%s and "DAY9"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY9"=%s,"DAY10"=%s where "DAY8"=%s and "DAY11"=%s and "DAY9"=%s and "DAY10"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY10"=%s,"DAY11"=%s where "DAY9"=%s and "DAY12"=%s and "DAY10"=%s and "DAY11"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY11"=%s,"DAY12"=%s where "DAY10"=%s and "DAY13"=%s and "DAY11"=%s and "DAY12"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY12"=%s,"DAY13"=%s where "DAY11"=%s and "DAY14"=%s and "DAY12"=%s and "DAY13"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY13"=%s,"DAY14"=%s where "DAY12"=%s and "DAY15"=%s and "DAY13"=%s and "DAY14"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY14"=%s,"DAY15"=%s where "DAY13"=%s and "DAY16"=%s and "DAY14"=%s and "DAY15"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY15"=%s,"DAY16"=%s where "DAY14"=%s and "DAY17"=%s and "DAY15"=%s and "DAY16"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY16"=%s,"DAY17"=%s where "DAY15"=%s and "DAY18"=%s and "DAY16"=%s and "DAY17"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY17"=%s,"DAY18"=%s where "DAY16"=%s and "DAY19"=%s and "DAY17"=%s and "DAY18"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY18"=%s,"DAY19"=%s where "DAY17"=%s and "DAY20"=%s and "DAY18"=%s and "DAY19"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY19"=%s,"DAY20"=%s where "DAY18"=%s and "DAY21"=%s and "DAY19"=%s and "DAY20"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY20"=%s,"DAY21"=%s where "DAY19"=%s and "DAY22"=%s and "DAY20"=%s and "DAY21"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY21"=%s,"DAY22"=%s where "DAY20"=%s and "DAY23"=%s and "DAY21"=%s and "DAY22"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY22"=%s,"DAY23"=%s where "DAY21"=%s and "DAY24"=%s and "DAY22"=%s and "DAY23"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                if month==3:
                    cr.execute('update muster_roll_register set "DAY26"=%s,"DAY27"=%s where "DAY25"=%s and "DAY28"=%s and "DAY26"=%s and "DAY27"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY27"=%s,"DAY28"=%s where "DAY26"=%s and "DAY1"=%s and "DAY27"=%s and "DAY28"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY28"=%s,"DAY1"=%s where "DAY27"=%s and "DAY2"=%s and "DAY28"=%s and "DAY1"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY1"=%s,"DAY2"=%s where "DAY28"=%s and "DAY3"=%s and "DAY1"=%s and "DAY2"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY2"=%s,"DAY3"=%s where "DAY1"=%s and "DAY4"=%s and "DAY2"=%s and "DAY3"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY3"=%s,"DAY4"=%s where "DAY2"=%s and "DAY5"=%s and "DAY3"=%s and "DAY4"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY4"=%s,"DAY5"=%s where "DAY3"=%s and "DAY6"=%s and "DAY4"=%s and "DAY5"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY5"=%s,"DAY6"=%s where "DAY4"=%s and "DAY7"=%s and "DAY5"=%s and "DAY6"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY6"=%s,"DAY7"=%s where "DAY5"=%s and "DAY8"=%s and "DAY6"=%s and "DAY7"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY7"=%s,"DAY8"=%s where "DAY6"=%s and "DAY9"=%s and "DAY7"=%s and "DAY8"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY8"=%s,"DAY9"=%s where "DAY7"=%s and "DAY10"=%s and "DAY8"=%s and "DAY9"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY9"=%s,"DAY10"=%s where "DAY8"=%s and "DAY11"=%s and "DAY9"=%s and "DAY10"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY10"=%s,"DAY11"=%s where "DAY9"=%s and "DAY12"=%s and "DAY10"=%s and "DAY11"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY11"=%s,"DAY12"=%s where "DAY10"=%s and "DAY13"=%s and "DAY11"=%s and "DAY12"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY12"=%s,"DAY13"=%s where "DAY11"=%s and "DAY14"=%s and "DAY12"=%s and "DAY13"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY13"=%s,"DAY14"=%s where "DAY12"=%s and "DAY15"=%s and "DAY13"=%s and "DAY14"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY14"=%s,"DAY15"=%s where "DAY13"=%s and "DAY16"=%s and "DAY14"=%s and "DAY15"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY15"=%s,"DAY16"=%s where "DAY14"=%s and "DAY17"=%s and "DAY15"=%s and "DAY16"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY16"=%s,"DAY17"=%s where "DAY15"=%s and "DAY18"=%s and "DAY16"=%s and "DAY17"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY17"=%s,"DAY18"=%s where "DAY16"=%s and "DAY19"=%s and "DAY17"=%s and "DAY18"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY18"=%s,"DAY19"=%s where "DAY17"=%s and "DAY20"=%s and "DAY18"=%s and "DAY19"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY19"=%s,"DAY20"=%s where "DAY18"=%s and "DAY21"=%s and "DAY19"=%s and "DAY20"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY20"=%s,"DAY21"=%s where "DAY19"=%s and "DAY22"=%s and "DAY20"=%s and "DAY21"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY21"=%s,"DAY22"=%s where "DAY20"=%s and "DAY23"=%s and "DAY21"=%s and "DAY22"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));
                    cr.execute('update muster_roll_register set "DAY22"=%s,"DAY23"=%s where "DAY21"=%s and "DAY24"=%s and "DAY22"=%s and "DAY23"=%s',(day_val,day_val,day_val,day_val,day_val_sat,day_val_sun));

                ################################################
                value_lwp='LWP'
                value_hlwp='H.LWP'
                cr.execute('Select Case When "DAY25" = %s Then 1 Else 0 End + \
                                    Case When "DAY26" = %s Then 1 Else 0 End + \
                                    Case When "DAY27" = %s Then 1 Else 0 End + \
                                    Case When "DAY28" = %s Then 1 Else 0 End + \
                                    Case When "DAY29" = %s Then 1 Else 0 End + \
                                    Case When "DAY30" = %s Then 1 Else 0 End + \
                                    Case When "DAY31" = %s Then 1 Else 0 End + \
                                    Case When "DAY1" = %s Then 1 Else 0 End + \
                                    Case When "DAY2" = %s Then 1 Else 0 End + \
                                    Case When "DAY3" = %s Then 1 Else 0 End + \
                                    Case When "DAY4" = %s Then 1 Else 0 End + \
                                    Case When "DAY5" = %s Then 1 Else 0 End + \
                                    Case When "DAY6" = %s Then 1 Else 0 End + \
                                    Case When "DAY7" = %s Then 1 Else 0 End + \
                                    Case When "DAY8" = %s Then 1 Else 0 End + \
                                    Case When "DAY9" = %s Then 1 Else 0 End + \
                                    Case When "DAY10" = %s Then 1 Else 0 End + \
                                    Case When "DAY11" = %s Then 1 Else 0 End + \
                                    Case When "DAY12" = %s Then 1 Else 0 End + \
                                    Case When "DAY13" = %s Then 1 Else 0 End + \
                                    Case When "DAY14" = %s Then 1 Else 0 End + \
                                    Case When "DAY15" = %s Then 1 Else 0 End + \
                                    Case When "DAY16" = %s Then 1 Else 0 End + \
                                    Case When "DAY17" = %s Then 1 Else 0 End + \
                                    Case When "DAY18" = %s Then 1 Else 0 End + \
                                    Case When "DAY19" = %s Then 1 Else 0 End + \
                                    Case When "DAY20" = %s Then 1 Else 0 End + \
                                    Case When "DAY21" = %s Then 1 Else 0 End + \
                                    Case When "DAY22" = %s Then 1 Else 0 End + \
                                    Case When "DAY23" = %s Then 1 Else 0 End + \
                                    Case When "DAY24" = %s Then 1 Else 0 End as count \
                                From muster_roll_register where emp_code=%s',(value_lwp,value_lwp,value_lwp,value_lwp,value_lwp,value_lwp,value_lwp,value_lwp,value_lwp,value_lwp,value_lwp,value_lwp,value_lwp,value_lwp,value_lwp,value_lwp,value_lwp,value_lwp,value_lwp,value_lwp,value_lwp,value_lwp,value_lwp,value_lwp,value_lwp,value_lwp,value_lwp,value_lwp,value_lwp,value_lwp,value_lwp,emp_code));
                c_lwp = cr.fetchall()
                cr.execute('Select Case When "DAY25" = %s Then 1 Else 0 End + \
                                    Case When "DAY26" = %s Then 1 Else 0 End + \
                                    Case When "DAY27" = %s Then 1 Else 0 End + \
                                    Case When "DAY28" = %s Then 1 Else 0 End + \
                                    Case When "DAY29" = %s Then 1 Else 0 End + \
                                    Case When "DAY30" = %s Then 1 Else 0 End + \
                                    Case When "DAY31" = %s Then 1 Else 0 End + \
                                    Case When "DAY1" = %s Then 1 Else 0 End + \
                                    Case When "DAY2" = %s Then 1 Else 0 End + \
                                    Case When "DAY3" = %s Then 1 Else 0 End + \
                                    Case When "DAY4" = %s Then 1 Else 0 End + \
                                    Case When "DAY5" = %s Then 1 Else 0 End + \
                                    Case When "DAY6" = %s Then 1 Else 0 End + \
                                    Case When "DAY7" = %s Then 1 Else 0 End + \
                                    Case When "DAY8" = %s Then 1 Else 0 End + \
                                    Case When "DAY9" = %s Then 1 Else 0 End + \
                                    Case When "DAY10" = %s Then 1 Else 0 End + \
                                    Case When "DAY11" = %s Then 1 Else 0 End + \
                                    Case When "DAY12" = %s Then 1 Else 0 End + \
                                    Case When "DAY13" = %s Then 1 Else 0 End + \
                                    Case When "DAY14" = %s Then 1 Else 0 End + \
                                    Case When "DAY15" = %s Then 1 Else 0 End + \
                                    Case When "DAY16" = %s Then 1 Else 0 End + \
                                    Case When "DAY17" = %s Then 1 Else 0 End + \
                                    Case When "DAY18" = %s Then 1 Else 0 End + \
                                    Case When "DAY19" = %s Then 1 Else 0 End + \
                                    Case When "DAY20" = %s Then 1 Else 0 End + \
                                    Case When "DAY21" = %s Then 1 Else 0 End + \
                                    Case When "DAY22" = %s Then 1 Else 0 End + \
                                    Case When "DAY23" = %s Then 1 Else 0 End + \
                                    Case When "DAY24" = %s Then 1 Else 0 End as count \
                                From muster_roll_register where emp_code=%s',(value_hlwp,value_hlwp,value_hlwp,value_hlwp,value_hlwp,value_hlwp,value_hlwp,value_hlwp,value_hlwp,value_hlwp,value_hlwp,value_hlwp,value_hlwp,value_hlwp,value_hlwp,value_hlwp,value_hlwp,value_hlwp,value_hlwp,value_hlwp,value_hlwp,value_hlwp,value_hlwp,value_hlwp,value_hlwp,value_hlwp,value_hlwp,value_hlwp,value_hlwp,value_hlwp,value_hlwp,emp_code));
                c_hlwp = cr.fetchall()
                list_lwp = [int(i[0]) for i in c_lwp]
                list_hlwp = [int(i[0]) for i in c_hlwp]
                data_lwp=0
                data_hlwp=0.0
                final_data_lwp=0.0
                if len(list_lwp) <> 0:
                    data_lwp = list_lwp[0]
                if len(list_hlwp) <> 0:
                    data_hlwp = list_hlwp[0]
                    ex_data_hlwp=float(data_hlwp)/float(2)
                final_data_lwp=data_lwp+ex_data_hlwp
                cr.execute('update muster_roll_register set "LWP"=%s where emp_code=%s',(final_data_lwp,emp_code));
                if joining_date>=first_date and joining_date<=last_date:
                    cr.execute('update muster_roll_register set "DY_DIFF"=0 where emp_code=%s',(emp_code,));
                cr.execute('select "DY_DIFF" from muster_roll_register where emp_code=%s',(emp_code,));
                c_diff = cr.fetchall()
                list_diff = [int(i[0]) for i in c_diff]
                diff_data=0.0
                if len(list_diff) <> 0:
                    diff_data = list_diff[0]
#                     if month in [1,3,5,7,8,10,12]:
#                         diff_data = 0
                twd1=31
                twd2=31-(-diff_data)-(final_data1+final_data2+final_data3+final_data_lwp+difference)
                tdp=twd2+(final_data1+final_data2+final_data3)    
                    
                cr.execute('update muster_roll_register set "TWD1"=%s,"TWD2"=%s,"TDP"=%s where emp_code=%s',(twd1,twd2,tdp,emp_code));

                cr.execute('update muster_roll_register set "TOFDAY"=%s-%s where emp_code=%s',(cur_month_days,data7,emp_code));
        a=cr.execute('SELECT emp_code,emp_name,"DAY25","DAY26","DAY27","DAY28","DAY29","DAY30","DAY31","DAY1","DAY2","DAY3","DAY4","DAY5","DAY6","DAY7","DAY8","DAY9","DAY10","DAY11","DAY12","DAY13","DAY14","DAY15","DAY16","DAY17","DAY18","DAY19","DAY20","DAY21","DAY22","DAY23","DAY24","LEAVE_CL","LEAVE_PL","LEAVE_SL","LEAVE_CMP","TWD","TOFDAY","DY_DIFF","TWD_2","IS_NIGHT","TOTAL_P","TOLAL_OFF_NHD","PTL_LEAVE","DEPT_CODE" from muster_roll_register');
        res = cr.fetchall()
        fp = StringIO.StringIO()
        writer = csv.writer(fp)
        row1 = ['']
        row2 = ['','','','','IDS','Infotech','Limited.']
        row3 = ['','','','','Department :',attendance.department_id.name]
        row4 = ['','','','','Period :', attendance.month,attendance.year]
        writer.writerow(row1)
        writer.writerow(row2)
        writer.writerow(row3)
        writer.writerow(row4)
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
        file_name = 'muster_roll_register.csv'
        self.write(cr, uid, ids, {'filedata':out, 'filename':file_name}, context=context)
        a=cr.execute('SELECT emp_code,emp_name,"TWD1","DY_DIFF","TWD2","LEAVE_CL","LEAVE_SL","LEAVE_PL","LEAVE_CMP","LWP","TDP","REMARKS" from muster_roll_register');
        res = cr.fetchall()
        fp1 = StringIO.StringIO()
        writer1 = csv.writer(fp1)
        row1 = [' ']
        row2 = [' ',' ',' ',' ','IDS','Infotech','Limited']
        row3 = ['','','','','Department :',attendance.department_id.name]
        row4 = ['','','','','Period :', attendance.month,attendance.year]
        writer1.writerow(row1)
        writer1.writerow(row2)
        writer1.writerow(row3)
        writer1.writerow(row4)
        writer1.writerow([ i[0] for i in cr.description ])
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
            writer1.writerow(row)
        fp1.seek(0)
        data1 = fp1.read()
        fp1.close()
        out1=base64.encodestring(data1)
        file_name1 = 'muster_roll_summery.csv'
        self.write(cr, uid, ids, {'filedata1':out1, 'filename1':file_name1}, context=context)
        return {
                    'name':'Muster Roll Report',
                    'res_model':'attendance.report.wizard',
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
class muster_roll_register(osv.Model):
    _name = 'muster.roll.register'
    
    _columns = {
                'name':fields.many2one('attendance.report.wizard','Name'),
                'emp_code':fields.char('Employee Code'),
                'emp_name':fields.char('Employee Name'),
                'DATE':fields.date('DATE'),
                'DAY25':fields.char('DAY25'),
                'DAY26':fields.char('DAY26'),
                'DAY27':fields.char('DAY27'),
                'DAY28':fields.char('DAY28'),
                'DAY29':fields.char('DAY29'),
                'DAY30':fields.char('DAY30'),
                'DAY31':fields.char('DAY31'),
                'DAY1':fields.char('DAY1'),
                'DAY2':fields.char('DAY2'),
                'DAY3':fields.char('DAY3'),
                'DAY4':fields.char('DAY4'),
                'DAY5':fields.char('DAY5'),
                'DAY6':fields.char('DAY6'),
                'DAY7':fields.char('DAY7'),
                'DAY8':fields.char('DAY8'),
                'DAY9':fields.char('DAY9'),
                'DAY10':fields.char('DAY10'),
                'DAY11':fields.char('DAY11'),
                'DAY12':fields.char('DAY12'),
                'DAY13':fields.char('DAY13'),
                'DAY14':fields.char('DAY14'),
                'DAY15':fields.char('DAY15'),
                'DAY16':fields.char('DAY16'),
                'DAY17':fields.char('DAY17'),
                'DAY18':fields.char('DAY18'),
                'DAY19':fields.char('DAY19'),
                'DAY20':fields.char('DAY20'),
                'DAY21':fields.char('DAY21'),
                'DAY22':fields.char('DAY22'),
                'DAY23':fields.char('DAY23'),
                'DAY24':fields.char('DAY24'),
                'LEAVE_CL':fields.char('LEAVE_CL'),
                'LEAVE_PL':fields.char('LEAVE_PL'),
                'LEAVE_SL':fields.char('LEAVE_SL'),
                'LEAVE_CMP':fields.char('LEAVE_CMP'),
                'TWD':fields.char('TWD'),
                'TOFDAY':fields.char('TOFDAY'),
                'DY_DIFF':fields.char('DY_DIFF'),
                'TWD_2':fields.char('TWD_2'),
                'IS_NIGHT':fields.char('IS_NIGHT'),
                'TOTAL_P':fields.char('TOTAL_P'),
                'TOLAL_OFF_NHD':fields.char('TOLAL_OFF_NHD'),
                'PTL_LEAVE':fields.char('PTL_LEAVE'),
                'DEPT_CODE':fields.char('DEPT_CODE'),
                'LWP':fields.char('LWP'),
                'TWD1':fields.char('TWD'),
                'TWD2':fields.char('TWD'),
                'TDP':fields.char('TDP'),
                'REMARKS':fields.char('REMARKS'),
                }
    


    
