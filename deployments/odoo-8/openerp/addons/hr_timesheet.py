# -*- coding: utf-8 -*-
##############################################################################
#
#    IDS Infotech Ltd
#    Copyright (C) 2004-2010 Tiny SPRL (<http://idsil.com>).
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

import time
from datetime import date
from datetime import datetime, timedelta
from itertools import chain
from openerp.osv import fields
from openerp.osv import osv
from openerp.tools.translate import _

class hr_timesheet_current_open(osv.osv_memory):
    _inherit = 'hr.timesheet.current.open'
    _description = 'hr.timesheet.current.open'

    def open_timesheet(self, cr, uid, ids, context=None):
        ts = self.pool.get('hr_timesheet_sheet.sheet')
        if context is None:
            context = {}
        view_type = 'tree,form'

        user_ids = self.pool.get('hr.employee').search(cr, uid, [('user_id','=',uid)], context=context)
        if not len(user_ids):
            raise osv.except_osv(_('Error!'), _('Please create an employee and associate it with this user.'))
        ids = ts.search(cr, uid, [('user_id','=',uid),('state','in',('draft','new')),('date_from','<=',time.strftime('%Y-%m-%d')), ('date_to','>=',time.strftime('%Y-%m-%d'))], context=context)

        if len(ids) > 1:
            view_type = 'tree,form'
            domain = "[('id','in',["+','.join(map(str, ids))+"]),('user_id', '=', uid)]"
        elif len(ids)==1:
            domain = "[('user_id', '=', uid)]"
        else:
            domain = "[('user_id', '=', uid)]"
        value = {
            'domain': domain,
            'name': _('Open Timesheet'),
            'view_type': 'form',
            'view_mode': view_type,
            'res_model': 'hr_timesheet_sheet.sheet',
            'view_id': False,
            'type': 'ir.actions.act_window'
        }
        if len(ids) == 1:
            value['res_id'] = ids[0]
        return value

class hr_timesheet_sheet(osv.osv):
    _inherit = "hr_timesheet_sheet.sheet"
    _table = 'hr_timesheet_sheet_sheet'
    _order = "id desc"
    _description="Timesheet"
