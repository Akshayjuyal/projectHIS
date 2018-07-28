#-*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2017 IDS Infotech Ltd>.
#    All Rights Reserved.
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
import time
from datetime import date
from datetime import datetime
from datetime import timedelta as td
from dateutil import relativedelta
from openerp.osv import fields, osv
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools.translate import _
from openerp import SUPERUSER_ID
from openerp import api, tools
import StringIO
import base64
import csv

class hr_roster(osv.Model):
    _name = 'hr.roster'
    _description = 'HR Roster'
    
    def _default_user(self, cr, uid, context=None):
        user_id = self.pool.get('res.users').search(cr, uid, [('id','=',uid)], context=context)
        return user_id and user_id[0] or False
    
    _columns = {
                'name':fields.char('Remark'),
                'department_id':fields.many2one('hr.department','Department'),
                'from_date':fields.date('From Date'),
                'to_date':fields.date('To Date'),
                'responsible':fields.many2one('res.users','Responsible'),
                'hr_roster_line':fields.one2many('hr.roster.line','roster_id','Details'),
                'state': fields.selection([
                                           ('draft', 'Draft'),
                                           ('approved', 'Approved'),            
                                           ],
                                          'Status', readonly=True),
                }
    
    _defaults = {
                 
        'responsible': _default_user,
        'state': 'draft',
        'from_date': lambda *a: time.strftime('%Y-%m-25'),
        'to_date': lambda *a: str(datetime.now() + relativedelta.relativedelta(months=+1, day=24))[:10],
    }
    
    def approve(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'approved'}, context=context)
    def unlink(self, cr, uid, ids, context=None):
        for item in self.browse(cr, uid, ids, context=context):
            if item.state not in ('draft'):
                raise osv.except_osv(_('Warning!'),_('You cannot delete a record which is not draft!'))
        return super(hr_roster, self).unlink(cr, uid, ids, context=context)
    
class hr_roster_line(osv.Model):
    _name = 'hr.roster.line'
    _description = 'HR Roster Lines'
    
    _columns = {
                'name':fields.char('Name'),
                'roster_id':fields.many2one('hr.roster','Roster'),
                'employee_id':fields.many2one('hr.employee','Employee'),
                'shift_id':fields.many2one('employee.shift','Shift'),
                'off_day':fields.selection([('0', 'Monday'), ('1', 'Tuesday'), ('2', 'Wednesday'), ('3', 'Thursday'),
                ('4', 'Friday'), ('5', 'Satarday'), ('6', 'Sunday')], 'Off Day'),
                'extra_off_day':fields.selection([('0', 'Monday'), ('1', 'Tuesday'), ('2', 'Wednesday'), ('3', 'Thursday'),
                ('4', 'Friday'), ('5', 'Satarday'), ('6', 'Sunday')], 'Extra Off Day')
                }
    
class hr_leave_swap(osv.Model):
    _name = 'hr.leave.swap'
    _description = 'HR Leave Swap'
    
    _columns = {
                'name':fields.char('Name'),
                'month':fields.selection([('1','January'),('2','February'),('3','March'),
                                          ('4','April'),('5','May'),('6','June'),('7','July'),
                                          ('8','August'),('9','September'),('10','October'),('11','November'),
                                          ('12','December')],'Month' ),
                'year':fields.selection([('2017','2017')],'Year' ),
                'employee_id':fields.many2one('hr.employee','Employee'),
                'swap_on_date':fields.date('Swap On Date'),
                'swap_against_date':fields.date('Swap Against Date'),
                'state': fields.selection([
                                           ('draft', 'Draft'),
                                           ('approved', 'Approved'),            
                                           ],
                                          'Status', readonly=True),
                }
    _defaults = {
                 'state': 'draft',
                 }
    
    def swap(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'approved'}, context=context)
    
    def unlink(self, cr, uid, ids, context=None):
        for item in self.browse(cr, uid, ids, context=context):
            if item.state not in ('draft'):
                raise osv.except_osv(_('Warning!'),_('You cannot delete a record which is not draft!'))
        return super(hr_leave_swap, self).unlink(cr, uid, ids, context=context)
    
    
