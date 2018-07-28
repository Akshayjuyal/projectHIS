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
    def update_total(self,cr,uid,context=None):
        """ update total attendance,total timesheet and differences
        """
        res={}
        list=[]
        data= 0.0,
        data1= 0.0,
        data2= 0.0,
        for record in self.pool.get('hr_timesheet_sheet.sheet').search(cr, uid, [('total_attendance','<=',0.00)]):
            for data_record in self.pool.get('hr_timesheet_sheet.sheet').browse(cr, uid, record, context=None):
                list=[]
                sheet_id=data_record.id
                emp_code=data_record.employee_id.emp_code
                list.append(sheet_id)
                cr.execute("""
                    SELECT sheet_id as id,
                        ( select sum(worked_hours) as total_attendance from hr_attendance where sheet_id IN %s) ,
                           sum(total_timesheet) as total_timesheet,
                        ( (select sum(worked_hours) from hr_attendance where sheet_id IN %s) - (select sum(total_timesheet) FROM hr_timesheet_sheet_sheet_day
                    WHERE sheet_id IN %s)) as total_difference
                    FROM hr_timesheet_sheet_sheet_day
                    WHERE sheet_id IN %s
                    GROUP BY sheet_id
                """, (tuple(list),tuple(list),tuple(list),tuple(list),))
                c = cr.fetchall()
                d_list = [i[1] for i in c]
                d_list1 = [i[2] for i in c]
                d_list2 = [i[3] for i in c]
                data = d_list[0]
                data1 = d_list1[0]
                data2 = d_list2[0]
                cr.execute("update hr_timesheet_sheet_sheet set total_attendance=%s,total_timesheet=%s,total_difference=%s WHERE id=%s",(data,data1,data2,sheet_id));
        return res
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
                if data>9.0:
                    res[obj.id]=data-9.0
                else:
                    res[obj.id]=0.0
            else:
                pass
        return res
    
    
    def button_confirm(self, cr, uid, ids, context=None):
        """Constraints on Submit button. """
        for sheet in self.browse(cr, uid, ids, context=context):
            if sheet.employee_id and sheet.employee_id.parent_id and sheet.employee_id.parent_id.user_id:
                self.message_subscribe_users(cr, uid, [sheet.id], user_ids=[sheet.employee_id.parent_id.user_id.id], context=context)
            self.check_employee_attendance_state(cr, uid, sheet.id, context=context)
            if sheet.cal_ot_hours>0:
                self.write(cr, uid, ids,{'is_extra_hours':True}, context=context )
            di = sheet.user_id.company_id.timesheet_max_difference
            if sheet.total_timesheet == 0.0:
                raise osv.except_osv(_('Warning!'), _('You can not submit blank timesheet!'))
            if sheet.total_attendance == 0.0:
                raise osv.except_osv(_('Warning!'), _('Total attendance must be greater than zero!'))
            if ((abs(sheet.total_difference) < di) and (sheet.total_difference >= 0.0)) or not di:
                sheet.signal_workflow('confirm')
                cr.execute("update hr_analytic_timesheet set state='confirm' where sheet_id=%s"%(sheet.id));
            else:
                raise osv.except_osv(_('Warning!'), _('Please verify that the total difference of the sheet is lower than %.2f.') %(di,))
        return True
    def create(self, cr, uid, vals, context=None):
        """Constraints while creating timesheets. """
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
            dt_temp_to=datetime.strptime(timesheet.date_to, '%Y-%m-%d').date()
            c_date=datetime.strptime(cur_date, '%Y-%m-%d').date()
            dt_temp1=(date.today().replace(day=dt_temp.day,month=dt_temp.month,year=dt_temp.year))
            cur_date1=(date.today().replace(day=c_date.day,month=c_date.month,year=c_date.year))
            difference=(cur_date1 - dt_temp1).days
            if difference>days:
                raise osv.except_osv(_('Warning!'), _('You cannot mark previous timesheet which is %s days before.') % (days))
            if dt_temp<>dt_temp_to:
                raise osv.except_osv(_('Warning!'), _('Timesheet period must be equal!'))
        return id
        ########################################
    def write(self, cr, uid, ids, vals, context=None):
        """Constraints while editting timesheets. """
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
               'division_id':fields.many2one('division', 'Division')
