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
from openerp import netsvc
from openerp.tools.translate import _ 
from openerp import SUPERUSER_ID


class hr_employee(osv.osv):
    _inherit='hr.employee'
                        
    def create(self, cr, uid, data, context=None):
        """Automatic creation of record in technical information and triggers
            email to associated Manager, with the creation of new employee
             in hr.employee. """
        busi_pool=self.pool.get('ids.business.information')
        
        context = dict(context or {})
        if context.get("mail_broadcast"):
            context['mail_create_nolog'] = True
 
        employee_id = super(hr_employee, self).create(cr, uid, data, context=context)
        res={}
        parent_id=0
        name=data['name']
        job=data['job_id']
        department=data['department_id']
        doj=data['joining_date']
        employee_type= data['employment_type_id']
        division= data['division']
        parent= data['parent_id']
        res={
             'employee_id':employee_id,
             'department_id': department,
             }
        info_id=busi_pool.create(cr,uid,res, context=context)
        div=self.pool.get('division').search(cr,uid,[('id','=',division)])
        division_id=self.pool.get('division').browse(cr, uid, div, context=context)
        depart=self.pool.get('hr.department').search(cr,uid,[('id','=',department)])
        department_id=self.pool.get('hr.department').browse(cr, uid, depart, context=context)
        url="http://ids-erp.idsil.loc:8069/web"
        if parent:
            parent=self.search(cr,uid,[('id','=',parent)])
            parent_id=self.browse(cr, uid, parent, context=context)
            values = {
            'subject': 'New Employee Code Request',
            'body_html': 'Employee Information of new joinee has been updated successfully, please generate the employee code.<br/>Detail of user is given as follows: <br/>NAME : '+ name +'<br/>EMPLOYEE TYPE : '+ employee_type +'<br/>DOJ : '+ doj +'<br/>DIVISION : '+ division_id.name +'<br/>DEPARTMENT : '+ department_id.name +' <br/>REPORTING MANAGER : '+ parent_id.name +'<br/><br/><br/>Url:'+url,
            'email_to': 'sandeep.singh@idsil.com',
            'email_from': 'info.openerp@idsil.com',
              }
        else:
            values = {
            'subject': 'New Employee Code Request',
            'body_html': 'Employee Information of new joinee has been updated successfully, please generate the employee code.<br/>Detail of user is given as follows: <br/>NAME : '+ name +'<br/>EMPLOYEE TYPE : '+ employee_type +'<br/>DOJ : '+ doj +'<br/>DIVISION : '+ division_id.name +'<br/>DEPARTMENT : '+ department_id.name +' <br/>REPORTING MANAGER : N/A<br/><br/><br/>Url:'+url,
            'email_to': 'sandeep.singh@idsil.com',
            'email_from': 'info.openerp@idsil.com',
              }
            
        #---------------------------------------------------------------
        mail_obj = self.pool.get('mail.mail') 
        msg_id = mail_obj.create(cr, uid, values, context=context) 
        if msg_id: 
            mail_obj.send(cr, uid, [msg_id], context=context)
        
        if context.get("mail_broadcast"):
            self._broadcast_welcome(cr, uid, employee_id, context=context)
        return employee_id