class hr_roster_report(osv.Model):
    _name = 'hr.roster.report'
    _description = 'HR Roster Report'
    
    _columns = {
                'name':fields.char('Name'),
                'from_date':fields.date('From Date'),
                'to_date':fields.date('To Date'),
                'department_id':fields.many2one('hr.department','Department'),
                'filename': fields.char('Filename', size = 64, readonly=True),
                'filedata': fields.binary('File1', readonly=True),
                'hr_roster_report_ids':fields.one2many('hr.roster.report.line','roster_report_id','Details'),

                }
    
    _defaults = {
        'from_date': lambda *a: time.strftime('%Y-%m-25'),
        'to_date': lambda *a: str(datetime.now() + relativedelta.relativedelta(months=+1, day=24))[:10],
    }
    @api.cr_uid_ids_context
    def print_report(self, cr, uid, ids, context=None):
        #raise osv.except_osv(_('Warning!'), _('Report is under progress please wait for some times!'))
        roster_obj=self.pool.get('hr.roster')
        roster_line_obj=self.pool.get('hr.roster.line')
        if context is None:
            context = {}
        cr.execute("truncate hr_roster_report_line");
        for roster in self.browse(cr,uid,ids,context=context):
            to_date = datetime.strptime(roster.to_date, '%Y-%m-%d').date()
            month = to_date.month
            roster_report_id=roster.id
            roster_ids=roster_obj.search(cr,uid,[('from_date','=',roster.from_date),('to_date','=',roster.to_date),('department_id','=',roster.department_id.id)])
            roster_data=roster_obj.browse(cr,uid,roster_ids,context=None)
            if not roster_data:
                raise osv.except_osv(_('Warning!'), _('There is no roster define for given department !'))
            else:
                roster_id = roster_data.id
                for roster_line in roster_line_obj.search(cr,uid,[('roster_id','=',roster_id)]):
                    for roster_line_data in roster_line_obj.browse(cr,uid,roster_line,context=None):
                        employee_id = roster_line_data.employee_id.name_related
                        emp_code = roster_line_data.employee_id.emp_code
                        shift = roster_line_data.shift_id.name
                        off_day = roster_line_data.off_day
                        emp_id = roster_line_data.employee_id.id
                        value='W'
                        cr.execute("""Insert into hr_roster_report_line (emp_code,emp_name,roster_report_id,shift,off_day,
                        "DAY25","DAY26","DAY27","DAY28","DAY29","DAY30","DAY31","DAY1","DAY2","DAY3","DAY4","DAY5","DAY6","DAY7","DAY8","DAY9","DAY10","DAY11",
                        "DAY12","DAY13","DAY14","DAY15","DAY16","DAY17","DAY18","DAY19","DAY20","DAY21","DAY22","DAY23","DAY24"
                        )Values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
                        ,(emp_code,employee_id,roster_report_id,shift,off_day,value,value,value,value,value,value,value,value,value,value,value,value,value,value,value,value,value,value,value,value,value,value,value,value,value,value,value,value,value,value,value
                          ));
                        d1 = datetime.strptime(roster.from_date, '%Y-%m-%d').date()
                        d2 = datetime.strptime(roster.to_date, '%Y-%m-%d').date()
                        delta = d2 - d1
                        for i in range(delta.days + 1):
                            st_date=(d1 + td(days=i)).day
                            wk_day=(d1 + td(days=i)).weekday()
                            value1='WO'
                            value2='N/A'
                            if st_date==25 and wk_day==0 and off_day=='MON':
                                cr.execute('update hr_roster_report_line set "DAY25"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==25 and wk_day==1 and off_day=='TUE':
                                cr.execute('update hr_roster_report_line set "DAY25"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==25 and wk_day==2 and off_day=='WED':
                                cr.execute('update hr_roster_report_line set "DAY25"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==25 and wk_day==3 and off_day=='THU':
                                cr.execute('update hr_roster_report_line set "DAY25"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==25 and wk_day==4 and off_day=='FRI':
                                cr.execute('update hr_roster_report_line set "DAY25"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==25 and wk_day==5 and off_day=='SAT':
                                cr.execute('update hr_roster_report_line set "DAY25"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==25 and wk_day==6 and off_day=='SUN':
                                cr.execute('update hr_roster_report_line set "DAY25"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==26 and wk_day==0 and off_day=='MON':
                                cr.execute('update hr_roster_report_line set "DAY26"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==26 and wk_day==1 and off_day=='TUE':
                                cr.execute('update hr_roster_report_line set "DAY26"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==26 and wk_day==2 and off_day=='WED':
                                cr.execute('update hr_roster_report_line set "DAY26"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==26 and wk_day==3 and off_day=='THU':
                                cr.execute('update hr_roster_report_line set "DAY26"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==26 and wk_day==4 and off_day=='FRI':
                                cr.execute('update hr_roster_report_line set "DAY26"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==26 and wk_day==5 and off_day=='SAT':
                                cr.execute('update hr_roster_report_line set "DAY26"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==26 and wk_day==6 and off_day=='SUN':
                                cr.execute('update hr_roster_report_line set "DAY26"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==27 and wk_day==0 and off_day=='MON':
                                cr.execute('update hr_roster_report_line set "DAY27"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==27 and wk_day==1 and off_day=='TUE':
                                cr.execute('update hr_roster_report_line set "DAY27"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==27 and wk_day==2 and off_day=='WED':
                                cr.execute('update hr_roster_report_line set "DAY27"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==27 and wk_day==3 and off_day=='THU':
                                cr.execute('update hr_roster_report_line set "DAY27"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==27 and wk_day==4 and off_day=='FRI':
                                cr.execute('update hr_roster_report_line set "DAY27"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==27 and wk_day==5 and off_day=='SAT':
                                cr.execute('update hr_roster_report_line set "DAY27"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==27 and wk_day==6 and off_day=='SUN':
                                cr.execute('update hr_roster_report_line set "DAY27"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==28 and wk_day==0 and off_day=='MON':
                                cr.execute('update hr_roster_report_line set "DAY28"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==28 and wk_day==1 and off_day=='TUE':
                                cr.execute('update hr_roster_report_line set "DAY28"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==28 and wk_day==2 and off_day=='WED':
                                cr.execute('update hr_roster_report_line set "DAY28"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==28 and wk_day==3 and off_day=='THU':
                                cr.execute('update hr_roster_report_line set "DAY28"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==28 and wk_day==4 and off_day=='FRI':
                                cr.execute('update hr_roster_report_line set "DAY28"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==28 and wk_day==5 and off_day=='SAT':
                                cr.execute('update hr_roster_report_line set "DAY28"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==28 and wk_day==6 and off_day=='SUN':
                                cr.execute('update hr_roster_report_line set "DAY28"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==29 and wk_day==0 and off_day=='MON':
                                cr.execute('update hr_roster_report_line set "DAY29"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==29 and wk_day==1 and off_day=='TUE':
                                cr.execute('update hr_roster_report_line set "DAY29"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==29 and wk_day==2 and off_day=='WED':
                                cr.execute('update hr_roster_report_line set "DAY29"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==29 and wk_day==3 and off_day=='THU':
                                cr.execute('update hr_roster_report_line set "DAY29"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==29 and wk_day==4 and off_day=='FRI':
                                cr.execute('update hr_roster_report_line set "DAY29"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==29 and wk_day==5 and off_day=='SAT':
                                cr.execute('update hr_roster_report_line set "DAY29"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==29 and wk_day==6 and off_day=='SUN':
                                cr.execute('update hr_roster_report_line set "DAY29"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==30 and wk_day==0 and off_day=='MON':
                                cr.execute('update hr_roster_report_line set "DAY30"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==30 and wk_day==1 and off_day=='TUE':
                                cr.execute('update hr_roster_report_line set "DAY30"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==30 and wk_day==2 and off_day=='WED':
                                cr.execute('update hr_roster_report_line set "DAY30"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==30 and wk_day==3 and off_day=='THU':
                                cr.execute('update hr_roster_report_line set "DAY30"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==30 and wk_day==4 and off_day=='FRI':
                                cr.execute('update hr_roster_report_line set "DAY30"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==30 and wk_day==5 and off_day=='SAT':
                                cr.execute('update hr_roster_report_line set "DAY30"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==30 and wk_day==6 and off_day=='SUN':
                                cr.execute('update hr_roster_report_line set "DAY30"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==31 and wk_day==0 and off_day=='MON':
                                cr.execute('update hr_roster_report_line set "DAY31"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==31 and wk_day==1 and off_day=='TUE':
                                cr.execute('update hr_roster_report_line set "DAY31"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==31 and wk_day==2 and off_day=='WED':
                                cr.execute('update hr_roster_report_line set "DAY31"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==31 and wk_day==3 and off_day=='THU':
                                cr.execute('update hr_roster_report_line set "DAY31"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==31 and wk_day==4 and off_day=='FRI':
                                cr.execute('update hr_roster_report_line set "DAY31"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==31 and wk_day==5 and off_day=='SAT':
                                cr.execute('update hr_roster_report_line set "DAY31"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==31 and wk_day==6 and off_day=='SUN':
                                cr.execute('update hr_roster_report_line set "DAY31"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==1 and wk_day==0 and off_day=='MON':
                                cr.execute('update hr_roster_report_line set "DAY1"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==1 and wk_day==1 and off_day=='TUE':
                                cr.execute('update hr_roster_report_line set "DAY1"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==1 and wk_day==2 and off_day=='WED':
                                cr.execute('update hr_roster_report_line set "DAY1"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==1 and wk_day==3 and off_day=='THU':
                                cr.execute('update hr_roster_report_line set "DAY1"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==1 and wk_day==4 and off_day=='FRI':
                                cr.execute('update hr_roster_report_line set "DAY1"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==1 and wk_day==5 and off_day=='SAT':
                                cr.execute('update hr_roster_report_line set "DAY1"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==1 and wk_day==6 and off_day=='SUN':
                                cr.execute('update hr_roster_report_line set "DAY1"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==2 and wk_day==0 and off_day=='MON':
                                cr.execute('update hr_roster_report_line set "DAY2"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==2 and wk_day==1 and off_day=='TUE':
                                cr.execute('update hr_roster_report_line set "DAY2"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==2 and wk_day==2 and off_day=='WED':
                                cr.execute('update hr_roster_report_line set "DAY2"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==2 and wk_day==3 and off_day=='THU':
                                cr.execute('update hr_roster_report_line set "DAY2"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==2 and wk_day==4 and off_day=='FRI':
                                cr.execute('update hr_roster_report_line set "DAY2"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==2 and wk_day==5 and off_day=='SAT':
                                cr.execute('update hr_roster_report_line set "DAY2"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==2 and wk_day==6 and off_day=='SUN':
                                cr.execute('update hr_roster_report_line set "DAY2"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==3 and wk_day==0 and off_day=='MON':
                                cr.execute('update hr_roster_report_line set "DAY3"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==3 and wk_day==1 and off_day=='TUE':
                                cr.execute('update hr_roster_report_line set "DAY3"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==3 and wk_day==2 and off_day=='WED':
                                cr.execute('update hr_roster_report_line set "DAY3"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==3 and wk_day==3 and off_day=='THU':
                                cr.execute('update hr_roster_report_line set "DAY3"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==3 and wk_day==4 and off_day=='FRI':
                                cr.execute('update hr_roster_report_line set "DAY3"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==3 and wk_day==5 and off_day=='SAT':
                                cr.execute('update hr_roster_report_line set "DAY3"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==3 and wk_day==6 and off_day=='SUN':
                                cr.execute('update hr_roster_report_line set "DAY3"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==4 and wk_day==0 and off_day=='MON':
                                cr.execute('update hr_roster_report_line set "DAY4"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==4 and wk_day==1 and off_day=='TUE':
                                cr.execute('update hr_roster_report_line set "DAY4"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==4 and wk_day==2 and off_day=='WED':
                                cr.execute('update hr_roster_report_line set "DAY4"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==4 and wk_day==3 and off_day=='THU':
                                cr.execute('update hr_roster_report_line set "DAY4"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==4 and wk_day==4 and off_day=='FRI':
                                cr.execute('update hr_roster_report_line set "DAY4"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==4 and wk_day==5 and off_day=='SAT':
                                cr.execute('update hr_roster_report_line set "DAY4"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==4 and wk_day==6 and off_day=='SUN':
                                cr.execute('update hr_roster_report_line set "DAY4"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==5 and wk_day==0 and off_day=='MON':
                                cr.execute('update hr_roster_report_line set "DAY5"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==5 and wk_day==1 and off_day=='TUE':
                                cr.execute('update hr_roster_report_line set "DAY5"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==5 and wk_day==2 and off_day=='WED':
                                cr.execute('update hr_roster_report_line set "DAY5"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==5 and wk_day==3 and off_day=='THU':
                                cr.execute('update hr_roster_report_line set "DAY5"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==5 and wk_day==4 and off_day=='FRI':
                                cr.execute('update hr_roster_report_line set "DAY5"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==5 and wk_day==5 and off_day=='SAT':
                                cr.execute('update hr_roster_report_line set "DAY5"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==5 and wk_day==6 and off_day=='SUN':
                                cr.execute('update hr_roster_report_line set "DAY5"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==6 and wk_day==0 and off_day=='MON':
                                cr.execute('update hr_roster_report_line set "DAY6"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==6 and wk_day==1 and off_day=='TUE':
                                cr.execute('update hr_roster_report_line set "DAY6"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==6 and wk_day==2 and off_day=='WED':
                                cr.execute('update hr_roster_report_line set "DAY6"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==6 and wk_day==3 and off_day=='THU':
                                cr.execute('update hr_roster_report_line set "DAY6"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==6 and wk_day==4 and off_day=='FRI':
                                cr.execute('update hr_roster_report_line set "DAY6"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==6 and wk_day==5 and off_day=='SAT':
                                cr.execute('update hr_roster_report_line set "DAY6"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==6 and wk_day==6 and off_day=='SUN':
                                cr.execute('update hr_roster_report_line set "DAY6"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==7 and wk_day==0 and off_day=='MON':
                                cr.execute('update hr_roster_report_line set "DAY7"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==7 and wk_day==1 and off_day=='TUE':
                                cr.execute('update hr_roster_report_line set "DAY7"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==7 and wk_day==2 and off_day=='WED':
                                cr.execute('update hr_roster_report_line set "DAY7"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==7 and wk_day==3 and off_day=='THU':
                                cr.execute('update hr_roster_report_line set "DAY7"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==7 and wk_day==4 and off_day=='FRI':
                                cr.execute('update hr_roster_report_line set "DAY7"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==7 and wk_day==5 and off_day=='SAT':
                                cr.execute('update hr_roster_report_line set "DAY7"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==7 and wk_day==6 and off_day=='SUN':
                                cr.execute('update hr_roster_report_line set "DAY7"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==8 and wk_day==0 and off_day=='MON':
                                cr.execute('update hr_roster_report_line set "DAY8"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==8 and wk_day==1 and off_day=='TUE':
                                cr.execute('update hr_roster_report_line set "DAY8"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==8 and wk_day==2 and off_day=='WED':
                                cr.execute('update hr_roster_report_line set "DAY8"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==8 and wk_day==3 and off_day=='THU':
                                cr.execute('update hr_roster_report_line set "DAY8"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==8 and wk_day==4 and off_day=='FRI':
                                cr.execute('update hr_roster_report_line set "DAY8"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==8 and wk_day==5 and off_day=='SAT':
                                cr.execute('update hr_roster_report_line set "DAY8"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==8 and wk_day==6 and off_day=='SUN':
                                cr.execute('update hr_roster_report_line set "DAY8"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==9 and wk_day==0 and off_day=='MON':
                                cr.execute('update hr_roster_report_line set "DAY9"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==9 and wk_day==1 and off_day=='TUE':
                                cr.execute('update hr_roster_report_line set "DAY9"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==9 and wk_day==2 and off_day=='WED':
                                cr.execute('update hr_roster_report_line set "DAY9"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==9 and wk_day==3 and off_day=='THU':
                                cr.execute('update hr_roster_report_line set "DAY9"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==9 and wk_day==4 and off_day=='FRI':
                                cr.execute('update hr_roster_report_line set "DAY9"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==9 and wk_day==5 and off_day=='SAT':
                                cr.execute('update hr_roster_report_line set "DAY9"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==9 and wk_day==6 and off_day=='SUN':
                                cr.execute('update hr_roster_report_line set "DAY9"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==10 and wk_day==0 and off_day=='MON':
                                cr.execute('update hr_roster_report_line set "DAY10"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==10 and wk_day==1 and off_day=='TUE':
                                cr.execute('update hr_roster_report_line set "DAY10"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==10 and wk_day==2 and off_day=='WED':
                                cr.execute('update hr_roster_report_line set "DAY10"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==10 and wk_day==3 and off_day=='THU':
                                cr.execute('update hr_roster_report_line set "DAY10"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==10 and wk_day==4 and off_day=='FRI':
                                cr.execute('update hr_roster_report_line set "DAY10"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==10 and wk_day==5 and off_day=='SAT':
                                cr.execute('update hr_roster_report_line set "DAY10"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==10 and wk_day==6 and off_day=='SUN':
                                cr.execute('update hr_roster_report_line set "DAY10"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==11 and wk_day==0 and off_day=='MON':
                                cr.execute('update hr_roster_report_line set "DAY11"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==11 and wk_day==1 and off_day=='TUE':
                                cr.execute('update hr_roster_report_line set "DAY11"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==11 and wk_day==2 and off_day=='WED':
                                cr.execute('update hr_roster_report_line set "DAY11"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==11 and wk_day==3 and off_day=='THU':
                                cr.execute('update hr_roster_report_line set "DAY11"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==11 and wk_day==4 and off_day=='FRI':
                                cr.execute('update hr_roster_report_line set "DAY11"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==11 and wk_day==5 and off_day=='SAT':
                                cr.execute('update hr_roster_report_line set "DAY11"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==11 and wk_day==6 and off_day=='SUN':
                                cr.execute('update hr_roster_report_line set "DAY11"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==12 and wk_day==0 and off_day=='MON':
                                cr.execute('update hr_roster_report_line set "DAY12"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==12 and wk_day==1 and off_day=='TUE':
                                cr.execute('update hr_roster_report_line set "DAY12"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==12 and wk_day==2 and off_day=='WED':
                                cr.execute('update hr_roster_report_line set "DAY12"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==12 and wk_day==3 and off_day=='THU':
                                cr.execute('update hr_roster_report_line set "DAY12"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==12 and wk_day==4 and off_day=='FRI':
                                cr.execute('update hr_roster_report_line set "DAY12"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==12 and wk_day==5 and off_day=='SAT':
                                cr.execute('update hr_roster_report_line set "DAY12"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==12 and wk_day==6 and off_day=='SUN':
                                cr.execute('update hr_roster_report_line set "DAY12"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==13 and wk_day==0 and off_day=='MON':
                                cr.execute('update hr_roster_report_line set "DAY13"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==13 and wk_day==1 and off_day=='TUE':
                                cr.execute('update hr_roster_report_line set "DAY13"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==13 and wk_day==2 and off_day=='WED':
                                cr.execute('update hr_roster_report_line set "DAY13"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==13 and wk_day==3 and off_day=='THU':
                                cr.execute('update hr_roster_report_line set "DAY13"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==13 and wk_day==4 and off_day=='FRI':
                                cr.execute('update hr_roster_report_line set "DAY13"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==13 and wk_day==5 and off_day=='SAT':
                                cr.execute('update hr_roster_report_line set "DAY13"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==13 and wk_day==6 and off_day=='SUN':
                                cr.execute('update hr_roster_report_line set "DAY13"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==14 and wk_day==0 and off_day=='MON':
                                cr.execute('update hr_roster_report_line set "DAY14"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==14 and wk_day==1 and off_day=='TUE':
                                cr.execute('update hr_roster_report_line set "DAY14"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==14 and wk_day==2 and off_day=='WED':
                                cr.execute('update hr_roster_report_line set "DAY14"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==14 and wk_day==3 and off_day=='THU':
                                cr.execute('update hr_roster_report_line set "DAY14"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==14 and wk_day==4 and off_day=='FRI':
                                cr.execute('update hr_roster_report_line set "DAY14"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==14 and wk_day==5 and off_day=='SAT':
                                cr.execute('update hr_roster_report_line set "DAY14"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==14 and wk_day==6 and off_day=='SUN':
                                cr.execute('update hr_roster_report_line set "DAY14"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==15 and wk_day==0 and off_day=='MON':
                                cr.execute('update hr_roster_report_line set "DAY15"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==15 and wk_day==1 and off_day=='TUE':
                                cr.execute('update hr_roster_report_line set "DAY15"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==15 and wk_day==2 and off_day=='WED':
                                cr.execute('update hr_roster_report_line set "DAY15"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==15 and wk_day==3 and off_day=='THU':
                                cr.execute('update hr_roster_report_line set "DAY15"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==15 and wk_day==4 and off_day=='FRI':
                                cr.execute('update hr_roster_report_line set "DAY15"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==15 and wk_day==5 and off_day=='SAT':
                                cr.execute('update hr_roster_report_line set "DAY15"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==15 and wk_day==6 and off_day=='SUN':
                                cr.execute('update hr_roster_report_line set "DAY15"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==16 and wk_day==0 and off_day=='MON':
                                cr.execute('update hr_roster_report_line set "DAY16"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==16 and wk_day==1 and off_day=='TUE':
                                cr.execute('update hr_roster_report_line set "DAY16"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==16 and wk_day==2 and off_day=='WED':
                                cr.execute('update hr_roster_report_line set "DAY16"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==16 and wk_day==3 and off_day=='THU':
                                cr.execute('update hr_roster_report_line set "DAY16"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==16 and wk_day==4 and off_day=='FRI':
                                cr.execute('update hr_roster_report_line set "DAY16"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==16 and wk_day==5 and off_day=='SAT':
                                cr.execute('update hr_roster_report_line set "DAY16"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==16 and wk_day==6 and off_day=='SUN':
                                cr.execute('update hr_roster_report_line set "DAY16"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==17 and wk_day==0 and off_day=='MON':
                                cr.execute('update hr_roster_report_line set "DAY17"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==17 and wk_day==1 and off_day=='TUE':
                                cr.execute('update hr_roster_report_line set "DAY17"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==17 and wk_day==2 and off_day=='WED':
                                cr.execute('update hr_roster_report_line set "DAY17"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==17 and wk_day==3 and off_day=='THU':
                                cr.execute('update hr_roster_report_line set "DAY17"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==17 and wk_day==4 and off_day=='FRI':
                                cr.execute('update hr_roster_report_line set "DAY17"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==17 and wk_day==5 and off_day=='SAT':
                                cr.execute('update hr_roster_report_line set "DAY17"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==17 and wk_day==6 and off_day=='SUN':
                                cr.execute('update hr_roster_report_line set "DAY17"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==18 and wk_day==0 and off_day=='MON':
                                cr.execute('update hr_roster_report_line set "DAY18"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==18 and wk_day==1 and off_day=='TUE':
                                cr.execute('update hr_roster_report_line set "DAY18"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==18 and wk_day==2 and off_day=='WED':
                                cr.execute('update hr_roster_report_line set "DAY18"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==18 and wk_day==3 and off_day=='THU':
                                cr.execute('update hr_roster_report_line set "DAY18"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==18 and wk_day==4 and off_day=='FRI':
                                cr.execute('update hr_roster_report_line set "DAY18"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==18 and wk_day==5 and off_day=='SAT':
                                cr.execute('update hr_roster_report_line set "DAY18"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==18 and wk_day==6 and off_day=='SUN':
                                cr.execute('update hr_roster_report_line set "DAY18"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==19 and wk_day==0 and off_day=='MON':
                                cr.execute('update hr_roster_report_line set "DAY19"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==19 and wk_day==1 and off_day=='TUE':
                                cr.execute('update hr_roster_report_line set "DAY19"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==19 and wk_day==2 and off_day=='WED':
                                cr.execute('update hr_roster_report_line set "DAY19"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==19 and wk_day==3 and off_day=='THU':
                                cr.execute('update hr_roster_report_line set "DAY19"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==19 and wk_day==4 and off_day=='FRI':
                                cr.execute('update hr_roster_report_line set "DAY19"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==19 and wk_day==5 and off_day=='SAT':
                                cr.execute('update hr_roster_report_line set "DAY19"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==19 and wk_day==6 and off_day=='SUN':
                                cr.execute('update hr_roster_report_line set "DAY19"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==20 and wk_day==0 and off_day=='MON':
                                cr.execute('update hr_roster_report_line set "DAY20"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==20 and wk_day==1 and off_day=='TUE':
                                cr.execute('update hr_roster_report_line set "DAY20"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==20 and wk_day==2 and off_day=='WED':
                                cr.execute('update hr_roster_report_line set "DAY20"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==20 and wk_day==3 and off_day=='THU':
                                cr.execute('update hr_roster_report_line set "DAY20"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==20 and wk_day==4 and off_day=='FRI':
                                cr.execute('update hr_roster_report_line set "DAY20"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==20 and wk_day==5 and off_day=='SAT':
                                cr.execute('update hr_roster_report_line set "DAY20"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==20 and wk_day==6 and off_day=='SUN':
                                cr.execute('update hr_roster_report_line set "DAY20"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==21 and wk_day==0 and off_day=='MON':
                                cr.execute('update hr_roster_report_line set "DAY21"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==21 and wk_day==1 and off_day=='TUE':
                                cr.execute('update hr_roster_report_line set "DAY21"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==21 and wk_day==2 and off_day=='WED':
                                cr.execute('update hr_roster_report_line set "DAY21"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==21 and wk_day==3 and off_day=='THU':
                                cr.execute('update hr_roster_report_line set "DAY21"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==21 and wk_day==4 and off_day=='FRI':
                                cr.execute('update hr_roster_report_line set "DAY21"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==21 and wk_day==5 and off_day=='SAT':
                                cr.execute('update hr_roster_report_line set "DAY21"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==21 and wk_day==6 and off_day=='SUN':
                                cr.execute('update hr_roster_report_line set "DAY21"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==22 and wk_day==0 and off_day=='MON':
                                cr.execute('update hr_roster_report_line set "DAY22"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==22 and wk_day==1 and off_day=='TUE':
                                cr.execute('update hr_roster_report_line set "DAY22"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==22 and wk_day==2 and off_day=='WED':
                                cr.execute('update hr_roster_report_line set "DAY22"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==22 and wk_day==3 and off_day=='THU':
                                cr.execute('update hr_roster_report_line set "DAY22"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==22 and wk_day==4 and off_day=='FRI':
                                cr.execute('update hr_roster_report_line set "DAY22"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==22 and wk_day==5 and off_day=='SAT':
                                cr.execute('update hr_roster_report_line set "DAY22"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==22 and wk_day==6 and off_day=='SUN':
                                cr.execute('update hr_roster_report_line set "DAY22"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==23 and wk_day==0 and off_day=='MON':
                                cr.execute('update hr_roster_report_line set "DAY23"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==23 and wk_day==1 and off_day=='TUE':
                                cr.execute('update hr_roster_report_line set "DAY23"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==23 and wk_day==2 and off_day=='WED':
                                cr.execute('update hr_roster_report_line set "DAY23"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==23 and wk_day==3 and off_day=='THU':
                                cr.execute('update hr_roster_report_line set "DAY23"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==23 and wk_day==4 and off_day=='FRI':
                                cr.execute('update hr_roster_report_line set "DAY23"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==23 and wk_day==5 and off_day=='SAT':
                                cr.execute('update hr_roster_report_line set "DAY23"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==23 and wk_day==6 and off_day=='SUN':
                                cr.execute('update hr_roster_report_line set "DAY23"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==24 and wk_day==0 and off_day=='MON':
                                cr.execute('update hr_roster_report_line set "DAY24"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==24 and wk_day==1 and off_day=='TUE':
                                cr.execute('update hr_roster_report_line set "DAY24"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==24 and wk_day==2 and off_day=='WED':
                                cr.execute('update hr_roster_report_line set "DAY24"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==24 and wk_day==3 and off_day=='THU':
                                cr.execute('update hr_roster_report_line set "DAY24"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==24 and wk_day==4 and off_day=='FRI':
                                cr.execute('update hr_roster_report_line set "DAY24"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==24 and wk_day==5 and off_day=='SAT':
                                cr.execute('update hr_roster_report_line set "DAY24"=%s where emp_code=%s',(value1,emp_code));
                            if st_date==24 and wk_day==6 and off_day=='SUN':
                                cr.execute('update hr_roster_report_line set "DAY24"=%s where emp_code=%s',(value1,emp_code));
                            if month in [5,7,10,12]:
                                cr.execute('update hr_roster_report_line set "DAY31"=%s where emp_code=%s',(value2,emp_code));
                            if month==3:
                                cr.execute('update hr_roster_report_line set "DAY29"=%s where emp_code=%s',(value2,emp_code));
                                cr.execute('update hr_roster_report_line set "DAY30"=%s where emp_code=%s',(value2,emp_code));
                                cr.execute('update hr_roster_report_line set "DAY31"=%s where emp_code=%s',(value2,emp_code));
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
                                            From hr_roster_report_line where emp_code=%s',(value1,value1,value1,value1,value1,value1,value1,value1,value1,value1,value1,value1,value1,value1,value1,value1,value1,value1,value1,value1,value1,value1,value1,value1,value1,value1,value1,value1,value1,value1,value1,emp_code));
                            c1 = cr.fetchall()
                            list1 = [int(i[0]) for i in c1]
                            data1=0
                            if len(list1) <> 0:
                                data1 = list1[0]
                            cr.execute('update hr_roster_report_line set "off"=%s where emp_code=%s',(data1,emp_code));
                        for leave_swap in self.pool.get('hr.leave.swap').search(cr,uid,[('employee_id','=',emp_id),('swap_on_date','>=',d1),('swap_on_date','<=',d2)], order='swap_on_date'):
                            for leave_swap_data in self.pool.get('hr.leave.swap').browse(cr,uid,leave_swap,context=context):
                                print"leave_swap_data====",leave_swap_data
                                value='WO-SW'
                                day=datetime.strptime(leave_swap_data.swap_on_date,'%Y-%m-%d').day
 
        a=cr.execute('SELECT shift,emp_code,emp_name,off_day,"DAY25","DAY26","DAY27","DAY28","DAY29","DAY30","DAY31","DAY1","DAY2","DAY3","DAY4","DAY5","DAY6","DAY7","DAY8","DAY9","DAY10","DAY11","DAY12","DAY13","DAY14","DAY15","DAY16","DAY17","DAY18","DAY19","DAY20","DAY21","DAY22","DAY23","DAY24",off from hr_roster_report_line');
        res = cr.fetchall()
        fp = StringIO.StringIO()
        writer = csv.writer(fp)
        row2 = [' ',' ',' ',' ','IDS','Infotech','Limited']
        row3 = [' ',' ',' ',' ','Duty','Roster',':', roster.from_date ,':',roster.to_date]
        writer.writerow(row2)
        writer.writerow(row3)
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
        file_name = 'roster_report.csv'
        self.write(cr, uid, ids, {'filedata':out, 'filename':file_name}, context=context)
        return {
                    'name':'Duty Roster Report',
                    'res_model':'hr.roster.report',
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
    
class hr_roster_report_line(osv.Model):
    _name = 'hr.roster.report.line'
    _description = 'HR Roster Report Line'
    
    _columns = {
                'name':fields.char('Name'),
                'roster_report_id':fields.many2one('hr.roster.report','Roster Report'),
                'emp_code':fields.char('Employee Code'),
                'emp_name':fields.char('Employee Name'),
                'shift':fields.char('Shift'),
                'off_day':fields.char('Off Day'),
                'extra_off_day':fields.char('Extra Off Day'),
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
                'off':fields.char('Off'),
                }
    
    
class download_template(osv.Model):
    _name = 'download.template'
    _description = 'Download Template(Shift Roster)'
    
    _columns = {
                'name':fields.char('Name', required=True),
                'file':fields.binary('File', filters='*.csv'),
                'filename': fields.char('FileName')
    
                }
    
    