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
from openerp import api
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from openerp import netsvc
from lxml import etree
from openerp.tools.translate import _

class ids_emp_info_change(osv.osv):
    
    _name = 'ids.emp.info.change'
    _description = "Employee Information Change"
    
    def _employee_get(self, cr, uid, context=None): 
        """Gets default value from the hr.employee. """       
        emp_id = context.get('default_employee_id', False)
        if emp_id:
            return emp_id
        ids = self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
        if ids:
            return ids[0]
        return False           
    _columns = {
                'name':fields.char('Name', size=100),
                'division_id':fields.many2one('division', 'Division'),
                'emp_code':fields.char('Employee Code', size=100),
                'employee_id':fields.many2one('hr.employee','Employee Name'),
                'req_date':fields.date('Request Date'),
                'date':fields.date('Date'),
                'marital': fields.selection([('single', 'Single'), ('married', 'Married'), ('widower', 'Widower'), ('divorced', 'Divorced')], 'Marital Status'),
                'doa':fields.date('Date Of Anniversary'),
                'email':fields.char('Email',  size=240),
                'blood_groups':fields.selection([('1','A+'),('2','B+'),('3','A-'),('4','B-'),('5','O+'),('6','O-'),('7','AB+'),('8','AB-')], 'Blood Group'),
                'mobile_no':fields.char('Mobile', size=240),
                'home_phone':fields.char('Home Phone', size=240),
                'local_address':fields.char('Local Address'),
                'pin_local':fields.char('Pin', size=100),
                'permanent_address':fields.char('Permanent Address'),
                'pin_permanent':fields.char('Pin', size=100),
                'weight':fields.char('Weight', size=100),
                'height':fields.char('Height', size=100),
                'passport_no':fields.char('Passport No.', size=100),
                'passport_till':fields.date('Passport Till'),
                'vehicle':fields.char('Vehicle'),
                'hobby':fields.char('Hobby'),
                'spouse_name':fields.char('Spouse Name'),
                'child_name1':fields.char('Child Name'),
                'dob1':fields.date('DOB'),
                'child_name2':fields.char('Child Name'),
                'dob2':fields.date('DOB'),
                'emerg_per_name':fields.char('Emergency Person Name'),
                'emerg_per_relation':fields.char('Emergency Person Relation'),
                'emerg_address':fields.char('Emergency Address'),
                'emerg_pin':fields.char('Emergency Pin'),
                'emerg_contact_no':fields.char('Emergency Contact Number'),
                'text1':fields.char('Text1'),
                'text2':fields.char('Text2'),
                'text3':fields.char('Text3'),
                'text4':fields.char('Text4'),
                'text5':fields.char('Text5'),
                'text6':fields.char('Text6'),
                'text7':fields.char('Text7'),
                'text8':fields.char('Text8'),
                'text9':fields.char('Text9'),
                'text10':fields.char('Text10'),
                'text11':fields.char('Text11'),
                'text12':fields.char('Text12'),
                'text13':fields.char('Text13'),
                'text14':fields.char('Text14'),
                'text15':fields.char('Text15'),
                'text16':fields.char('Text16'),
                'text17':fields.char('Text17'),
                'text18':fields.char('Text18'),
                'text19':fields.char('Text19'),
                'text20':fields.char('Text20'),
                'text21':fields.char('Text21'),
                'text22':fields.char('Text22'),
                'text23':fields.char('Text23'),
                'text24':fields.char('Text24'),
                'text25':fields.char('Text25'),
                'text26':fields.char('Text26'),
                'marital_prev': fields.selection([('single', 'Single'), ('married', 'Married'), ('widower', 'Widower'), ('divorced', 'Divorced')], 'Marital Status'),
                'doa_prev':fields.date('Date Of Anniversary'),
                'email_prev':fields.char('Email',  size=240),
                'blood_groups_prev':fields.selection([('1','A+'),('2','B+'),('3','A-'),('4','B-'),('5','O+'),('6','O-'),('7','AB+'),('8','AB-')], 'Blood Group'),
                'mobile_no_prev':fields.char('Mobile', size=240),
                'home_phone_prev':fields.char('Home Phone', size=240),
                'local_address_prev':fields.char('Local Address'),
                'pin_local_prev':fields.char('Pin', size=100),
                'permanent_address_prev':fields.char('Permanent Address'),
                'pin_permanent_prev':fields.char('Pin', size=100),
                'weight_prev':fields.char('Weight', size=100),
                'height_prev':fields.char('Height', size=100),
                'passport_no_prev':fields.char('Passport No.', size=100),
                'passport_till_prev':fields.date('Passport Till'),
                'vehicle_prev':fields.char('Vehicle'),
                'hobby_prev':fields.char('Hobby'),
                'spouse_name_prev':fields.char('Spouse Name'),
                'child_name1_prev':fields.char('Child Name'),
                'dob1_prev':fields.date('DOB'),
                'child_name2_prev':fields.char('Child Name'),
                'dob2_prev':fields.date('DOB'),
                'emerg_per_name_prev':fields.char('Emergency Person Name'),
                'emerg_per_relation_prev':fields.char('Emergency Person Relation'),
                'emerg_address_prev':fields.char('Emergency Address'),
                'emerg_pin_prev':fields.char('Emergency Pin'),
                'emerg_contact_no_prev':fields.char('Emergency Contact Number'),
                'state': fields.selection([
                                           ('draft', 'Draft'),
                                           ('submitted', 'Waiting For Approval'),
                                           ('validated', 'Approved'),            
                                           ('refused', 'Refused'),
                                           ],
                                          'Status', readonly=True,
                                          help='When the employee information change request is created the status is \'Draft\'.\n It is submitted by the employee and request is sent to Location HR, the status is \'submitted\'.\
                                          \nIf the Location Hr validate it, the status is \'Validated\'.\n If the Location Hr refuse it, the status is \'Refused\'.'),
                }
    
    _defaults = {
        'employee_id': _employee_get,
        'state': 'draft',
        'req_date': lambda *a: time.strftime("%Y-%m-%d"),
    }
    
    
    def unlink(self, cr, uid, ids, context=None):
        for item in self.browse(cr, uid, ids, context=context):
            if item.state not in ('draft'):
                raise osv.except_osv(_('Warning!'),_('You cannot delete a request which is not draft!'))
        return super(ids_emp_info_change, self).unlink(cr, uid, ids, context=context)
    
    def onchange_employee_id(self, cr, uid, ids, employee_id, context=None):
        """Get all the values associated with employee with onchange of employee id
            from hr.employee. """
        emp_code = ''
        marital = ''
        doa = ''
        email = ''
        blood_group = ''
        mobile_no = ''
        home_phone = ''
        local_address = ''
        pin_local = ''
        permanent_address = ''
        pin_permanent = ''
        weight = ''
        height = ''
        passport_no = ''
        passport_till = ''
        vehicle = ''
        hobby = ''
        spouse_name = ''
        child_name1 = ''
        dob1 = ''
        child_name2 = ''
        dob2 = ''
        emerg_per_name = ''
        emerg_per_relation = ''
        emerg_address = ''
        emerg_pin = ''
        emerg_contact_no = ''
        division_id=''
        obj_emp = self.pool.get('hr.employee')        
        res={}    
        if employee_id:
            record = obj_emp.browse(cr,uid,employee_id,context=context)            
            
            if record:    
                emp_code = record.emp_code
                marital = record.marital
                doa = record.marriage_date
                email = record.work_email
                blood_group = record.blood_groups
                mobile_no = record.mobile_phone
                home_phone = record.work_phone
                permanent_address = record.permanent_address
                weight = record.weight
                height = record.height
                passport_no = record.passport_id
                local_address = record.current_address
                division_id=record.division
                res = {'value': {
                                 'emp_code': emp_code,
                                 'marital': marital,
                                 'email': email,
                                 'blood_groups': blood_group,
                                 'mobile_no': mobile_no,
                                 'home_phone': home_phone,
                                 'permanent_address': permanent_address,
                                 'weight': weight,
                                 'height': height,
                                 'passport_no': passport_no,
                                 'local_address' : local_address,
                                 'doa' : doa,
                                 
                                 'marital_prev': marital,
                                 'email_prev': email,
                                 'blood_groups_prev': blood_group,
                                 'mobile_no_prev': mobile_no,
                                 'home_phone_prev': home_phone,
                                 'permanent_address_prev': permanent_address,
                                 'weight_prev': weight,
                                 'height_prev': height,
                                 'passport_no_prev': passport_no,
                                 'local_address_prev' : local_address,
                                 'doa_prev' : doa,
                                 'division_id': division_id
                                 
                                 
                                }
                       }
                      
        return res
    
    def submit(self, cr, uid, ids, context=None):
        """Submit the form to Location HR. """
        change=self.browse(cr, uid, ids, context=context)
        if change.marital<>change.marital_prev:
            self.write(cr, uid, ids, {'text1': 'Update'}, context=context)
        if change.email<>change.email_prev:
            self.write(cr, uid, ids, {'text2': 'Update'}, context=context)
        if change.mobile_no<>change.mobile_no_prev:
            self.write(cr, uid, ids, {'text3': 'Update'}, context=context)
        if change.local_address<>change.local_address_prev:
            self.write(cr, uid, ids, {'text4': 'Update'}, context=context)
        if change.permanent_address<>change.permanent_address_prev:
            self.write(cr, uid, ids, {'text5': 'Update'}, context=context)
        if change.weight<>change.weight_prev:
            self.write(cr, uid, ids, {'text6': 'Update'}, context=context)
        if change.passport_no<>change.passport_no_prev:
            self.write(cr, uid, ids, {'text7': 'Update'}, context=context)
        if change.vehicle<>change.vehicle_prev:
            self.write(cr, uid, ids, {'text8': 'Update'}, context=context)
        if change.child_name1<>change.child_name1_prev:
            self.write(cr, uid, ids, {'text9': 'Update'}, context=context)
        if change.child_name2<>change.child_name2_prev:
            self.write(cr, uid, ids, {'text10': 'Update'}, context=context)
        if change.emerg_per_name<>change.emerg_per_name_prev:
            self.write(cr, uid, ids, {'text11': 'Update'}, context=context)
        if change.emerg_address<>change.emerg_address_prev:
            self.write(cr, uid, ids, {'text12': 'Update'}, context=context)
        if change.emerg_contact_no<>change.emerg_contact_no_prev:
            self.write(cr, uid, ids, {'text13': 'Update'}, context=context)
        if change.doa<>change.doa_prev:
            self.write(cr, uid, ids, {'text14': 'Update'}, context=context)
        if change.blood_groups<>change.blood_groups_prev:
            self.write(cr, uid, ids, {'text15': 'Update'}, context=context)
        if change.home_phone<>change.home_phone_prev:
            self.write(cr, uid, ids, {'text16': 'Update'}, context=context)
        if change.pin_local<>change.pin_local_prev:
            self.write(cr, uid, ids, {'text17': 'Update'}, context=context)
        if change.pin_permanent<>change.pin_permanent_prev:
            self.write(cr, uid, ids, {'text18': 'Update'}, context=context)
        if change.height<>change.height_prev:
            self.write(cr, uid, ids, {'text19': 'Update'}, context=context)
        if change.passport_till<>change.passport_till_prev:
            self.write(cr, uid, ids, {'text20': 'Update'}, context=context)
        if change.hobby<>change.hobby_prev:
            self.write(cr, uid, ids, {'text21': 'Update'}, context=context)
        if change.dob1<>change.dob1_prev:
            self.write(cr, uid, ids, {'text22': 'Update'}, context=context)
        if change.dob2<>change.dob2_prev:
            self.write(cr, uid, ids, {'text23': 'Update'}, context=context)
        if change.emerg_per_relation<>change.emerg_per_relation_prev:
            self.write(cr, uid, ids, {'text24': 'Update'}, context=context)
        if change.emerg_pin<>change.emerg_pin_prev:
            self.write(cr, uid, ids, {'text25': 'Update'}, context=context)
        if change.spouse_name<>change.spouse_name_prev:
            self.write(cr, uid, ids, {'text26': 'Update'}, context=context)
        url="http://ids-erp.idsil.loc:8069/web"
        if change.mobile_no<>change.mobile_no_prev or change.local_address<>change.local_address_prev:
            
            values = {
            'subject': 'Employee Information Change Request',
            'body_html': change.employee_id.display_name + ' ' + 'created change request for Mobile No./Local Address.<br/> Please take necessary action.<br/><br/><br/>Kindly do not reply.<br/>---This is auto generated email---<br/>Regards:<br/>ERP HR Team<br/>IDS Infotech LTD.<br/><br/>Url:'+url,
            'email_to': change.employee_id.division.hr_email,
            'email_cc': change.employee_id.parent_id.work_email,
            'email_from': 'info.openerp@idsil.com',
            }
        
        else:
            values = {
            'subject': 'Employee Information Change Request',
            'body_html': change.employee_id.display_name + ' ' + 'created change request . <br/>Please take necessary action.<br/><br/><br/>Kindly do not reply.<br/>---This is auto generated email---<br/>Regards:<br/>ERP HR Team<br/>IDS Infotech LTD.<br/><br/>Url:'+url,
            'email_to': change.employee_id.division.hr_email,
            'email_from': 'info.openerp@idsil.com',
              }
        
        
            
        #---------------------------------------------------------------
        mail_obj = self.pool.get('mail.mail') 
        msg_id = mail_obj.create(cr, uid, values, context=context) 
        if msg_id: 
            mail_obj.send(cr, uid, [msg_id], context=context) 
            print"mail sent successfully======"
        return self.write(cr, uid, ids, {'state': 'submitted'}, context=context)
    def validate(self, cr, uid, ids, context=None):
        """Validation Process """
        change=self.browse(cr, uid, ids, context=context)
        if change.marital<>change.marital_prev:
            self.write(cr, uid, ids, {'text1': 'Updated'}, context=context)
        if change.email<>change.email_prev:
            self.write(cr, uid, ids, {'text2': 'Updated'}, context=context)
        if change.mobile_no<>change.mobile_no_prev:
            self.write(cr, uid, ids, {'text3': 'Updated'}, context=context)
        if change.local_address<>change.local_address_prev:
            self.write(cr, uid, ids, {'text4': 'Updated'}, context=context)
        if change.permanent_address<>change.permanent_address_prev:
            self.write(cr, uid, ids, {'text5': 'Updated'}, context=context)
        if change.weight<>change.weight_prev:
            self.write(cr, uid, ids, {'text6': 'Updated'}, context=context)
        if change.passport_no<>change.passport_no_prev:
            self.write(cr, uid, ids, {'text7': 'Updated'}, context=context)
        if change.vehicle<>change.vehicle_prev:
            self.write(cr, uid, ids, {'text8': 'Updated'}, context=context)
        if change.child_name1<>change.child_name1_prev:
            self.write(cr, uid, ids, {'text9': 'Updated'}, context=context)
        if change.child_name2<>change.child_name2_prev:
            self.write(cr, uid, ids, {'text10': 'Updated'}, context=context)
        if change.emerg_per_name<>change.emerg_per_name_prev:
            self.write(cr, uid, ids, {'text11': 'Updated'}, context=context)
        if change.emerg_address<>change.emerg_address_prev:
            self.write(cr, uid, ids, {'text12': 'Updated'}, context=context)
        if change.emerg_contact_no<>change.emerg_contact_no_prev:
            self.write(cr, uid, ids, {'text13': 'Updated'}, context=context)
        if change.doa<>change.doa_prev:
            self.write(cr, uid, ids, {'text14': 'Updated'}, context=context)
        if change.blood_groups<>change.blood_groups_prev:
            self.write(cr, uid, ids, {'text15': 'Updated'}, context=context)
        if change.home_phone<>change.home_phone_prev:
            self.write(cr, uid, ids, {'text16': 'Updated'}, context=context)
        if change.pin_local<>change.pin_local_prev:
            self.write(cr, uid, ids, {'text17': 'Updated'}, context=context)
        if change.pin_permanent<>change.pin_permanent_prev:
            self.write(cr, uid, ids, {'text18': 'Updated'}, context=context)
        if change.height<>change.height_prev:
            self.write(cr, uid, ids, {'text19': 'Updated'}, context=context)
        if change.passport_till<>change.passport_till_prev:
            self.write(cr, uid, ids, {'text20': 'Updated'}, context=context)
        if change.hobby<>change.hobby_prev:
            self.write(cr, uid, ids, {'text21': 'Updated'}, context=context)
        if change.dob1<>change.dob1_prev:
            self.write(cr, uid, ids, {'text22': 'Updated'}, context=context)
        if change.dob2<>change.dob2_prev:
            self.write(cr, uid, ids, {'text23': 'Updated'}, context=context)
        if change.emerg_per_relation<>change.emerg_per_relation_prev:
            self.write(cr, uid, ids, {'text24': 'Updated'}, context=context)
        if change.emerg_pin<>change.emerg_pin_prev:
            self.write(cr, uid, ids, {'text25': 'Updated'}, context=context)
        if change.spouse_name<>change.spouse_name_prev:
            self.write(cr, uid, ids, {'text26': 'Updated'}, context=context)
        email=change.employee_id.work_email
        emp_obj=self.pool.get('hr.employee')
        emp_id=emp_obj.search(cr, uid, [('id','=',change.employee_id.id)])
        emp_data = emp_obj.browse(cr, uid, emp_id)
        if emp_data:
            emp_obj.write(cr, uid, emp_data.id, {
                                         'marital': change.marital,
                                         'marriage_date': change.doa,
                                         'work_email': change.email,
                                         'blood_groups': change.blood_groups,
                                         'mobile_phone': change.mobile_no,
                                         'work_phone': change.home_phone,
                                         'permanent_address': change.permanent_address,
                                         'weight': change.weight,
                                         'height': change.height,
                                         'passport_id': change.passport_no,
                                         'current_address': change.local_address,}, context=context)
        url="http://ids-erp.idsil.loc:8069/web"
        if change.mobile_no<>change.mobile_no_prev or change.local_address<>change.local_address_prev:
            values = {
            'subject': 'Employee Information Change Request',
            'body_html': 'Your change request for Mobile No./Local Address is approved.<br/><br/><br/>Kindly do not reply.<br/>---This is auto generated email---<br/>Regards:<br/>ERP HR Team<br/>IDS Infotech LTD.<br/><br/>Url:'+url,
            'email_to': email,
            'email_cc': change.employee_id.parent_id.work_email,
            'email_from': 'info.openerp@idsil.com',
            }
        else:
            values = {
            'subject': 'Information Change Request Status',
            'body_html': 'Your change request is approved.<br/><br/><br/>Kindly do not reply.<br/>---This is auto generated email---<br/>Regards:<br/>ERP HR Team<br/>IDS Infotech LTD.<br/><br/>Url:'+url,
            'email_to': email,
            'email_from': 'info.openerp@idsil.com',
              }
        
        #---------------------------------------------------------------
        mail_obj = self.pool.get('mail.mail') 
        msg_id = mail_obj.create(cr, uid, values, context=context) 
        if msg_id: 
            mail_obj.send(cr, uid, [msg_id], context=context)
        date = time.strftime("%Y-%m-%d"), 
        return self.write(cr, uid, ids, {'state': 'validated','date': date}, context=context)
    def refuse(self, cr, uid, ids, context=None):
        """In case, Form get refused. """
        change=self.browse(cr, uid, ids, context=context)
        if change.marital<>change.marital_prev:
            self.write(cr, uid, ids, {'text1': 'Not Updated'}, context=context)
        if change.email<>change.email_prev:
            self.write(cr, uid, ids, {'text2': 'Not Updated'}, context=context)
        if change.mobile_no<>change.mobile_no_prev:
            self.write(cr, uid, ids, {'text3': 'Not Updated'}, context=context)
        if change.local_address<>change.local_address_prev:
            self.write(cr, uid, ids, {'text4': 'Not Updated'}, context=context)
        if change.permanent_address<>change.permanent_address_prev:
            self.write(cr, uid, ids, {'text5': 'Not Updated'}, context=context)
        if change.weight<>change.weight_prev:
            self.write(cr, uid, ids, {'text6': 'Not Updated'}, context=context)
        if change.passport_no<>change.passport_no_prev:
            self.write(cr, uid, ids, {'text7': 'Not Updated'}, context=context)
        if change.vehicle<>change.vehicle_prev:
            self.write(cr, uid, ids, {'text8': 'Not Updated'}, context=context)
        if change.child_name1<>change.child_name1_prev:
            self.write(cr, uid, ids, {'text9': 'Not Updated'}, context=context)
        if change.child_name2<>change.child_name2_prev:
            self.write(cr, uid, ids, {'text10': 'Not Updated'}, context=context)
        if change.emerg_per_name<>change.emerg_per_name_prev:
            self.write(cr, uid, ids, {'text11': 'Not Updated'}, context=context)
        if change.emerg_address<>change.emerg_address_prev:
            self.write(cr, uid, ids, {'text12': 'Not Updated'}, context=context)
        if change.emerg_contact_no<>change.emerg_contact_no_prev:
            self.write(cr, uid, ids, {'text13': 'Not Updated'}, context=context)
        if change.doa<>change.doa_prev:
            self.write(cr, uid, ids, {'text14': 'Not Updated'}, context=context)
        if change.blood_group<>change.blood_group_prev:
            self.write(cr, uid, ids, {'text15': 'Not Updated'}, context=context)
        if change.home_phone<>change.home_phone_prev:
            self.write(cr, uid, ids, {'text16': 'Not Updated'}, context=context)
        if change.pin_local<>change.pin_local_prev:
            self.write(cr, uid, ids, {'text17': 'Not Updated'}, context=context)
        if change.pin_permanent<>change.pin_permanent_prev:
            self.write(cr, uid, ids, {'text18': 'Not Updated'}, context=context)
        if change.height<>change.height_prev:
            self.write(cr, uid, ids, {'text19': 'Not Updated'}, context=context)
        if change.passport_till<>change.passport_till_prev:
            self.write(cr, uid, ids, {'text20': 'Not Updated'}, context=context)
        if change.hobby<>change.hobby_prev:
            self.write(cr, uid, ids, {'text21': 'Not Updated'}, context=context)
        if change.dob1<>change.dob1_prev:
            self.write(cr, uid, ids, {'text22': 'Not Updated'}, context=context)
        if change.dob2<>change.dob2_prev:
            self.write(cr, uid, ids, {'text23': 'Not Updated'}, context=context)
        if change.emerg_per_relation<>change.emerg_per_relation_prev:
            self.write(cr, uid, ids, {'text24': 'Not Updated'}, context=context)
        if change.emerg_pin<>change.emerg_pin_prev:
            self.write(cr, uid, ids, {'text25': 'Not Updated'}, context=context)
        if change.spouse_name<>change.spouse_name_prev:
            self.write(cr, uid, ids, {'text26': 'Not Updated'}, context=context)
        email=change.employee_id.work_email
        url="http://ids-erp.idsil.loc:8069/web"
        if change.mobile_no<>change.mobile_no_prev or change.local_address<>change.local_address_prev:
            values = {
            'subject': 'Employee Information Change Request',
            'body_html': 'Your change request for Mobile No./Local Address is refused . <br/>Please Contact to your HR department.<br/><br/><br/>Kindly do not reply.<br/>---This is auto generated email---<br/>Regards:<br/>ERP HR Team<br/>IDS Infotech LTD.<br/><br/>Url:'+url,
            'email_to': email,
            'email_cc': change.employee_id.parent_id.work_email,
            'email_from': 'info.openerp@idsil.com',
            }
        else:
            values = {
            'subject': 'Information Change Request Status',
            'body_html': 'Your change request is refused .<br/> Please Contact to your HR department.<br/><br/><br/>Kindly do not reply.<br/>---This is auto generated email---<br/>Regards:<br/>ERP HR Team<br/>IDS Infotech LTD.<br/><br/>Url:'+url,
            'email_to': email,
            'email_from': 'info.openerp@idsil.com',
              }
        
        
        #---------------------------------------------------------------
        mail_obj = self.pool.get('mail.mail') 
        msg_id = mail_obj.create(cr, uid, values, context=context) 
        if msg_id: 
            mail_obj.send(cr, uid, [msg_id], context=context)
        date = time.strftime("%Y-%m-%d"), 
        return self.write(cr, uid, ids, {'state': 'refused','date': date}, context=context)
    
    
    
    