#     def _total(self, cr, uid, ids, name, args, context=None):
#         """ Compute the attendances, analytic lines timesheets and differences between them
#             for all the days of a timesheet and the current day
#         """
#         res = dict.fromkeys(ids, {
#             'total_attendance': 0.0,
#             'total_timesheet': 0.0,
#             'total_difference': 0.0,
#         })
#    
#         cr.execute("""
#             SELECT sheet_id as id,
#                    sum(total_attendance) as total_attendance,
#                    sum(total_timesheet) as total_timesheet,
#                    sum(total_difference) as  total_difference
#             FROM hr_timesheet_sheet_sheet_day
#             WHERE sheet_id IN %s
#             GROUP BY sheet_id
#         """, (tuple(ids),))
#    
#         res.update(dict((x.pop('id'), x) for x in cr.dictfetchall()))
#    
#         return res
    
    def _total(self, cr, uid, ids, name, args, context=None):
        """ Compute the attendances, analytic lines timesheets and differences between them
            for all the days of a timesheet and the current day
        """
        res = dict.fromkeys(ids, {
            'total_attendance': 0.0,
            'total_timesheet': 0.0,
            'total_difference': 0.0,
        })
    
        cr.execute("""
            SELECT sheet_id as id,
                ( select sum(worked_hours) as total_attendance from hr_attendance where sheet_id IN %s) ,
                   sum(total_timesheet) as total_timesheet,
                ( (select sum(worked_hours) from hr_attendance where sheet_id IN %s) - (select sum(total_timesheet) FROM hr_timesheet_sheet_sheet_day
            WHERE sheet_id IN %s)) as total_difference
            FROM hr_timesheet_sheet_sheet_day
            WHERE sheet_id IN %s
            GROUP BY sheet_id
        """, (tuple(ids),tuple(ids),tuple(ids),tuple(ids),))
    
        res.update(dict((x.pop('id'), x) for x in cr.dictfetchall()))
    
        return res
    
    def _cal_extrahours(self, cr, uid, ids, name, args, context=None):
        """ Compute the attendances, analytic lines timesheets and differences between them
            for all the days of a timesheet and the current day
        """
        res = {}
        for obj in self.browse(cr, uid, ids, context=context):
            cr.execute("""SELECT sum(total_timesheet) from hr_timesheet_sheet_sheet_day WHERE sheet_id IN %s GROUP BY sheet_id""", (tuple(ids),));
            result = cr.fetchall()
            if result:
                list = [(i[0]) for i in result]
                data = list[0]
                if data>8.5:
                    res[obj.id]=data-8.5
                else:
                    res[obj.id]=0.0
            else:
                pass
        return res
    
    
    def button_confirm(self, cr, uid, ids, context=None):
        for sheet in self.browse(cr, uid, ids, context=context):
            if sheet.employee_id and sheet.employee_id.parent_id and sheet.employee_id.parent_id.user_id:
                self.message_subscribe_users(cr, uid, [sheet.id], user_ids=[sheet.employee_id.parent_id.user_id.id], context=context)
            self.check_employee_attendance_state(cr, uid, sheet.id, context=context)
            if sheet.cal_ot_hours>0:
                self.write(cr, uid, ids,{'is_extra_hours':True}, context=context )
            di = sheet.user_id.company_id.timesheet_max_difference
            if ((abs(sheet.total_difference) < di) and (sheet.total_difference >= 0.0)) or not di:
                sheet.signal_workflow('confirm')
            else:
                raise osv.except_osv(_('Warning!'), _('Please verify that the total difference of the sheet is lower than %.2f.') %(di,))
        return True
    def create(self, cr, uid, vals, context=None):
        users_obj = self.pool.get('res.users')
        if 'employee_id' in vals:
            if not self.pool.get('hr.employee').browse(cr, uid, vals['employee_id'], context=context).user_id:
                raise osv.except_osv(_('Error!'), _('In order to create a timesheet for this employee, you must link him/her to a user.'))
            if not self.pool.get('hr.employee').browse(cr, uid, vals['employee_id'], context=context).product_id:
                raise osv.except_osv(_('Error!'), _('In order to create a timesheet for this employee, you must link the employee to a product, like \'Consultant\'.'))
            if not self.pool.get('hr.employee').browse(cr, uid, vals['employee_id'], context=context).journal_id:
                raise osv.except_osv(_('Configuration Error!'), _('In order to create a timesheet for this employee, you must assign an analytic journal to the employee, like \'Timesheet Journal\'.'))
        if vals.get('attendances_ids'):
            # If attendances, we sort them by date asc before writing them, to satisfy the alternance constraint
            vals['attendances_ids'] = self.sort_attendances(cr, uid, vals['attendances_ids'], context=context)
        id= super(hr_timesheet_sheet, self).create(cr, uid, vals, context=context)
        ###Added By Satya ################
        timesheet=self.browse(cr, uid, id, context=context)
        days=self.pool.get('hr.employee').browse(cr, uid, timesheet.employee_id.id, context=context).company_id.timesheet_allowed_days
        if not users_obj.has_group(cr, uid, 'base.group_hr_manager'):
            cur_date=time.strftime("%Y-%m-%d")
            dt_temp=datetime.strptime(timesheet.date_from, '%Y-%m-%d').date()
            c_date=datetime.strptime(cur_date, '%Y-%m-%d').date()
            dt_temp1=(date.today().replace(day=dt_temp.day,month=dt_temp.month,year=dt_temp.year))
            cur_date1=(date.today().replace(day=c_date.day,month=c_date.month,year=c_date.year))
            difference=(cur_date1 - dt_temp1).days
            if difference>days:
                raise osv.except_osv(_('Warning!'), _('You cannot mark previous timesheet which is %s days before.') % (days))
        return id
        ########################################
    def write(self, cr, uid, ids, vals, context=None):
        users_obj = self.pool.get('res.users')
        if 'employee_id' in vals:
            new_user_id = self.pool.get('hr.employee').browse(cr, uid, vals['employee_id'], context=context).user_id.id or False
            if not new_user_id:
                raise osv.except_osv(_('Error!'), _('In order to create a timesheet for this employee, you must link him/her to a user.'))
            if not self._sheet_date(cr, uid, ids, forced_user_id=new_user_id, context=context):
                raise osv.except_osv(_('Error!'), _('You cannot have 2 timesheets that overlap!\nYou should use the menu \'My Timesheet\' to avoid this problem.'))
            if not self.pool.get('hr.employee').browse(cr, uid, vals['employee_id'], context=context).product_id:
                raise osv.except_osv(_('Error!'), _('In order to create a timesheet for this employee, you must link the employee to a product.'))
            if not self.pool.get('hr.employee').browse(cr, uid, vals['employee_id'], context=context).journal_id:
                raise osv.except_osv(_('Configuration Error!'), _('In order to create a timesheet for this employee, you must assign an analytic journal to the employee, like \'Timesheet Journal\'.'))
        if vals.get('attendances_ids'):
            # If attendances, we sort them by date asc before writing them, to satisfy the alternance constraint
            # In addition to the date order, deleting attendances are done before inserting attendances
            vals['attendances_ids'] = self.sort_attendances(cr, uid, vals['attendances_ids'], context=context)
        res = super(hr_timesheet_sheet, self).write(cr, uid, ids, vals, context=context)
        if vals.get('attendances_ids'):
            for timesheet in self.browse(cr, uid, ids):
                if not self.pool['hr.attendance']._altern_si_so(cr, uid, [att.id for att in timesheet.attendances_ids]):
                    raise osv.except_osv(_('Warning !'), _('Error ! Sign in (resp. Sign out) must follow Sign out (resp. Sign in)'))
        return res
    
    _columns = {
               'is_extra_hours':fields.boolean('Is Extra Hours'),
               'cal_ot_hours':fields.function(_cal_extrahours, type='float', string='Extra Hours', store=True),
               'actual_ot_hours':fields.float('Actual Extra Hours'),
               'remarks':fields.text('Remarks'),
               'total_attendance': fields.function(_total, method=True, string='Total Attendance', multi="_total",store=True),
               'total_timesheet': fields.function(_total, method=True, string='Total Timesheet', multi="_total",store=True),
               'total_difference': fields.function(_total, method=True, string='Difference', multi="_total",store=True),
#                'timesheet_ids' : fields.one2many('hr.analytic.timesheet', 'sheet_id',
#             'Timesheet lines',
#             readonly=True, states={
#                 'draft': [('readonly', False)],
#                 'confirm': [('readonly', False)],
#                 'new': [('readonly', False)]}
#             ),
               }
    def button_cancel(self, cr, uid, ids, context=None):
        for sheet in self.browse(cr, uid, ids, context=context):
            if sheet.remarks==False:
                raise osv.except_osv(_('Warning!'), _('Please enter remarks!'))
            else:
                sheet.signal_workflow('cancel')
        return True
    def button_done(self, cr, uid, ids, context=None):
        for sheet in self.browse(cr, uid, ids, context=context):
            if sheet.employee_id.user_id.id == uid:
                raise osv.except_osv(_('Warning!'), _('You cannot approve your own Timesheet:\nEmployee: %s') % (sheet.employee_id.name))
            else:
                if sheet.is_extra_hours==False:
                    sheet.signal_workflow('done')
                elif sheet.is_extra_hours==True and sheet.actual_ot_hours>0.0 and sheet.actual_ot_hours<=sheet.cal_ot_hours:
                    sheet.signal_workflow('done')
                elif sheet.actual_ot_hours>sheet.cal_ot_hours:
                    raise osv.except_osv(_('Warning!'), _('Please verify that the actual extra hours of the sheet is lower or equal to extra hours!'))
                else:
                    raise osv.except_osv(_('Warning!'), _('Please enter actual extra hours!'))
        return True
    def unlink(self, cr, uid, ids, context=None):
        sheets = self.read(cr, uid, ids, ['state','total_attendance'], context=context)
        for sheet in sheets:
            if sheet['state'] in ('confirm', 'done'):
                raise osv.except_osv(_('Invalid Action!'), _('You cannot delete a timesheet which is already confirmed.'))
            elif sheet['total_attendance'] <> 0.00:
                pass
                #raise osv.except_osv(_('Invalid Action!'), _('You cannot delete a timesheet which have attendance entries.'))
        toremove = []
        analytic_timesheet = self.pool.get('hr.analytic.timesheet')
        for sheet in self.browse(cr, uid, ids, context=context):
            for timesheet in sheet.timesheet_ids:
                toremove.append(timesheet.id)
        analytic_timesheet.unlink(cr, uid, toremove, context=context)
        cr.execute("delete from hr_timesheet_sheet_sheet where id in %s", (tuple(ids),));
        return True