class ids_technical_information(osv.osv):
    
    _name = 'ids.technical.information'
    _description = 'Technical Information'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    
   
    def _default_employee(self, cr, uid, context=None):
        emp_ids = self.pool.get('hr.employee').search(cr, uid, [('user_id','=',uid)], context=context)
        return emp_ids and emp_ids[0] or False
    
    def onchange_employee_id(self, cr, uid, ids, employee_id, context=None):
        """Gets information of employee from hr.employee onchange of empoyee id. """
        emp_code = ''
        department_id = ''
        job_id = ''
        department_name = ''
        job_name = ''
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
                        

        
        res = {'value': {'emp_code': emp_code, 'department_id': department_name, 'job_id': job_name}}                 
        
        return res
    
    
    def _get_employee_info(self, cr, uid, ids, name, args, context=None):
                
        result = {}
        emp_code = ''
        department_id = ''
        job_id = ''
        
        if not ids:
            return []
        
        for self_obj_new in self.browse(cr, uid, ids, context=context):
             
            emp_info = self.pool.get('hr.employee').read(cr, SUPERUSER_ID, [self_obj_new.employee_id.id], ['emp_code','department_id','job_id','joining_date','confirmation_date','confirmation_status'])                
                        
            if emp_info:                
                emp_code = emp_info[0]['emp_code']
                department_id = emp_info[0]['department_id'][1]
                job_id = emp_info[0]['job_id'][1]
                #result = dict.fromkeys(ids[self_obj_new.id], {'emp_code': emp_code, 'department_id': department_id, 'job_id': job_id, 'joining_date': joining_date, 'confirmation_date': confirmation_date, 'confirmation_status': confirmation_status})
                result[self_obj_new.id] = {'emp_code': emp_code, 'department_id': department_id, 'job_id': job_id}
               
        return result 
    
    _columns = {
                'employee_id': fields.many2one('hr.employee', 'Employee', required=True, domain="[('working_status', '!=', 'exit')]"),
                'emp_code': fields.function(_get_employee_info, type='char', string='Employee Code', multi='emp_info'),
                'department_id': fields.function(_get_employee_info, type='char', string='Department', multi='emp_info',store=True),
                'job_id': fields.function(_get_employee_info, type='char', string='Designation', multi='emp_info'),
                'allocation_of_itassets': fields.selection([('yes', 'Yes'), ('no','No')],'Allocation of IT Assets'),
                'email_created': fields.selection([('yes', 'Yes'), ('no','No')],'Email ID Created'),
                'internet_access_control': fields.selection([('yes', 'Yes'), ('no','No')],'Internet Access Control'),
                'backup_setup': fields.selection([('yes', 'Yes'), ('no','No')],'Back-Up Setup'),
                'software_provisioning_and_access_control': fields.selection([('yes', 'Yes'), ('no','No')],'Software Provisioning Control'),
                'application_share_access': fields.selection([('yes', 'Yes'), ('no','No')],'Application Share Access'),
                'allocation_of_itassets_remarks': fields.char('Assets Remarks'),
                'email_created_remarks': fields.char('Email ID Remarks'),
                'internet_access_control_remarks': fields.char('Internet Access Remarks'),
                'backup_setup_remarks': fields.char('Back-Up Remarks'),
                'software_provisioning_and_access_control_remarks': fields.char('Software Provisioning Remarks'),
                'application_share_access_remarks': fields.char('Share Access Remarks'),
                'technical_notes': fields.text('Remarks(For Manager/Leads)'),
                'technical_notes_it': fields.text('Remarks(For IT Team)'),
                'email_control': fields.selection([('local', 'Local Access'), ('full','Full Access'),('restricted','Restricted Access'),('none','None')],'Email Control'),
                'internet_control': fields.selection([('full', 'Full Access'), ('corporate_policy','Corporate Policy'),('restricted','Restricted Access'),('none','None')],'Internet Control'),
                'remote_control': fields.selection([('yes', 'Yes'), ('no','No')],'Remote Control'),
                'application_share_access_busi': fields.char('Application Share Access'),
                'email_remarks': fields.char('Email Remarks'),
                'internet_remarks': fields.char('Internet Remarks'),
                'backup_remarks': fields.char('Databack-up Details'),
                'software_requirements': fields.char('Software Requirements'),
                'state': fields.selection([
                                           ('draft', 'Draft'),
                                           ('submitted', 'Done'),
                                           ('validated', 'Validated'),            
                                           ('refused', 'Refused'),
                                           ],
                                          'Status', readonly=True,
                                          help='When the employee information change request is created the status is \'Draft\'.\n It is submitted by the employee and request is sent to Location HR, the status is \'submitted\'.\
                                          \nIf the Location Hr validate it, the status is \'Validated\'.\n If the Location Hr refuse it, the status is \'Refused\'.'),
                }
                     
    _sql_constraints = [
        ('tech_id_uniq', 'unique(employee_id)', 'Duplicate Entry!'),                                     
    ]    
    
    _rec_name = 'emp_code'
    _defaults = {
        'state': 'draft', 
        #'capture_date':fields.date.context_today
    }
    
    

 
    def submit(self, cr, uid, ids, context=None):
        """Workflow initiated-submit to Technical Support. """
        tech=self.browse(cr, uid, ids, context=context)
        emp_id=self.pool.get('hr.employee').search(cr,uid,[('id','=',tech.employee_id.id)])
        emp_data=self.pool.get('hr.employee').browse(cr, uid, emp_id, context=context)
        url="http://ids-erp.idsil.loc:8069/web"
        if emp_data.emp_code:
            if emp_data.parent_id:
                values = {
                    'subject': 'New User Access Detail',
                    'body_html': 'Technical information of new employee has been successfully updated, please check the Technical Information.<br/> Detail of user is given as follows: <br/>ECODE : '+ emp_data.emp_code +'<br/>NAME : '+ emp_data.name_related +'<br/>EMPLOYEE TYPE : '+ emp_data.employment_type_id +'<br/>DOJ : '+ emp_data.joining_date +'<br/>DIVISION : '+ emp_data.division.name +'<br/>DEPARTMENT : '+ emp_data.department_id.name +' <br/>REPORTING MANAGER : '+ emp_data.parent_id.name +'<br/><br/><br/>Url:'+url,
                    'email_to': tech.employee_id.parent_id.work_email,
                    'email_cc': {tech.employee_id.parent_id.parent_id.work_email,tech.employee_id.division.hr_email, 'sandeep.singh@idsil.com'},
                    'email_from': 'info.openerp@idsil.com',
                      }
            else:
                values = {
                    'subject': 'New User Access Detail',
                    'body_html': 'Technical information of new employee has been successfully updated, please check the Technical Information.<br/> Detail of user is given as follows: <br/>ECODE : '+ emp_data.emp_code +'<br/>NAME : '+ emp_data.name_related +'<br/>EMPLOYEE TYPE : '+ emp_data.employment_type_id +'<br/>DOJ : '+ emp_data.joining_date +'<br/>DIVISION : '+ emp_data.division.name +'<br/>DEPARTMENT : '+ emp_data.department_id.name +' <br/>REPORTING MANAGER :  N/A<br/><br/><br/>Url:'+url,
                    'email_to': tech.employee_id.parent_id.work_email,
                    'email_cc': {tech.employee_id.parent_id.parent_id.work_email,tech.employee_id.division.hr_email, 'sandeep.singh@idsil.com'},
                    'email_from': 'info.openerp@idsil.com',
                    }
        else:
            raise osv.except_osv(_('Warning!'), _('Employee Code is not Generated.')) 
        #---------------------------------------------------------------
        mail_obj = self.pool.get('mail.mail') 
        msg_id = mail_obj.create(cr, uid, values, context=context) 
        if msg_id: 
            mail_obj.send(cr, uid, [msg_id], context=context) 
        return self.write(cr, uid, ids, {'state': 'submitted'}, context=context)
    
    def write(self, cr, uid,ids,vals, context=None):
        record_id=self.browse(cr,uid, ids, context=context )
        cr.execute("update ids_technical_information set state='draft' where id=%s"%record_id.id);
        
        return super(ids_technical_information, self).write(cr, uid, ids, vals, context=context)
    
        return True
        
        
