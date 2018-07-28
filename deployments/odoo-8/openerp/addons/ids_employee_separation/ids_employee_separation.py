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

def _check_unique_insesitive(self, cr, uid, ids, context=None):
    """Checking for uniqueness of the value """
    list_ids = self.search(cr, uid , [], context=context)
    lst = [list_id.name.lower() for list_id in self.browse(cr, uid, list_ids, context=context) if list_id.name and list_id.id not in ids]
    for self_obj in self.browse(cr, uid, ids, context=context):
        if self_obj.name and self_obj.name.lower() in lst:
            return False
        return True

class ids_hr_employee_exit_form(osv.osv):
    
    _name = 'ids.hr.employee.exit.form'
    _description = "Employee Exit Form"    
    
    _columns = {
              'last_salary_date': fields.date('Last Salary Date', required=True)                                         
    }      

class ids_hr_employee_separation(osv.osv): 
    
    def separation_submit(self, cr, uid, ids, context=None):
        """Initiate workflow- submit the form. """
        self._check_resignations(cr, uid, ids, context=context)
        users= self.pool.get('res.users')
    	#code to update employee working status
    	self._update_employee_working_status(cr, uid, ids, 'on_resign', context=None)

        resign=self.browse(cr, uid, ids, context=None)
        if users.has_group(cr, uid, 'ids_emp.group_location_hr'):
            print "------------------------------location--outer------------------------"
            if resign.employee_id.parent_id.parent_id.id==7626:
                print "------------------------------res--------------------------"
                url="http://ids-erp.idsil.loc:8069/web"
                values = {
                'subject': 'Resignation' + '-' + resign.employee_id.name,
                'body_html': 'Resignation of' +' '+resign.employee_id.name+' '+'is Intiated.Please take necessary action.<br/><br/><br/>Kindly do not reply.<br/>---This is auto generated email---<br/>Regards:<br/>ERP HR Team<br/>IDS Infotech LTD.<br/>Url:'+url,
                'email_to': resign.employee_id.parent_id.work_email,
                'email_from': 'info.openerp@idsil.com',
                  }  
            else:
                print "------------------------------location--------------------------"
                url="http://ids-erp.idsil.loc:8069/web"
                values = {
                'subject': 'Resignation' + '-' + resign.employee_id.name,
                'body_html': 'Resignation of' +' '+resign.employee_id.name+' '+'is Intiated.Please take necessary action.<br/><br/><br/>Kindly do not reply.<br/>---This is auto generated email---<br/>Regards:<br/>ERP HR Team<br/>IDS Infotech LTD.<br/>Url:'+url,
                'email_to': resign.employee_id.division.hod_email,
                'email_cc': resign.employee_id.parent_id.work_email,
                'email_from': 'info.openerp@idsil.com',
                  }

        #---------------------------------------------------------------
            mail_obj = self.pool.get('mail.mail') 
            msg_id = mail_obj.create(cr, uid, values, context=context) 
            if msg_id: 
                mail_obj.send(cr, uid, [msg_id], context=context)
        
        elif users.has_group(cr, uid, 'ids_emp.group_business_head'):
            print "------------------------------business--------------------------"
            url="http://ids-erp.idsil.loc:8069/web"
            values = {
            'subject': 'Resignation' + '-' + resign.employee_id.name,
            'body_html': 'Resignation of' +' '+resign.employee_id.name+' '+'is Intiated.Please take necessary action.<br/><br/><br/>Kindly do not reply.<br/>---This is auto generated email---<br/>Regards:<br/>ERP HR Team<br/>IDS Infotech LTD.<br/>Url:'+url,
            'email_to': resign.employee_id.division.hr_email,
            'email_from': 'info.openerp@idsil.com',
              }
        #---------------------------------------------------------------
            mail_obj = self.pool.get('mail.mail') 
            msg_id = mail_obj.create(cr, uid, values, context=context) 
            if msg_id: 
                mail_obj.send(cr, uid, [msg_id], context=context)
        else:
            print "------------------------------manager--------------------------"
            url="http://ids-erp.idsil.loc:8069/web"
            values = {
            'subject': 'Resignation' + '-' + resign.employee_id.name,
            'body_html': 'Resignation of' +' '+resign.employee_id.name+' '+'is Intiated.Please take necessary action.<br/><br/><br/>Kindly do not reply.<br/>---This is auto generated email---<br/>Regards:<br/>ERP HR Team<br/>IDS Infotech LTD.<br/>Url:'+url,
            'email_to': resign.employee_id.division.hod_email,
            'email_cc': resign.employee_id.division.hr_email,
            'email_from': 'info.openerp@idsil.com',
              }
        #---------------------------------------------------------------
            mail_obj = self.pool.get('mail.mail') 
            msg_id = mail_obj.create(cr, uid, values, context=context) 
            if msg_id: 
                mail_obj.send(cr, uid, [msg_id], context=context)
        	
    	return self.write(cr, uid, ids, {'state': 'confirm'})   	 
      
    def separation_first_validate(self, cr, uid, ids, context=None):	
        """Validating the form by Manager and update the working status. """
        self._check_validate(cr, uid, ids, context=context)
    	#code to update employee working status
    	self._update_employee_working_status(cr, uid, ids, 'resigned', context=None)	
        
        resign=self.browse(cr, uid, ids, context=None)
        url="http://ids-erp.idsil.loc:8069/web"
        values = {
        'subject': 'Resignation' + '-' + resign.employee_id.name,
        'body_html': 'Resignation of' +' '+resign.employee_id.name+' '+'is Approved.<br/><br/><br/>Kindly do not reply.<br/>---This is auto generated email---<br/>Regards:<br/>ERP HR Team<br/>IDS Infotech LTD.<br/><br/>Url:'+url,
        'email_to': resign.employee_id.parent_id.work_email,
        'email_cc': resign.employee_id.division.hr_email,
        'email_from': 'info.openerp@idsil.com',
          }
        #---------------------------------------------------------------
        mail_obj = self.pool.get('mail.mail') 
        msg_id = mail_obj.create(cr, uid, values, context=context) 
        if msg_id: 
            mail_obj.send(cr, uid, [msg_id], context=context)
        

        return self.write(cr, uid, ids, {'state':'approve'})      
    
    def separation_second_validate(self, cr, uid, ids, context=None):   
        """Final validation by HOD. """ 
        now=datetime.now()
        current = now.strftime('%Y-%m-%d')   
        self._check_validate(cr, uid, ids, context=context)

    	#code to update employee working status
    	self._update_employee_working_status(cr, uid, ids, 'resigned', context=None)
        
        resign=self.browse(cr, uid, ids, context=None)
        if resign.last_date>current:
            raise osv.except_osv(_('Warning!'), _('You can not validate before last date in company!'))
        if resign.employee_id.parent_id.parent_id.id==7626:
            print "------------------------------res--------------------------"
            url="http://ids-erp.idsil.loc:8069/web"
            values = {
            'subject': 'Resignation' + '-' + resign.employee_id.name,
            'body_html': 'Resignation of' +' '+resign.employee_id.name+' '+'is Intiated.Please take necessary action.<br/><br/><br/>Kindly do not reply.<br/>---This is auto generated email---<br/>Regards:<br/>ERP HR Team<br/>IDS Infotech LTD.<br/>Url:'+url,
            'email_to': resign.employee_id.parent_id.work_email,
            'email_from': 'info.openerp@idsil.com',
              }  
        else:
            url="http://ids-erp.idsil.loc:8069/web"
            values = {
            'subject': 'Resignation' + '-' + resign.employee_id.name,
            'body_html': 'Resignation of' +' '+resign.employee_id.name+' '+'is Validated.<br/><br/><br/>Kindly do not reply.<br/>---This is auto generated email---<br/>Regards:<br/>ERP HR Team<br/>IDS Infotech LTD.\<br/><br/>Url:'+url,
            'email_to': resign.employee_id.parent_id.work_email,
            'email_cc': resign.employee_id.division.hod_email,
            'email_from': 'info.openerp@idsil.com',
              }
        #---------------------------------------------------------------
        mail_obj = self.pool.get('mail.mail') 
        msg_id = mail_obj.create(cr, uid, values, context=context) 
        if msg_id: 
            mail_obj.send(cr, uid, [msg_id], context=context)
            
        ee = self.pool.get('hr.employee').browse(cr, uid, resign.employee_id, context=context)
        emp_busi_id = self.pool.get('ids.business.information').search(cr, uid , [('employee_id','=',resign.employee_id.id)], context=context) 
        eb = self.pool.get('ids.business.information').browse(cr, uid, emp_busi_id[0], context=context)
        emp_tech_id = self.pool.get('ids.technical.information').search(cr, uid , [('employee_id','=',resign.employee_id.id)], context=context)
        et = self.pool.get('ids.technical.information').browse(cr, uid, emp_tech_id[0], context=context)
        res = {
               'employee_id':resign.employee_id.id,
               'job_id':resign.employee_id.job_id.id,
               'department_id':resign.employee_id.department_id.id,
               'dob':resign.employee_id.birthday,
               'division_id':resign.employee_id.division.id,
               'location_id':resign.employee_id.office_location.id,
               'gender':resign.employee_id.gender,
               'mobile_no':resign.employee_id.mobile_phone,
               'joining_date':resign.employee_id.joining_date,
               'confirmation_status':resign.employee_id.confirmation_status.title(),
               'resign_id':resign.id,
               'capture_date':resign.capture_date,
               'last_date':resign.last_date,
               'email_control':eb.email_control,
               'internet_control':eb.internet_control,
               'remote_control':eb.remote_control,
               'software_requirement':eb.software_requirements,
               'application_share':eb.application_share_access,
               'data_backup':eb.backup_remarks,
               'allocation_it_asset':et.allocation_of_itassets or False,
               'email_id_tech':et.email_created or False,
               'internet_control_tech':et.internet_access_control or False,
               'backup_setup_tech':et.backup_setup or False,
               'software_requirement_tech': et.software_provisioning_and_access_control or False,
               'application_share_tech':et.application_share_access or False,
               'state':'phase1',
               
               } 
        self.pool.get('emp.no.dues').create(cr, uid, res)
        return self.write(cr, uid, ids, {'state':'done'})
    
    def separation_refuse(self, cr, uid, ids, context=None):
        """In case, resignation of employee is refused. """
        
        #code to update employee working status
        self._update_employee_working_status(cr, uid, ids, 'working', context=None)
        
        resign=self.browse(cr, uid, ids, context=None)
        url="http://ids-erp.idsil.loc:8069/web"
        values = {
        'subject': 'Resignation' + '-' + resign.employee_id.name,
        'body_html': 'Resignation of' +' '+resign.employee_id.name+' '+'is Refused.<br/><br/><br/>Kindly do not reply.<br/>---This is auto generated email---<br/>Regards:<br/>ERP HR Team<br/>IDS Infotech LTD.<br/>Url:'+url,
        'email_to': resign.employee_id.parent_id.work_email,
        'email_cc':  resign.employee_id.division.hr_email,
        'email_from': 'info.openerp@idsil.com',
          }
        #---------------------------------------------------------------
        mail_obj = self.pool.get('mail.mail') 
        msg_id = mail_obj.create(cr, uid, values, context=context) 
        if msg_id: 
            mail_obj.send(cr, uid, [msg_id], context=context)
        
        
        return self.write(cr, uid, ids, {'state': 'cancel'})
    
    def refuse_location(self, cr, uid, ids, context=None):
        """In case, resignation of employee is refused. """
        
        #code to update employee working status
        self._update_employee_working_status(cr, uid, ids, 'working', context=None)
        
        resign=self.browse(cr, uid, ids, context=None)
        url="http://ids-erp.idsil.loc:8069/web"
        values = {
        'subject': 'Resignation' + '-' + resign.employee_id.name,
        'body_html': 'Resignation of' +' '+resign.employee_id.name+' '+'is Refused.<br/><br/><br/>Kindly do not reply.<br/>---This is auto generated email---<br/>Regards:<br/>ERP HR Team<br/>IDS Infotech LTD.<br/>Url:'+url,
        'email_to': resign.employee_id.parent_id.work_email,
        'email_from': 'info.openerp@idsil.com',
          }
        #---------------------------------------------------------------
        mail_obj = self.pool.get('mail.mail') 
        msg_id = mail_obj.create(cr, uid, values, context=context) 
        if msg_id: 
            mail_obj.send(cr, uid, [msg_id], context=context)
        
        
        return self.write(cr, uid, ids, {'state': 'cancel'})
    
    def _update_employee_working_status(self, cr, uid, ids, working_status, context=None):
        """Updating final working status. """
        obj_separation = self.browse(cr, uid, ids)
        sep_emp_id = 0	
        obj_emp = self.pool.get('hr.employee')    
        for record in obj_separation:
            sep_emp_id = record.employee_id.id
        
        obj_emp.write(cr, SUPERUSER_ID , [sep_emp_id], {'working_status':working_status})
        
    def _initiated_get(self, cr, uid, context=None):        
        emp_id = context.get('default_employee_id', False)
        if emp_id:
            return emp_id
        ids = self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
        if ids:
            return ids[0]
        return False    	
	
    
    _name = 'ids.hr.employee.separation'        
    _inherit = ['mail.thread', 'ir.needaction_mixin'] 
    _description = "Employee Separation"
    _columns = {
                'rgn_number':fields.char('RGN Number', size=15, readonly=True),
                'initiated_by': fields.many2one('hr.employee', 'Resign Initiated By', required=True),
                'employee_id': fields.many2one('hr.employee', 'Employee', required=True),
                'emp_code': fields.char('Employee Code', size=20),
                'department_id':fields.many2one('hr.department', 'Department'),
                'job_id': fields.many2one('hr.job', 'Designation'),
                'confirmation_status': fields.related('employee_id', 'confirmation_status', type='char', relation='hr.employee', string='Confirmation Status', store=True, readonly=True),
                'separation_type': fields.many2one('ids.hr.employee.separation.type', 'Resignation Type', required=True),
                'rgn_accepted':fields.selection([('yes', 'Yes'),
                                           ('no', 'No'),
                                           ('na', 'N/A')], 'Resignation Accepted', required=True),
                'reason': fields.many2one('ids.hr.employee.separation.reason', 'Reason', required=True),
                'eligible_rehire': fields.boolean('Eligible for rehire?'),
                'capture_date': fields.date('Capture date', required=True),
                'last_date': fields.date('Last date in company', required=True),
#                 'interview_by': fields.many2one('hr.employee', 'Interview By', required=True),
                'user_id':fields.related('employee_id', 'user_id', type='many2one', relation='res.users', string='User', store=True),
                'manager_id1': fields.many2one('hr.employee', 'First Approval', invisible=False, readonly=True, help='This area is automatically filled by the user who approve/validate the resignation at first level'),
                'manager_id2': fields.many2one('hr.employee', 'Second Approval', invisible=False, readonly=True, help='This area is automatically filled by the user who approve/validate the resignation at second level'),
                'notes': fields.text('Notes'),                
                'state': fields.selection([('draft', 'Draft'),
                                           ('confirm', 'Waiting for Approval'),
                                           ('approve', 'Approved'),
                                           ('done', 'Validated'),
                                           ('cancel', 'Refused')], 'Status', readonly=True),
                'full_final_status': fields.selection([('pending', 'Pending'), ('done', 'Done')],'Full & Final Status'),                                                   
    }
    _rec_name = 'rgn_number'
    _defaults = {
        'state': 'draft', 
        'capture_date':fields.date.context_today,
        'full_final_status':'pending',
        #'initiated_by': _initiated_get
    }
    
    def create(self, cr, uid, vals, context=None):
        """Create the unique id used for F&F """
        vals['rgn_number']=self.pool.get('ir.sequence').get(cr, uid,'ids.hr.employee.separation')
        res=super(ids_hr_employee_separation, self).create(cr, uid, vals)
        return res
    
    def write(self, cr, uid, ids, vals, context=None):        
        """Updating final working status. """        
        if vals.get('full_final_status', False):
            if (vals['full_final_status'] == 'done'):                               
                self._update_employee_working_status(cr, uid, ids, 'exit', context=None)                                     
            if (vals['full_final_status'] == 'pending'):
                self._update_employee_working_status(cr, uid, ids, 'resigned', context=None)
        res=super(ids_hr_employee_separation, self).write(cr, uid, ids, vals)
        return res
    
    def unlink(self, cr, uid, ids, context=None):
        
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.state not in ['draft']:
                raise osv.except_osv(_('Warning!'),_('You cannot delete a resignation which is not in draft state.'))
        return super(ids_hr_employee_separation, self).unlink(cr, uid, ids, context)    
    
    def onchange_employee_id(self, cr, uid, ids, employee_id, capture_date, context=None):
        """get associated values of employee onchange of employee id. """
        value = {'department_id': False}
        notice_period_days=0
        if employee_id:
            employee = self.pool.get('hr.employee').browse(cr, uid, employee_id)
            notice_period_days = int(employee.notice)
            last_date = datetime.strptime(capture_date, "%Y-%m-%d")+timedelta(days=notice_period_days)
            value['department_id'] = employee.department_id.id
            value['emp_code'] = employee.emp_code
            value['job_id'] = employee.job_id.id
            value['initiated_by'] = employee.parent_id.id
            value['initiated_by'] = employee.parent_id.id
            value['last_date'] = last_date
            if employee.employment_type_id=='regular':
                value['confirmation_status'] = employee.confirmation_status
            else:
                value['confirmation_status'] = 'NA'
        return {'value': value}
    
    def _check_resignations(self, cr, uid, ids, context=None):        
        """Constraints on submitting resignation. """
        for obj in self.browse(cr, uid, ids, context=context):
            res_user_id = obj.user_id.id
            
        resignation_ids = self.search(cr, uid, [('id','not in',ids),('user_id', '=', res_user_id),('state', '!=', 'refuse')], context=context)
        
        if resignation_ids:
            raise osv.except_osv(_('Warning!'), _('Resignation is already in progress for this employee'))
        
        return True
    
    def _check_validate(self, cr, uid, ids, context=None):
        """Constraints on validating resignation. """
        users_obj = self.pool.get('res.users')
        
        if not users_obj.has_group(cr, uid, 'base.group_hr_manager'):
            for separation in self.browse(cr, uid, ids, context=context):
                if separation.employee_id.user_id.id == uid:
                    raise osv.except_osv(_('Warning!'), _('You cannot approve your own Resignation.'))
                if (separation.manager_id1 and separation.manager_id1.user_id.id == uid) or (separation.manager_id2 and separation.manager_id2.user_id.id == uid):
                    raise osv.except_osv(_('Warning!'), _('You have already approved the Resignation.'))
        return True
    
    def calculate_last_day(self, cr, uid, ids, employee_id, capture_date,context=None):       
        """Calculate last day from date of resignation. """
        notice_period_days=0
        if employee_id:
            employee = self.pool.get('hr.employee').browse(cr, uid,employee_id)     
            notice_period_days = int(employee.notice)
        last_date = datetime.strptime(capture_date, "%Y-%m-%d")+timedelta(days=notice_period_days)
        return {'value':{'last_date':datetime.strftime(last_date,DEFAULT_SERVER_DATE_FORMAT)}}
        

class ids_hr_employee_separation_type(osv.osv): 
    
    _name = 'ids.hr.employee.separation.type'
    _description = "Employee Separation Type"
    _columns = {
                'name': fields.char('Separation Type',size=100, required=True)                   
    }   
    
    _sql_constraints = [('name_unique','unique(name)','Separation type already exists')]
    _constraints = [(_check_unique_insesitive, 'Separation type already exists', ['name'])]
    
class ids_hr_employee_separation_reason(osv.osv): 
    
    _name = 'ids.hr.employee.separation.reason'
    _description = "Employee Separation Reason"
    _columns = {
                'name': fields.char('Reason',size=100, required=True)                   
    }   
    
    _sql_constraints = [('name_unique','unique(name)','Reason name already exists')]
    _constraints = [(_check_unique_insesitive, 'Reason name already exists', ['name'])]
    
        