class hr_analytic_timesheet(osv.osv):
    _name = "hr.analytic.timesheet"
    _table = 'hr_analytic_timesheet'
    _inherit = 'hr.analytic.timesheet'
    _description = "Timesheet Line"   
    
    _columns = {
               'project_category_id':fields.many2one('project.category','Category'),
               'hour_type':fields.selection([('B','Billable'),('N','Non Billable'),('R','Research & Development'),('I','ISG'),('O','Other')],'Hour Type'),
               }
    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        emp_obj = self.pool.get('hr.employee')
        emp_id = emp_obj.search(cr, uid, [('user_id', '=', context.get('user_id') or uid)], context=context)
        ename = ''
        if emp_id:
            ename = emp_obj.browse(cr, uid, emp_id[0], context=context).name
        if vals['unit_amount'] > 8:
            raise osv.except_osv(_('Warning!'), _('Duration must be less or equal to 8 hours in one line!'))
        if not vals.get('journal_id',False):
           raise osv.except_osv(_('Warning!'), _('No \'Analytic Journal\' is defined for employee %s \nDefine an employee for the selected user and assign an \'Analytic Journal\'!')%(ename,))
        if not vals.get('account_id',False):
           raise osv.except_osv(_('Warning!'), _('No analytic account is defined on the project.\nPlease set one or we cannot automatically fill the timesheet.'))
        return super(hr_analytic_timesheet, self).create(cr, uid, vals, context=context)
    
    def write(self, cr, uid, ids, values, context=None):
        if 'unit_amount' in values:
            if values['unit_amount'] > 8:
                raise osv.except_osv(_('Warning!'), _('Duration must be less or equal to 8 hours in one line!'))
        else:
            pass
