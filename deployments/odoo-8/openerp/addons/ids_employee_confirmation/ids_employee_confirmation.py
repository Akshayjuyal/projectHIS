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
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from openerp import netsvc
from openerp.tools.translate import _ 
import re
from openerp import SUPERUSER_ID

class ids_employee_confirmation(osv.osv): 
      
    def confirmation_hr_start(self, cr, uid, ids, context=None):
        """Initiate the workflow. """
        self._check_confirmation(cr, uid, ids, context=context)
        self.confirmation_start_notificate(cr, uid, ids, context=context)
        obj_emp = self.pool.get('hr.employee')
        ids2 = obj_emp.search(cr, uid, [('user_id', '=', uid)])
        employee_id = ids2 and ids2[0] or False
        return self.write(cr, uid, ids, {'state': 'start', 'manager_id1': employee_id})   	 
     
    def confirmation_employee_submit(self, cr, uid, ids, context=None):  
        """Submit the form to Manager """      
        self.confirmation_submit_notificate(cr, uid, ids, context=context)
        
        emp_confirm=self.browse(cr, uid, ids, context=None)
        url="http://ids-erp.idsil.loc:8069/web"
        values = {
        'subject': 'Employee Confirmation' + ' ' + emp_confirm.employee_id.name,
        'body_html': 'The Employee Confirmation Process of'+' '+emp_confirm.employee_id.name+ ' ' + 'has started.Please take necessary action.<br/><br/><br/>Kindly do not reply.<br/>---This is auto generated email---<br/>Regards:<br/>ERP HR Team<br/>IDS Infotech LTD.<br/><br/>Url:'+url,
        'email_to': emp_confirm.employee_id.parent_id.work_email,
        'email_cc': emp_confirm.employee_id.work_email, 
        'email_from': 'info.openerp@idsil.com',
          }
        #---------------------------------------------------------------
        mail_obj = self.pool.get('mail.mail') 
        msg_id = mail_obj.create(cr, uid, values, context=context) 
        if msg_id: 
            mail_obj.send(cr, uid, [msg_id], context=context)
        
        
        
        
        return self.write(cr, uid, ids, {'state': 'submit'})   	 

    def confirmation_manager_recommend(self, cr, uid, ids, context=None):
        """ Manager recommends the confirmation."""
        self._check_validate(cr, uid, ids, context=context)       
        self.confirmation_recommend_notificate(cr, uid, ids, context=context)
        obj_emp = self.pool.get('hr.employee')
        ids2 = obj_emp.search(cr, uid, [('user_id', '=', uid)])
        manager = ids2 and ids2[0] or False     
        
        emp_confirm=self.browse(cr, uid, ids, context=None)
        url="http://ids-erp.idsil.loc:8069/web"
        values = {
        'subject': 'Employee Confirmation' + ' ' + emp_confirm.employee_id.name,
        'body_html': 'The Employee Confirmation Feedback Form of'+' '+emp_confirm.employee_id.name+ ' ' + 'has submitted and recommended for confirmation.<br/><br/><br/>Kindly do not reply.<br/>---This is auto generated email---<br/>Regards:<br/>ERP HR Team<br/>IDS Infotech LTD.<br/><br/>Url:'+url,
        'email_to': emp_confirm.employee_id.parent_id.parent_id.work_email,
        'email_cc': emp_confirm.employee_id.division.hr_email, 
        'email_from': 'info.openerp@idsil.com',
          }
        #---------------------------------------------------------------
        mail_obj = self.pool.get('mail.mail') 
        msg_id = mail_obj.create(cr, uid, values, context=context) 
        if msg_id: 
            mail_obj.send(cr, uid, [msg_id], context=context)
        
        
           
        return self.write(cr, uid, ids, {'state':'recommend', 'manager_id2': manager})      
    
    def confirmation_bh_approve(self, cr, uid, ids, context=None):
        """Approval process by HOD. """
        self._check_validate(cr, uid, ids, context=context)        
        obj_emp = self.pool.get('hr.employee')
        ids2 = obj_emp.search(cr, uid, [('user_id', '=', uid)])
        manager = ids2 and ids2[0] or False
        self.confirmation_approve_notificate(cr, uid, ids, context=context) 
        
        emp_confirm=self.browse(cr, uid, ids, context=None)
        url="http://ids-erp.idsil.loc:8069/web"
        values = {
        'subject': 'Employee Confirmation' + ' ' + emp_confirm.employee_id.name,
        'body_html': 'The Confirmation of'+' '+emp_confirm.employee_id.name+ ' ' + 'has Approved.<br/><br/><br/>Kindly do not reply.<br/>---This is auto generated email---<br/>Regards:<br/>ERP HR Team<br/>IDS Infotech LTD.<br/>Url:'+url,
        'email_to': emp_confirm.employee_id.parent_id.work_email,
        'email_cc': emp_confirm.employee_id.division.hr_email, 
        'email_from': 'info.openerp@idsil.com',
          }
        #---------------------------------------------------------------
        mail_obj = self.pool.get('mail.mail') 
        msg_id = mail_obj.create(cr, uid, values, context=context) 
        if msg_id: 
            mail_obj.send(cr, uid, [msg_id], context=context)
        
        
           	
        return self.write(cr, uid, ids, {'state':'approve', 'manager_id3': manager})
    
    def confirmation_hr_employee_confirm(self, cr, uid, ids, context=None):
        """Final Confirmation """
        self.confirmation_confirm_emp_notificate(cr, uid, ids, context=context)
        self._update_employee_working_status(cr, uid, ids, 'confirmed', context=None) 
        
        emp_confirm=self.browse(cr, uid, ids, context=None)
        url="http://ids-erp.idsil.loc:8069/web"
        values = {
        'subject': 'Employee Confirmation' + ' ' + emp_confirm.employee_id.name,
        'body_html': 'The Employee'+' '+emp_confirm.employee_id.name+ ' ' + 'has been Confirmed.<br/><br/><br/>Kindly do not reply.<br/>---This is auto generated email---<br/>Regards:<br/>ERP HR Team<br/>IDS Infotech LTD.<br/><br/>Url:'+url,
        'email_to': emp_confirm.employee_id.parent_id.work_email,
        'email_from': 'info.openerp@idsil.com',
        'email_cc': {emp_confirm.employee_id.parent_id.parent_id.work_email, emp_confirm.employee_id.work_email}
          }
        #---------------------------------------------------------------
        mail_obj = self.pool.get('mail.mail') 
        msg_id = mail_obj.create(cr, uid, values, context=context) 
        if msg_id: 
            mail_obj.send(cr, uid, [msg_id], context=context)
        
        
        return self.write(cr, uid, ids, {'state':'confirm'})
            
    def confirmation_reject(self, cr, uid, ids, context=None):	
        """In case, confirmation rejected by Manager. """
    	self.confirmation_reject_notificate(cr, uid, ids, context=context)
        obj_emp = self.pool.get('hr.employee')
        ids2 = obj_emp.search(cr, uid, [('user_id', '=', uid)])
        reject_mgr_id = ids2 and ids2[0] or False
        
        state_info = self.read(cr, uid, ids, ['state'])
              
        if state_info:
            state_name = state_info[0]['state']
            if state_name == 'recommend':
                self._check_validate(cr, uid, ids, context=context)      
      	        #code to update employee working status
    	        self._update_employee_working_status(cr, uid, ids, 'extended', context=None)
                
        emp_confirm=self.browse(cr, uid, ids, context=None)
        url="http://ids-erp.idsil.loc:8069/web"
        values = {
        'subject': 'Employee Confirmation' + ' ' + emp_confirm.employee_id.name,
        'body_html': 'The Employee'+' '+emp_confirm.employee_id.name+ ' ' + 'has been Rejected.<br/><br/><br/>Kindly do not reply.<br/>---This is auto generated email---<br/>Regards:<br/>ERP HR Team<br/>IDS Infotech LTD.<br/><br/>Url:'+url,
        'email_to': emp_confirm.employee_id.parent_id.parent_id.work_email,
        'email_cc': emp_confirm.employee_id.division.hr_email, 
        'email_from': 'info.openerp@idsil.com',
          }
        #---------------------------------------------------------------
        mail_obj = self.pool.get('mail.mail') 
        msg_id = mail_obj.create(cr, uid, values, context=context) 
        if msg_id: 
            mail_obj.send(cr, uid, [msg_id], context=context)
        
        return self.write(cr, uid, ids, {'state': 'reject', 'manager_id3': reject_mgr_id})
    
    def _update_employee_working_status(self, cr, uid, ids, confirmation_status, context=None):
        """Updating working status after employee is confirmed. """
        obj_confirmation = self.browse(cr, uid, ids)
        sep_emp_id = 0	    
        
        for record in obj_confirmation:
            sep_emp_id = record.employee_id.id	    
            obj_emp = self.pool.get('hr.employee')
          
        if confirmation_status == 'confirmed':
            self.pool.get('hr.holidays.status').allocate_holidays_on_confirmation(cr, uid, sep_emp_id, context=None)   
        
        return obj_emp.write(cr, SUPERUSER_ID , [sep_emp_id], {'confirmation_status':confirmation_status})	
        
	
    def onchange_employee_id(self, cr, uid, ids, employee_id, context=None):
        """Get the associated values with employee on changing the employee id from
              hr.employee """
        emp_code = ''
        department_id = ''
        job_id = ''
        department_name = ''
        parent_name= ''
        job_name = ''
        joining_date = ''
        confirmation_date = ''
        confirmation_status = ''
        
        obj_emp = self.pool.get('hr.employee')        
            
        if employee_id:
            record = obj_emp.browse(cr,uid,employee_id,context=context)            
            
            if record:    
                emp_code = record.emp_code
                department_id = record.department_id.id
                if department_id:
                    dept_info = self.pool.get('hr.department').read(cr, uid, [department_id], ['name'])
                    if dept_info:
                        department_name =  dept_info[0]['name']
                job_id = record.job_id.id
                if job_id:
                    job_info = self.pool.get('hr.job').read(cr, uid, [job_id], ['name'])
                    if job_info:
                        job_name =  job_info[0]['name']
                reporting_manager = record.parent_id.id
                if reporting_manager:
                    parent_info = self.pool.get('hr.employee').read(cr, uid, [reporting_manager], ['name'])
                    if parent_info:
                        parent_name =  parent_info[0]['name']
                        
                joining_date = record.joining_date
                confirmation_date = record.confirmation_date
                confirmation_status = record.confirmation_status
        
        res = {'value': {'emp_code': emp_code, 'department_id': department_name, 'reporting_manager':parent_name, 'job_id': job_name, 'joining_date': joining_date, 'confirmation_date': confirmation_date, 'confirmation_status': confirmation_status}}                 
        
        return res
    
    def _check_validate(self, cr, uid, ids, context=None):
        """Validating constraint on Employee confirming himself/herself. """
        users_obj = self.pool.get('res.users')
        
        if not users_obj.has_group(cr, uid, 'base.group_hr_manager'):
            for confirmation in self.browse(cr, uid, ids, context=context):
                if confirmation.employee_id.user_id.id == uid:
                    raise osv.except_osv(_('Warning!'), _('You cannot %s yourself.') % (confirmation.state))
        return
    
    def _get_employee_info(self, cr, uid, ids, name, args, context=None):
        """Getting the required employee information automatically. """      
        result = {}
        emp_code = ''
        department_id = ''
        reporting_manager= ''
        job_id = ''
        joining_date = ''
        confirmation_date = ''
        confirmation_status = ''
        
        if not ids:
            return []
        
        for self_obj_new in self.browse(cr, uid, ids, context=context):
             
            emp_info = self.pool.get('hr.employee').read(cr, SUPERUSER_ID, [self_obj_new.employee_id.id], ['emp_code','department_id','parent_id','job_id','joining_date','confirmation_date','confirmation_status'])                
                        
            if emp_info:                
                emp_code = emp_info[0]['emp_code']
                department_id = emp_info[0]['department_id'][1]
                reporting_manager = emp_info[0]['parent_id'][1]
                job_id = emp_info[0]['job_id'][1]
                joining_date = emp_info[0]['joining_date']
                confirmation_date = emp_info[0]['confirmation_date']
                confirmation_status = emp_info[0]['confirmation_status']
                #result = dict.fromkeys(ids[self_obj_new.id], {'emp_code': emp_code, 'department_id': department_id, 'job_id': job_id, 'joining_date': joining_date, 'confirmation_date': confirmation_date, 'confirmation_status': confirmation_status})
                result[self_obj_new.id] = {'emp_code': emp_code, 'department_id': department_id, 'reporting_manager':reporting_manager,'job_id': job_id, 'joining_date': joining_date, 'confirmation_date': confirmation_date, 'confirmation_status': confirmation_status}
               
        return result 
    
    _name = 'ids.employee.confirmation'        
    _inherit = ['mail.thread', 'ir.needaction_mixin'] 
    _description = "Employee Confirmation"
    _columns = {                
                'employee_id': fields.many2one('hr.employee', 'Employee', required=True, domain="[('working_status', '!=', 'exit')]"),
                'emp_code': fields.function(_get_employee_info, type='char', string='Employee Code', multi='emp_info'),
                'department_id': fields.function(_get_employee_info, type='char', string='Department', multi='emp_info'),
                'job_id': fields.function(_get_employee_info, type='char', string='Designation', multi='emp_info'),
                'joining_date': fields.function(_get_employee_info, type='date', string='Joining Date', multi='emp_info'),
                'confirmation_date': fields.function(_get_employee_info, type='date', string='Confirmation Date', multi='emp_info'),
                'reporting_manager':fields.function(_get_employee_info, type='char', string='Reporting Manager', multi='emp_info'),
                'data_file':fields.binary('Upload Assesment Form'),
                'confirmation_status': fields.function(_get_employee_info, type='char', string='Confirmation Status', multi='emp_info'),                
                'manager_id1': fields.many2one('hr.employee', 'First Approval', invisible=False, readonly=True, help='This area is automatically filled by the HR Manager'),
                'manager_id2': fields.many2one('hr.employee', 'Second Approval', invisible=False, readonly=True, help='This area is automatically filled by the Manager'),
                'manager_id3': fields.many2one('hr.employee', 'Third Approval', invisible=False, readonly=True, help='This area is automatically filled by the Business Head'),
                'reject_mgr_id': fields.many2one('hr.employee', 'Reject', invisible=False, readonly=True, help='This area is automatically filled by the employee id who rejected the confirmation'),
		        'state': fields.selection([('open', 'To start'), ('start', 'Confirmation Process Started'), ('submit', 'Employee Submitted Forms'), ('recommend', 'Manager Feedback Done'), ('approve', 'Approved'), ('confirm','Employee Confirmed'), ('reject', 'Rejected')], 'Status', readonly=True),
               }
    _rec_name = 'emp_code'
    _defaults = {
        'state': 'open', 
        #'capture_date':fields.date.context_today
    }
        
    def unlink(self, cr, uid, ids, context=None):        
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.state in ['approve', 'reject']:
                raise osv.except_osv(_('Warning!'),_('You cannot delete a confirmation entry which is in %s state.')%(rec.state))
        return super(ids_employee_confirmation, self).unlink(cr, uid, ids, context)    
    
        
    def _check_confirmation(self, cr, uid, ids, context=None):        
        """Validating constraints"""
        res_emp_id = 0
        
        for obj in self.browse(cr, uid, ids, context=context):
            res_emp_id = obj.employee_id.id            
        
        confirmation_emp_ids = self.pool.get('hr.employee').search(cr, uid, [('id', '=', res_emp_id),('confirmation_status', '=', 'confirmed')], context=context)        
        if confirmation_emp_ids:
            raise osv.except_osv(_('Warning!'), _('Employee is already confirmed.'))
        
        confirmation_ids = self.search(cr, uid, [('id','not in',ids),('employee_id', '=', res_emp_id),('state', '!=', 'reject')], context=context)
        if confirmation_ids:
            raise osv.except_osv(_('Warning!'), _('Confirmation is already in progress/done for this employee'))
        
        return True
    
    def refuse(self, cr, uid, ids, context=None):
        """In case, confirmation is refused by HOD. """
        emp_confirm=self.browse(cr, uid, ids, context=None)
        values = {
        'subject': 'Employee Confirmation' + ' ' + emp_confirm.employee_id.name,
        'body_html': 'The Employee'+' '+emp_confirm.employee_id.name+ ' ' + 'has been Rejected.<br/><br/><br/>Kindly do not reply.<br/>---This is auto generated email---<br/>Regards:<br/>ERP HR Team<br/>IDS Infotech LTD.',
        'email_to': emp_confirm.employee_id.parent_id.work_email,
        'email_cc': emp_confirm.employee_id.division.hr_email, 
        'email_from': 'info.openerp@idsil.com',
          }
        #---------------------------------------------------------------
        mail_obj = self.pool.get('mail.mail') 
        msg_id = mail_obj.create(cr, uid, values, context=context) 
        if msg_id: 
            mail_obj.send(cr, uid, [msg_id], context=context)
        
        return self.write(cr, uid, ids, {'state': 'reject'}, context=context)
    
        
        
    
    # -----------------------------
    # OpenChatter and notifications
    # -----------------------------
    
    def confirmation_start_notificate(self, cr, uid, ids, context=None):
	for obj in self.browse(cr, uid, ids, context=context):
            self.message_post(cr, uid, [obj.id],
                _("Confirmation process started, waiting for candidate's action."), context=context)
    
    def confirmation_submit_notificate(self, cr, uid, ids, context=None):
	for obj in self.browse(cr, uid, ids, context=context):
            self.message_post(cr, uid, [obj.id],
                _("Employee submitted confirmation form, waiting for manager's feedback."), context=context)

    def confirmation_recommend_notificate(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context=context):
            self.message_post(cr, uid, [obj.id],
                _("Manager provided feedback, waiting for approval from Business/Delivery Head"), context=context)
            
    def confirmation_approve_notificate(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context=context):
            self.message_post(cr, uid, [obj.id],
                _("Confirmation Approved."), context=context)
    
    def confirmation_confirm_emp_notificate(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context=context):
            self.message_post(cr, uid, [obj.id],
                _("Employee Confirmed."), context=context)
    
    def confirmation_reject_notificate(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context=context):
            self.message_post(cr, uid, [obj.id],
                _("Confirmation Rejected."), context=context)    
        