#                'timesheet_ids' : fields.one2many('hr.analytic.timesheet', 'sheet_id',
#             'Timesheet lines',
#             readonly=True, states={
#                 'draft': [('readonly', False)],
#                 'confirm': [('readonly', False)],
#                 'new': [('readonly', False)]}
#             ),
               }
    def button_cancel(self, cr, uid, ids, context=None):
        """In case, timesheet is refused and set to draft. """
        for sheet in self.browse(cr, uid, ids, context=context):
            if sheet.remarks==False:
                raise osv.except_osv(_('Warning!'), _('Please enter remarks!'))
            else:
                sheet.signal_workflow('cancel')
                cr.execute("update hr_analytic_timesheet set state='draft' where sheet_id=%s"%(sheet.id));
        return True
    
    def button_done(self, cr, uid, ids, context=None):
        """Constraints while approving timesheets. """
        for sheet in self.browse(cr, uid, ids, context=context):
            if sheet.employee_id.user_id.id == uid:
                raise osv.except_osv(_('Warning!'), _('You cannot approve your own Timesheet:\nEmployee: %s') % (sheet.employee_id.name))
            else:
                if sheet.is_extra_hours==False:
                    sheet.signal_workflow('done')
                    cr.execute("update hr_analytic_timesheet set state='done' where sheet_id=%s"%(sheet.id));
                elif sheet.is_extra_hours==True and sheet.actual_ot_hours>0.0 and round(sheet.actual_ot_hours, 2)<=sheet.cal_ot_hours:
                    sheet.signal_workflow('done')
                    cr.execute("update hr_analytic_timesheet set state='done' where sheet_id=%s"%(sheet.id));
                elif round(sheet.actual_ot_hours, 2)>sheet.cal_ot_hours:
                    raise osv.except_osv(_('Warning!'), _('Please verify that the actual extra hours of the sheet is lower or equal to extra hours!'))
                else:
                    raise osv.except_osv(_('Warning!'), _('Please enter actual extra hours!'))
        return True
    
    def button_done_multi(self, cr, uid, ids, context=None):
        for sheet in self.browse(cr, uid, ids, context=context):
            if sheet.employee_id.user_id.id == uid:
                raise osv.except_osv(_('Warning!'), _('You cannot approve your own Timesheet:\nEmployee: %s') % (sheet.employee_id.name))
            else:
                if sheet.is_extra_hours==False:
                    sheet.signal_workflow('done')
                    cr.execute("update hr_analytic_timesheet set state='done' where sheet_id=%s"%(sheet.id));
                else:
                    pass
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
    
    def onchange_employee_id(self, cr, uid, ids, employee_id, context=None):
        """On change function on employee_id. """
        department_id =  False
        user_id = False
        if employee_id:
            empl_id = self.pool.get('hr.employee').browse(cr, uid, employee_id, context=context)
            department_id = empl_id.department_id.id
            user_id = empl_id.user_id.id
            division_id = empl_id.division
        return {'value': {'department_id': department_id, 'user_id': user_id, 'division_id': division_id }}

class hr_analytic_timesheet(osv.osv):
    _name = "hr.analytic.timesheet"
    _table = 'hr_analytic_timesheet'
    _inherit = 'hr.analytic.timesheet'
    _description = "Timesheet Line"
    
    def on_change_account_id(self, cr, uid, ids, account_id,project_category_id, user_id=False):
        """Get project task on change account_id. """
        res = super(hr_analytic_timesheet, self).on_change_account_id(
            cr, uid, ids, account_id,)
        if project_category_id:
            return {'value':{'project_category_id':False}}
        if not account_id:
            return res
        cr.execute("select hour_type_id from analytic_category_rel where analytic_id=%s"%account_id);
        res1=cr.fetchall()
        list = [i[0] for i in res1]
        return {'domain':{'project_category_id':[('id','in',list)]}}
    