#         if isinstance(ids, (int, long)):
#             ids = [ids]
#         self._check(cr, uid, ids)
        return super(hr_analytic_timesheet, self).write(cr, uid, ids, values, context=context)
#     def _check(self, cr, uid, ids):
#         for att in self.browse(cr, uid, ids):
#             if att.sheet_id and att.sheet_id.state not in ('draft', 'new','confirm'):
#                 raise osv.except_osv(_('Error!'), _('You cannot modify an entry in a Approved timesheet.'))
#         return True
    
class account_analytic_account(osv.osv):

    _inherit = 'account.analytic.account'
    _description = 'Analytic Account'
    _columns = {
                'members': fields.many2many('res.users', 'analytic_user_rel', 'analytic_id', 'uid', 'Timesheet Members',
                help="Project's members are users who can have an access to the tasks related to this project.", states={'close':[('readonly',True)], 'cancelled':[('readonly',True)]}),
    }
    


class project_project(osv.osv):
    _inherit = "project.project"
    
    _columns = {
               'use_team':fields.boolean('Team'),
               'created':fields.boolean('created')
               }
    
    _defaults = {
        'use_team': True,
        'privacy_visibility': 'followers',
    }
    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        # Prevent double project creation when 'use_tasks' is checked + alias management
        create_context = dict(context, project_creation_in_progress=True,
                              alias_model_name=vals.get('alias_model', 'project.task'),
                              alias_parent_model_name=self._name)

        if vals.get('type', False) not in ('template', 'contract'):
            vals['type'] = 'contract'

        project_id = super(project_project, self).create(cr, uid, vals, context=create_context)
        cr.execute("update project_project set created=True WHERE id=%s"%project_id);
        if vals['use_team']==True:
            a1=cr.execute("SELECT analytic_account_id from project_project WHERE id=%s"%project_id);
            c1 = cr.fetchall()
            list = [int(i[0]) for i in c1]
            data = list[0]
            cr.execute("SELECT uid from project_user_rel WHERE project_id=%s"%project_id);
            res = cr.fetchall()
            for row in chain.from_iterable(res):
                cr.execute("insert into analytic_user_rel(analytic_id,uid) values(%s,%s)"%(data,row));
        project_rec = self.browse(cr, uid, project_id, context=context)
        self.pool.get('mail.alias').write(cr, uid, [project_rec.alias_id.id], {'alias_parent_thread_id': project_id, 'alias_defaults': {'project_id': project_id}}, context)
        return project_id
    
    def write(self, cr, uid, ids, vals, context=None):
        # if alias_model has been changed, update alias_model_id accordingly
        if vals.get('alias_model'):
            model_ids = self.pool.get('ir.model').search(cr, uid, [('model', '=', vals.get('alias_model', 'project.task'))])
            vals.update(alias_model_id=model_ids[0])
        project_id=super(project_project, self).write(cr, uid, ids, vals, context=context)
        if vals.get('members'):
            obj=self.browse(cr,uid,ids,context=None)
            project_id=obj.id
            analytic_id=obj.analytic_account_id.id
            a1=cr.execute("SELECT analytic_account_id from project_project WHERE id=%s"%project_id);
            c1 = cr.fetchall()
            list = [int(i[0]) for i in c1]
            data = list[0]
            cr.execute("SELECT uid from project_user_rel WHERE project_id=%s"%project_id);
            res = cr.fetchall()
            cr.execute("delete from analytic_user_rel where analytic_id=%s"%analytic_id);
            for row in chain.from_iterable(res):
                cr.execute("insert into analytic_user_rel(analytic_id,uid) values(%s,%s)"%(data,row));
        return True
    