#     def validate(self, cr, uid, ids, context=None):
#         """Technical support give technical access and appove the form. """
#         tech=self.browse(cr, uid, ids, context=context)
#         emp_id=self.pool.get('hr.employee').search(cr,uid,[('id','=',tech.employee_id.id)])
#         emp_data=self.pool.get('hr.employee').browse(cr, uid, emp_id, context=context)
#         url="http://ids-erp.idsil.loc:8069/web"
#         values = {
#         'subject': 'New User Access Detail',
#         'body_html': 'Employee code of new employee has been generated successfully, please fill the Business Information.\nDetail of user is given as follows: \nECODE : '+ emp_data.emp_code +'\nNAME : '+ emp_data.name_related +'\nEMPLOYEE TYPE : '+ emp_data.employment_type_id +'\nDOJ : '+ emp_data.joining_date +'\nDIVISION : '+ emp_data.division.name +'\nDEPARTMENT : '+ emp_data.department_id.name +' \nREPORTING MANAGER : '+ emp_data.parent_id.name +'\n\n\n'+url,
#         'email_to': tech.employee_id.parent_id.work_email,
#         'email_cc': {tech.employee_id.parent_id.parent_id.work_email,tech.employee_id.office_location.work_email, 'sandeep.singh@idsil.com'},
#         'email_from': 'info.openerp@idsil.com',
#           }
#         #---------------------------------------------------------------
#         mail_obj = self.pool.get('mail.mail') 
#         msg_id = mail_obj.create(cr, uid, values, context=context) 
#         if msg_id: 
#             mail_obj.send(cr, uid, [msg_id], context=context)
#         return self.write(cr, uid, ids, {'state': 'draft'}, context=context)