#     def get_project_category(self,cr,uid,account_id,context=None):
#         res=[1,2,3]
#         return res   
#     

    _columns = {
               'project_category_id':fields.many2one('project.category','Tasks'),
#                'hour_type':fields.selection([('B','Billable'),('N','Non Billable'),('R','Research & Development'),('I','ISG'),('O','Other')],'Hour Type'),
               'hour_type_id':fields.many2one('hour.type', 'Hour Type'),
               'utl_rpt_id':fields.many2one('timesheet.analysis.line','Utilization Report'),
				'state' : fields.selection([
                    ('new', 'New'),
                    ('draft','Open'),
                    ('confirm','Waiting Approval'),
                    ('done','Approved')], 'Status', readonly= True),			   
				'division_id':fields.many2one('division', 'Division')               
				}
    def create(self, cr, uid, vals, context=None):
        """Constraints while creating timesheets. """
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
    
    def onchange_project_category(self, cr, uid, ids, project_category_id,account_id=False,context=None):
        """Update hour type on change of project category. """
        if project_category_id and account_id==False:
            raise osv.except_osv(_('Warning!'), _('No Project Defined.\nYou must first select a project!.'))
        else:
            project= self.pool.get('project.category').browse(cr,uid,project_category_id, context=None)
            hour_type=project.hour_type_id
            return {'value':{'hour_type_id':hour_type}}
    def write(self, cr, uid, ids, values, context=None):
        """Constraints while creating timesheets. """
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

    def _getDivision(self, cr, uid, context=None):
        if context is None:
            context = {}
        emp_obj = self.pool.get('hr.employee')
        emp_id = emp_obj.search(cr, uid, [('user_id', '=', context.get('user_id') or uid)], context=context)
        if emp_id:
            emp = emp_obj.browse(cr, uid, emp_id[0], context=context)
            if emp.division:
                return emp.division
        return False
    
    _defaults = {
        'division_id': _getDivision
    }

    def on_change_user_id(self, cr, uid, ids, user_id):
            if not user_id:
                return {}
            context = {'user_id': user_id}
            return {'value': {
                'product_id': self. _getEmployeeProduct(cr, uid, context),
                'product_uom_id': self._getEmployeeUnit(cr, uid, context),
                'general_account_id': self._getGeneralAccount(cr, uid, context),
                'journal_id': self._getAnalyticJournal(cr, uid, context),
                'division_id': self._getDivision(cr, uid, context),
            }}
 
    
class hour_type(osv.osv):
    _name = "hour.type"
    
    _columns = {
               'name':fields.char('Name'),
               'code':fields.char('Code')
               }
    


class account_analytic_account(osv.osv):

    _inherit = 'account.analytic.account'
    _description = 'Analytic Account'
    _columns = {
                'members': fields.many2many('res.users', 'analytic_user_rel', 'analytic_id', 'uid', 'Timesheet Members',
                help="Project's members are users who can have an access to the tasks related to this project.", states={'close':[('readonly',True)], 'cancelled':[('readonly',True)]}),
               #created by Ravneet
                'tasks': fields.many2many('project.category','analytic_category_rel','analytic_id','hour_type_id','Tasks')
                
    }
    