class project_category(osv.osv):
    _name = "project.category"
    
    _columns = {
                'name':fields.char('Name')
                } 
    
class res_company(osv.osv):
    _inherit = 'res.company'
    _columns = {
        'timesheet_allowed_days': fields.float('Allowed days for timesheet creation?'),
    }  
    
###### Created By Ravneet

class mail_weekly(osv.osv):
    _name="mail.weekly"
    
    _columns= {
                'name':fields.char('Name'),
                'date_from':fields.date('Date From'),
                'date_to':fields.date('Date To'),
                }
    
    def mail_weekly(self,cr,uid,ids,context=None):
        
        cr.execute("select distinct(parent_id) from hr_employee");
        res=cr.fetchall()
        for values in res:
            if values<>(None,):
                
                cr.execute("select work_email from hr_employee where id=%s"%values);
                res1=cr.fetchall()
                list = [str(i[0]) for i in res1]
                data = list[0]
                values = {
                    'subject': 'Timesheet Approval Reminder',
                    'body_html': 'Please Approve those timesheets which are in To Approve State.\n\n\nKindly do not reply.\n---This is auto generated email---\nRegards:\nERP HR Team\nIDS Infotech LTD.',
                    'email_to': data,
                    'email_from': 'info.openerp@idsil.com',
                      }
                    
        #---------------------------------------------------------------
                mail_obj = self.pool.get('mail.mail') 
                msg_id = mail_obj.create(cr, uid, values, context=context) 
                if msg_id: 
                    mail_obj.send(cr, uid, [msg_id], context=context)       
        return True