class ids_business_information(osv.osv):
    
    _name = 'ids.business.information'
    _description = 'Business Information'
    
    _columns = {
                'employee_id': fields.many2one('hr.employee', 'Employee', required=True, domain="[('working_status', '!=', 'exit')]"),
                'department_id': fields.many2one('hr.department', string='Department'),
                'email_control': fields.selection([('local', 'Local Access'), ('full','Full Access'),('restricted','Restricted Access'),('none','None')],'Email Control'),
                'internet_control': fields.selection([('full', 'Full Access'), ('corporate_policy','Corporate Policy'),('restricted','Restricted Access'),('none','None')],'Internet Control'),
                'remote_control': fields.selection([('yes', 'Yes'), ('no','No')],'Remote Control'),
                'application_share_access': fields.char('Application Share Access'),
                'email_remarks': fields.char('Email Remarks'),
                'internet_remarks': fields.char('Internet Remarks'),
                'backup_remarks': fields.char('Databack-up Details'),
                'software_requirements': fields.char('Software Requirements'),
                'state': fields.selection([
                                           ('draft', 'Draft'),
                                           ('submitted', 'Done'),
                                           ],
                                          'Status', readonly=True)
                }
    
    _sql_constraints = [
        ('employee_id_uniq', 'unique(employee_id)', 'Duplicate Entry')                                   
    ]  
    
     
    _defaults = {
        'state': 'draft', 
    } 
    
                     
    
    def onchange_employee_id(self, cr, uid, ids, employee_id, context=None):
        """Gets information of employee from hr.employee onchange of empoyee id. """
        department_id = ''    
        if employee_id:
            record = self.pool.get('hr.employee').browse(cr,uid,employee_id,context=context)             
            department_id = record.department_id.id
                    
        res = {'value': {'department_id': department_id}}                 
        
        return res


    def submit(self, cr, uid, ids, context=None):
        """Workflow initiated-submit to Technical Support. """
        
        tech_pool=self.pool.get('ids.technical.information')
        
        tech=self.browse(cr, uid, ids, context=context)
        tech_id=tech_pool.search(cr, uid, [('employee_id', '=', tech.employee_id.id)])
        tech_data=tech_pool.browse(cr, uid, tech_id, context=context)

        emp_id=self.pool.get('hr.employee').search(cr,uid,[('id','=',tech.employee_id.id)])
        emp_data=self.pool.get('hr.employee').browse(cr, uid, emp_id, context=context)
        res={}
        res={
             'employee_id':emp_data.id,
             'department_id': emp_data.department_id.id,
             'job_id': emp_data.job_id.id,
             'email_control': tech.email_control,
             'internet_control': tech.internet_control,
             'remote_control': tech.remote_control,
             'application_share_access_busi': tech.application_share_access,
             'email_remarks': tech.email_remarks,
             'internet_remarks': tech.internet_remarks,
             'backup_remarks': tech.backup_remarks,
             'software_requirements': tech.software_requirements,
             }
        
        tech_id=tech_pool.search(cr, uid, [('employee_id', '=', tech.employee_id.id)])
        tech_data=tech_pool.browse(cr, uid, tech_id, context=context)
        if tech_data.employee_id.id<>tech.employee_id.id:
            info_id=tech_pool.create(cr,uid,res, context=context)
        
        url="http://ids-erp.idsil.loc:8069/web"
        if emp_data.emp_code:
            if emp_data.parent_id:
                values = {
                    'subject': 'New User Access Request',
                    'body_html': 'Business information of new employee has been successfully updated, please fill the Technical Information.<br/>Detail of user is given as follows: <br/>ECODE : '+ emp_data.emp_code +'<br/>NAME : '+ emp_data.name_related +'<br/>EMPLOYEE TYPE : '+ emp_data.employment_type_id +'<br/>DOJ : '+ emp_data.joining_date +'<br/>DIVISION : '+ emp_data.division.name +'<br/>DEPARTMENT : '+ emp_data.department_id.name +' <br/>REPORTING MANAGER : '+ emp_data.parent_id.name +'<br/><br/><br/>Url:'+url,
                    'email_to': 'mohtech1@idsil.com',
                    'email_cc': {tech.employee_id.parent_id.parent_id.work_email,tech.employee_id.division.hr_email, 'sandeep.singh@idsil.com'},
                    'email_from': 'info.openerp@idsil.com',
                    }
            else:
                values = {
                    'subject': 'New User Access Request',
                    'body_html': 'Business information of new employee has been successfully updated, please fill the Technical Information.<br/>Detail of user is given as follows: <br/>ECODE : '+ emp_data.emp_code +'<br/>NAME : '+ emp_data.name_related +'<br/>EMPLOYEE TYPE : '+ emp_data.employment_type_id +'<br/>DOJ : '+ emp_data.joining_date +'<br/>DIVISION : '+ emp_data.division.name +'<br/>DEPARTMENT : '+ emp_data.department_id.name +' <br/>REPORTING MANAGER : N/A <br/><br/><br/>Url:'+url,
                    'email_to': 'mohtech1@idsil.com',
                    'email_cc': {tech.employee_id.parent_id.parent_id.work_email,tech.employee_id.division.hr_email, 'sandeep.singh@idsil.com'},
                    'email_from': 'info.openerp@idsil.com',
                    }
        else:
            raise osv.except_osv(_('Warning!'), _('Employee Code is not Generated.')) 
        #---------------------------------------------------------------
        mail_obj = self.pool.get('mail.mail') 
        msg_id = mail_obj.create(cr, uid, values, context=context) 
        if msg_id: 
            mail_obj.send(cr, uid, [msg_id], context=context) 
            
        return self.write(cr, uid, ids, {'state': 'submitted'}, context=context)
    
    def write(self, cr, uid,ids,vals, context=None):
        
        record_id=self.browse(cr,uid, ids, context=context )
        cr.execute("update ids_business_information set state='draft' where id=%s"%record_id.id);
        
        
        if 'email_control' in vals:
            cr.execute("update ids_technical_information set email_control=%s where employee_id=%s ",(vals['email_control'],record_id.employee_id.id))
        if 'internet_control' in vals:
            cr.execute("update ids_technical_information set internet_control=%s where employee_id=%s ",(vals['internet_control'],record_id.employee_id.id))
        if 'remote_control' in vals:
            cr.execute("update ids_technical_information set remote_control=%s where employee_id=%s ",(vals['remote_control'],record_id.employee_id.id))
        if 'application_share_access' in vals:
            cr.execute("update ids_technical_information set application_share_access_busi=%s where employee_id=%s ",(vals['application_share_access'],record_id.employee_id.id))
        if 'email_remarks' in vals:
            cr.execute("update ids_technical_information set email_remarks=%s where employee_id=%s ",(vals['email_remarks'],record_id.employee_id.id))
        if 'internet_remarks' in vals:
            cr.execute("update ids_technical_information set internet_remarks=%s where employee_id=%s ",(vals['internet_remarks'],record_id.employee_id.id))
        if 'backup_remarks' in vals:
            cr.execute("update ids_technical_information set backup_remarks=%s where employee_id=%s ",(vals['backup_remarks'],record_id.employee_id.id))
        if 'software_requirements' in vals:
            cr.execute("update ids_technical_information set software_requirements=%s where employee_id=%s ",(vals['software_requirements'],record_id.employee_id.id))           
        
        
        return super(ids_business_information, self).write(cr, uid, ids, vals, context=context)
    
    
    
    
    
    