class project_project(osv.osv):
    _inherit = "project.project"
    
    def _get_task_id(self, cr, uid, context=None):
         result = []
         if context is None:
             context = {}
         task_obj = self.pool.get('project.category')
         res = task_obj.search(cr, uid, [('use_default', '=', True )])
         for eachid in res:
            result.append(eachid)
         return result or result[0] or False

    _columns = {
               'use_team':fields.boolean('Team'),
               'created':fields.boolean('created'),
               'tasks': fields.many2many('project.category','project_category_rel','project_id','hour_type_id','Tasks'),
               'company_id':fields.many2one('res.company','Company'),
               'description':fields.text('Description',size=100),
               'group_id':fields.many2one('employee.group','Group'),
               }
    
    _defaults = {
        'tasks': _get_task_id, 
        'use_team': True,
        'privacy_visibility': 'followers',
        'name':'/',
        'company_id':lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'project.project',context=c),
    }
    def copy(self, cr, uid, id, default=None, context=None):
        """Forbid duplicacy. """
        raise osv.except_osv(_('Forbbiden to duplicate'), _('Is not possible to duplicate the record, please create a new one.'))
    
    def onchange_user_id(self, cr, uid, ids, group_id,user_id, context=None):
        user=self.pool.get('res.users').browse(cr, uid, user_id, context=context)
        group_id=user.group_id.id
        res= {'value': {'group_id': group_id}}
        return res
    def create(self, cr, uid, vals, context=None):
        """creating sequence of project for IDEAS and also while creating new project, 
              new analytic account get created automatically."""
        if vals['company_id']==3:
            vals['name']=self.pool.get('ir.sequence').get(cr, uid,'project.project')
        
        if context is None:
            context = {}
        # Prevent double project creation when 'use_tasks' is checked + alias management
        create_context = dict(context, project_creation_in_progress=True,
                              alias_model_name=vals.get('alias_model', 'project.task'),
                              alias_parent_model_name=self._name)

        if vals.get('type', False) not in ('template', 'contract'):
            vals['type'] = 'contract'
        next=''
        data_id=users=0
        if vals['company_id']==3:
            if vals['partner_id']:
                partner_id=vals['partner_id']
                data_id=self.search(cr, uid, [('partner_id','=',partner_id)], order='create_date DESC', limit=1)
                data=self.browse(cr, uid, data_id, context=context)
                project_name=data.name
                if data_id:
                    month=project_name[-7:-5]
                    project_month=int(month)
                    now=datetime.now()
                    current_month=now.month
                    last=project_name[-3:]
                    next=int(last)+1
                    if len(str(next))==1:
                        next=str("00")+str(next)
                    if len(str(next))==2:
                        next=str("0")+str(next)
        project_id = super(project_project, self).create(cr, uid, vals, context=create_context)
        if vals['company_id']==3:
            if vals['partner_id']:
                partner_id=vals['partner_id']
                cr.execute('select ref from res_partner where id=%s '%partner_id)
                c1 = cr.fetchall()
                list = [str(i[0]) for i in c1]
                data = list[0]
                project_name=vals['name']
                if data_id and project_month==current_month:
                    new_project= project_name[:11]+data+next
                else:
                    new_project= project_name[:11]+data+str("001")
                self.write(cr, uid, project_id, {'name':new_project})
        if vals['members']:
            ids= vals['members']
            users= ids[0][2]
            for user_id in users:
                cr.execute("select work_email, name_related from hr_employee where resource_id=(select id from resource_resource where user_id=%s limit 1)"%user_id);
                values_get=cr.fetchall()
                list_get = [str(x[0]) for x in values_get]
                list_get1 = [str(x[1]) for x in values_get]
                final_email = list_get[0]
                final_name = list_get1[0]
                url="http://ids-erp.idsil.loc:8069/web"
                if vals['date']:
                    values = {
                    'subject': 'Project Assigned -'+ vals['name'] ,
                    'body_html': 'Hi '+final_name+'.<br/><br/>Start Execution of the'+vals['name']+'as per requirement.Kindly adhere mentioned deadline.<br/>Please feel free to ask me if you have any question.<br/><br/>Start date: '+ vals['date_start']+'<br/>End Date: '+vals['date']+'<br/><br/>Thank You<br/><br/>Regards:<br/>ERP HR Team<br/>IDS Infotech LTD.<br/>Url:'+url,
                    'email_to': final_email,
                    'email_from': 'info.openerp@idsil.com',
                      }
                else:
                    values = {
                    'subject': 'Project Assigned -'+ vals['name'] ,
                    'body_html': 'Hi '+final_name+'.<br/><br/>Start Execution of the'+vals['name']+'as per requirement.Kindly adhere mentioned deadline.<br/>Please feel free to ask me if you have any question.<br/><br/>Start date: '+ vals['date_start']+'<br/>End Date: <br/><br/>Thank You<br/><br/>Regards:<br/>ERP HR Team<br/>IDS Infotech LTD.<br/>Url:'+url,
                    'email_to': final_email,
                    'email_from': 'info.openerp@idsil.com',
                      }
                            
    #---------------------------------------------------------------
                mail_obj = self.pool.get('mail.mail') 
                msg_id = mail_obj.create(cr, uid, values, context=context) 
                if msg_id: 
                    mail_obj.send(cr, uid, [msg_id], context=context)    
                
        
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
        a2=cr.execute("SELECT analytic_account_id from project_project WHERE id=%s"%project_id);
        c2 = cr.fetchall()
        list1 = [int(i[0]) for i in c2]
        data1 = list1[0]
        cr.execute("SELECT hour_type_id from project_category_rel WHERE project_id=%s"%project_id);
        res1 = cr.fetchall()
        for row1 in chain.from_iterable(res1):
            cr.execute("insert into analytic_category_rel(analytic_id,hour_type_id) values(%s,%s)"%(data1,row1));
        project_rec = self.browse(cr, uid, project_id, context=context)
        self.pool.get('mail.alias').write(cr, uid, [project_rec.alias_id.id], {'alias_parent_thread_id': project_id, 'alias_defaults': {'project_id': project_id}}, context)
        
        return project_id
    
    def write(self, cr, uid, ids, vals, context=None):
        """updating analytic account while changing in any project. """
        # if alias_model has been changed, update alias_model_id accordingly
        obj=self.browse(cr,uid,ids,context=None)
        list_b=[]
        if vals.get('members'):
            cr.execute("SELECT uid from project_user_rel WHERE project_id=%s"%obj.id);
            res = cr.fetchall()
            for row in chain.from_iterable(res):
                print "row---------", row   
                list_b.append(row)

        if vals.get('alias_model'):
            model_ids = self.pool.get('ir.model').search(cr, uid, [('model', '=', vals.get('alias_model', 'project.task'))])
            vals.update(alias_model_id=model_ids[0])            
            
        project_id=super(project_project, self).write(cr, uid, ids, vals, context=context)
        list_a=[]
        if vals.get('members'):
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
                list_a.append(row)
            
            

            temp3 = [item for item in list_a if item not in list_b]
            for user_id in temp3:
                cr.execute("select work_email, name_related from hr_employee where resource_id=(select id from resource_resource where user_id=%s limit 1)"%user_id);
                values_get=cr.fetchall()
                list_get = [str(x[0]) for x in values_get]
                list_get1 = [str(x[1]) for x in values_get]
                final_email = list_get[0]
                final_name = list_get1[0]
                url="http://ids-erp.idsil.loc:8069/web"
                if obj.date:
                    values = {
                    'subject': 'Project Assigned -'+ obj.name ,
                    'body_html': 'Hi '+final_name+'.<br/><br/>Start Execution of the'+obj.name+'as per requirement.Kindly adhere mentioned deadline.<br/>Please feel free to ask me if you have any question.<br/><br/>Start date: '+ obj.date_start+'<br/>End Date: '+obj.date+'<br/><br/>Thank You<br/><br/>Regards:<br/>ERP HR Team<br/>IDS Infotech LTD.<br/>Url:'+url,
                    'email_to': final_email,
                    'email_from': 'info.openerp@idsil.com',
                      }
                else:
                    values = {
                    'subject': 'Project Assigned -'+ obj.name ,
                    'body_html': 'Hi '+final_name+'.<br/><br/>Start Execution of the'+obj.name+'as per requirement.Kindly adhere mentioned deadline.<br/>Please feel free to ask me if you have any question.<br/><br/>Start date: '+ obj.date_start+'<br/>End Date: <br/><br/>Thank You<br/><br/>Regards:<br/>ERP HR Team<br/>IDS Infotech LTD.<br/>Url:'+url,
                    'email_to': final_email,
                    'email_from': 'info.openerp@idsil.com',
                      }
                             
                mail_obj = self.pool.get('mail.mail') 
                msg_id = mail_obj.create(cr, uid, values, context=context) 
                if msg_id: 
                    mail_obj.send(cr, uid, [msg_id], context=context)    
                
        if vals.get('tasks'):
            obj=self.browse(cr,uid,ids,context=None)
            project_id=obj.id
            analytic_id=obj.analytic_account_id.id
            a2=cr.execute("SELECT analytic_account_id from project_project WHERE id=%s"%project_id);
            c2 = cr.fetchall()
            list1 = [int(i[0]) for i in c2]
            data1 = list1[0]
            cr.execute("SELECT hour_type_id from project_category_rel WHERE project_id=%s"%project_id);
            res1 = cr.fetchall()
            cr.execute("delete from analytic_category_rel where analytic_id=%s"%analytic_id);
            for row1 in chain.from_iterable(res1):
                cr.execute("insert into analytic_category_rel(analytic_id,hour_type_id) values(%s,%s)"%(data1,row1));
        return True
    
    def change(self, cr, uid, ids, context=None):
        """Action button to change name of the project. """
        return {
                    'name':'Change Name',
                    'res_model':'ids.project',
                    'type':'ir.actions.act_window',
                    'view_type':'form',
                    'view_mode':'form',
                    'target':'new',
                    'context': context
                    } 
    