class hr_attendance(osv.osv):
    _inherit = "hr.attendance"

    def _get_hr_timesheet_sheet(self, cr, uid, ids, context=None):
        attendance_ids = []
        for ts in self.browse(cr, uid, ids, context=context):
            cr.execute("""
                        SELECT a.id,a.action,a.name
                          FROM hr_attendance a
                         INNER JOIN hr_employee e
                               INNER JOIN resource_resource r
                                       ON (e.resource_id = r.id)
                            ON (a.employee_id = e.id)
                         LEFT JOIN res_users u
                         ON r.user_id = u.id
                         LEFT JOIN res_partner p
                         ON u.partner_id = p.id
                         WHERE %(date_to)s >= date_trunc('day', a.name AT TIME ZONE 'UTC' AT TIME ZONE coalesce(p.tz, 'UTC'))
                              AND %(date_from)s <= date_trunc('day', a.name AT TIME ZONE 'UTC' AT TIME ZONE coalesce(p.tz, 'UTC'))
                              AND %(user_id)s = r.user_id
                         GROUP BY a.id order by action asc""", {'date_from': ts.date_from,
                                            'date_to': ts.date_to,
                                            'user_id': ts.employee_id.user_id.id,
                                            })
            c1 = cr.fetchall()
            list7 = [i[0] for i in c1]
            list2 = [i[1] for i in c1]
            list3 = [i[2] for i in c1]
            data2=0
            data3=0
            data4=0
            if len(list2) <> 0:
                data2 = list2[0]
            if len(list3) > 1:
                data3 = list3[0]
                data4 = list3[1]
            data5=0
            if len(list3)<3:
                if data4>data3 or len(list3)==1:
                    attendance_ids.extend([row[0] for row in c1])
            if len(list3)>2:
                cr.execute("""
                        SELECT a.id,a.action,a.name
                          FROM hr_attendance a
                         INNER JOIN hr_employee e
                               INNER JOIN resource_resource r
                                       ON (e.resource_id = r.id)
                            ON (a.employee_id = e.id)
                         LEFT JOIN res_users u
                         ON r.user_id = u.id
                         LEFT JOIN res_partner p
                         ON u.partner_id = p.id
                         WHERE %(date_to)s >= date_trunc('day', a.name AT TIME ZONE 'UTC' AT TIME ZONE coalesce(p.tz, 'UTC'))
                              AND %(date_from)s <= date_trunc('day', a.name AT TIME ZONE 'UTC' AT TIME ZONE coalesce(p.tz, 'UTC'))
                              AND %(user_id)s = r.user_id
                         GROUP BY a.id order by name desc limit 2""", {'date_from': ts.date_from,
                                            'date_to': ts.date_to,
                                            'user_id': ts.employee_id.user_id.id,
                                            })
                c3 = cr.fetchall()
                attendance_ids.extend([row[0] for row in c3])
            else:
                cr.execute("""
                        SELECT a.id,a.action,a.name
                          FROM hr_attendance a
                         INNER JOIN hr_employee e
                               INNER JOIN resource_resource r
                                       ON (e.resource_id = r.id)
                            ON (a.employee_id = e.id)
                         LEFT JOIN res_users u
                         ON r.user_id = u.id
                         LEFT JOIN res_partner p
                         ON u.partner_id = p.id
                         WHERE %(date_to)s >= date_trunc('day', a.name AT TIME ZONE 'UTC' AT TIME ZONE coalesce(p.tz, 'UTC'))
                              AND %(date_from)s <= date_trunc('day', a.name AT TIME ZONE 'UTC' AT TIME ZONE coalesce(p.tz, 'UTC'))
                              AND %(user_id)s = r.user_id
                         GROUP BY a.id order by action asc limit 1""", {'date_from': ts.date_from,
                                            'date_to': ts.date_to,
                                            'user_id': ts.employee_id.user_id.id,
                                            })
                c2 = cr.fetchall()
                list4 = [int(i[0]) for i in c2]
                data5=0
                if len(list4) <> 0:
                    data5 = len(list4)
                attendance_ids.extend([row[0] for row in c2])
            cr.execute("""
                        SELECT count(a.id)
                          FROM hr_attendance a
                         INNER JOIN hr_employee e
                               INNER JOIN resource_resource r
                                       ON (e.resource_id = r.id)
                            ON (a.employee_id = e.id)
                         LEFT JOIN res_users u
                         ON r.user_id = u.id
                         LEFT JOIN res_partner p
                         ON u.partner_id = p.id
                         WHERE %(date_to)s >= date_trunc('day', a.name AT TIME ZONE 'UTC' AT TIME ZONE coalesce(p.tz, 'UTC'))
                              AND %(date_from)s <= date_trunc('day', a.name AT TIME ZONE 'UTC' AT TIME ZONE coalesce(p.tz, 'UTC'))
                              AND %(user_id)s = r.user_id
                         """, {'date_from': ts.date_from,
                                            'date_to': ts.date_to,
                                            'user_id': ts.employee_id.user_id.id,
                                            })
            c = cr.fetchall()
            list = [int(i[0]) for i in c]
            data=0
            if len(list) <> 0:
                data = list[0]
            df=datetime.strptime(ts.date_from, '%Y-%m-%d')
            dt=datetime.strptime(ts.date_to, '%Y-%m-%d')
            df1=df+timedelta(days=1)
            dt1=dt+timedelta(days=1)
            if data5==1 or len(list3)==1:    
                cr.execute("""
                        SELECT a.id,a.action,a.name
                          FROM hr_attendance a
                         INNER JOIN hr_employee e
                               INNER JOIN resource_resource r
                                       ON (e.resource_id = r.id)
                            ON (a.employee_id = e.id)
                         LEFT JOIN res_users u
                         ON r.user_id = u.id
                         LEFT JOIN res_partner p
                         ON u.partner_id = p.id
                         WHERE %(date_to)s >= date_trunc('day', a.name AT TIME ZONE 'UTC' AT TIME ZONE coalesce(p.tz, 'UTC'))
                              AND %(date_from)s <= date_trunc('day', a.name AT TIME ZONE 'UTC' AT TIME ZONE coalesce(p.tz, 'UTC'))
                              AND %(user_id)s = r.user_id
                         GROUP BY a.id order by name asc,action asc limit 1""", {'date_from': df1,
                                            'date_to': dt1,
                                            'user_id': ts.employee_id.user_id.id,
                                            })
                d=cr.fetchall()
                list1 = [i[1] for i in d]
                list5 = [i[0] for i in d]
		data6=0
                if len(list5)<>0:
                    data6 = list5[0]
                data1=0
                if len(list1) <> 0:
                    data1 = list1[0]
                if data1=='sign_out':
                    cr.execute("update hr_attendance set sheet_id=%s where id=%s"%(ts.id,data6));
                    #attendance_ids.extend([row[0] for row in d])
                    #print"attendance_ids====",attendance_ids
        return attendance_ids
    def _sheet(self, cursor, user, ids, name, args, context=None):
        res = {}.fromkeys(ids, False)
        for attendance in self.browse(cursor, user, ids, context=context):
            res[attendance.id] = self._get_current_sheet(
                    cursor, user, attendance.employee_id.id, attendance.name,
                    context=context)
        return res
    
    _columns = {
        'sheet_id': fields.function(_sheet, string='Sheet',
            type='many2one', relation='hr_timesheet_sheet.sheet',
            store={
                      'hr_timesheet_sheet.sheet': (_get_hr_timesheet_sheet, ['employee_id', 'date_from', 'date_to'], 10),
                      'hr.attendance': (lambda self,cr,uid,ids,context=None: ids, ['employee_id', 'name', 'day'], 10),
                  },
            )
    }
 
   

     