class ids_project(osv.osv):
    _name = 'ids.project'
    
    _columns= {
                'name':fields.char('Name'),
                'change_name':fields.char('Project Name',required=True)
                
               } 
    
    def default_get(self, cr, uid, fields, context=None):
        """
        This function gets default values
        """
        res = super(ids_project, self).default_get(cr, uid, fields, context=context)
        if context is None:
            context = {}
        record_id = context and context.get('active_id', False) or False
        if not record_id:
            return res
        project = self.pool.get('project.project')
        project_name = project.browse(cr, uid, record_id, context=context)

        if 'change_name' in fields:
            res['change_name'] = project_name.name if project_name.name else False

        return res
    
    def change_project_name(self, cr, uid, ids, context=None):
        """For changing project name. """
        record_id = context and context.get('active_id', False) or False
        change= self.browse(cr, uid, ids, context=None)
        change_name=change.change_name
        project=self.pool.get('project.project')
        for record in project.search(cr, uid, [('id','=',record_id)]):
            for data_record in project.browse(cr, uid, record, context=None):
                name=data_record.name
                
                if change_name :
                    project.write(cr, uid, record,{'name':change_name}, context=context )
        return True
        


class project_category(osv.osv):
    _name = "project.category"
    
    _columns = {
                'name':fields.char('Task Name'),
                'hour_type_id':fields.many2one('hour.type', 'Hour Type'),
                'use_default':fields.boolean('Use Default(In Project)'),
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
    
    def mail_weekly(self,cr,uid,context=None):
        """Email template for timesheet approving remainder to manager. """
        url="http://ids-erp.idsil.loc:8069/web"
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
                    'body_html': 'Please Approve those timesheets which are in To Approve State.<br/><br/><br/>Kindly do not reply.<br/>---This is auto generated email---<br/>Regards:<br/>ERP HR Team<br/>IDS Infotech LTD.<br/>Url:'+url,
                    'email_to': data,
                    'email_from': 'info.openerp@idsil.com',
                      }
        
        
            
        #---------------------------------------------------------------
                mail_obj = self.pool.get('mail.mail') 
                msg_id = mail_obj.create(cr, uid, values, context=context) 
                if msg_id: 
                    mail_obj.send(cr, uid, [msg_id], context=context)       
        return True
    def mail_weekly_all(self,cr,uid,context=None):
        """Email template for sending email to employees on weekly basis. """
        url="http://ids-erp.idsil.loc:8069/web"
        cr.execute("select id from hr_employee where working_status='working'");
        res=cr.fetchall()
        for values in res:
            if values<>(None,):
                
                cr.execute("select work_email from hr_employee where id=%s"%values);
                res1=cr.fetchall()
                list = [str(i[0]) for i in res1]
                data = list[0]
                values = {
                    'subject': 'Fill your Weekly Timesheet in ERP System (Odoo)',
                    'body_html': 'Hello Everyone.<br/><br/>Please fill your weekly timesheet before 11:30 AM of today.<br/><br/><br/>Kindly do not reply.<br/>---This is auto generated email---<br/>Regards:<br/>ERP HR Team<br/>IDS Infotech LTD.<br/>Url:'+url,
                    'email_to': data,
                    'email_from': 'info.openerp@idsil.com',
                      }
                    
        #------------------------------------data---------------------------
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
 
 
class account_analytic_line(osv.osv):
   _inherit = 'account.analytic.line'
   _columns = {
       'general_account_id': fields.many2one('account.account', 'General Account', ondelete='restrict'),
   }
 
   
class employee_group(osv.osv):
    
    _name = 'employee.group'
    _description = "Employee Group"
    _columns= {
               'name':fields.char('Group Name'),
               'division_group':fields.many2one('division','Division')
               } 
          


class res_partner(osv.Model):
    _inherit = 'res.partner'
    _columns = {
                'group_id':fields.many2one('employee.group','Group'),
                'group_ids_new':fields.many2many('employee.group', 'partner_group_rel', 'partner_id','employee_group','Group'),

                }    
    
    
class project_work(osv.osv):
    _inherit = "project.task.work"
    _columns = {
        'categ_id': fields.many2one('project.category','Category'),
    }
    
    