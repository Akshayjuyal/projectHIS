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

class hr_employee(osv.osv):
    _name = 'hr.employee'
    _inherits = {'ids.hr.medical.detail': "medical_detail_id", 'ids.hr.employee.background.detail': "background_detail_id",}
    _inherit = 'hr.employee'    
    
    def is_visible(self, cr, uid, ids, name, args, context=None):
        """Make form visible to certain groups. """
        bl = True
        result = {}
        emp_manager_ids = []
        
        if not ids:
            return []
        else:
            
            #get admin ids
            admin_ids = self.pool.get('res.users').search(cr, uid , [('login','=','admin')], context=context)
            
            if (uid in admin_ids):
                   bl = False
            else:
                #start of code to get employee Manager/Officer user ids
                group_id = self.pool.get('res.groups').search(cr, uid , [('name','=','Employee')], context=context)
                
                group_cat = self.pool.get('res.groups').read(cr, uid, group_id, ['category_id'])
                
                cr.execute("""SELECT
                    distinct(rugl.uid)
                from
                    res_groups_users_rel rugl
                    join res_groups rg on (rg.id=rugl.gid)
                where
                    rg.category_id=(%i) and
                    rg.name = 'Manager' or rg.name = 'Finance Head'"""%group_cat[0]['id'])
                
                res = cr.dictfetchall()
                for r in res:
                    emp_manager_ids.append(r['uid'])
                
                if (uid in emp_manager_ids):
                    bl = False
                #end of code to get employee Manager/Officer user ids          
                
                for self_obj in self.browse(cr, uid, ids, context=context):
                    if (self_obj.user_id and (self_obj.user_id.id == uid)):
                        bl = False

            for self_obj_new in self.browse(cr, uid, ids, context=context):
                result[self_obj_new.id] = bl		  				
                
        return result
    def _attendance_access(self, cr, uid, ids, name, args, context=None):
        # this function field use to hide attendance button to singin/singout from menu
        visible = self.pool.get("res.users").has_group(cr, uid, "ids_hr_attendance.group_attendance_icon")
        return dict([(x, visible) for x in ids])

    _columns = {
                'total_cost':fields.related('contract_id', 'current_tctc', type='integer', relation='hr.contract', string='Total Cost', readonly=True),
                'attendance_access': fields.function(_attendance_access, string='Attendance Access', type='boolean'),
                'emp_code':fields.char('Employee Code', size=7),
                'biometric_code':fields.char('Biometric Code', size=7),
                'office_location':fields.many2one('office.location', 'Office Location'),
                'division':fields.many2one('division', 'Division'),
                'religion_id':fields.many2one('ids.hr.religion', 'Religion'),
                'aadhar_card_no':fields.char('Aadhar Card No', size=20),
                'voter_card_no':fields.char('Voter Card No', size=20),
                'ration_card_no':fields.char('Ration Card No', size=20),
                'driving_license_no':fields.char('Driving License No', size=20),
                'npr_no':fields.char('NPR No', size=20, help='National Population Registration Number'),
                'pan_id':fields.char('PAN Card No', size=10),
                'marriage_date':fields.date('Marriage Date'),
                'lang_speak_ids':fields.many2many('ids.hr.language','rel_empspeak_lang', 'employee_id','language_id', 'Languages Speak'),
                'lang_write_ids':fields.many2many('ids.hr.language','rel_empwrite_lang', 'employee_id','language_id', 'Languages Write'),
                'education_category':fields.selection([('illiterate','Illiterate'), ('non_matric','Non Matric'), ('matric','Matric'), ('senior_secondary','Senior Secondary'),('graduate','Graduate'),('post_graduate','Post Graduate')], 'Education Category'),
                'education_ids':fields.one2many('ids.hr.education.detail','employee_id', 'Courses'),
                'verification_ids':fields.one2many('ids.verification','employee_id', 'Verification'),
                'family_detail_ids':fields.one2many('ids.hr.family.detail','employee_id', 'Family Details'),
                'employement_detail_ids':fields.one2many('ids.hr.employment.detail','employee_id', 'Work Experience Information'),
                'reference_detail_ids':fields.one2many('ids.hr.reference.detail','employee_id', 'Reference Details'),
                'training_detail_ids':fields.one2many('ids.hr.training.detail','employee_id', 'Training Details'),
                'medical_detail_id':fields.many2one('ids.hr.medical.detail', 'Medical Details',help="Link this employee to it's medical details", ondelete="cascade", required=True),
                'vehicle_detail_ids':fields.one2many('ids.hr.vehicle.detail','employee_id', 'Vehicle Details'),                                
                'background_detail_id':fields.many2one('ids.hr.employee.background.detail', 'Background Details',help="Link this employee to it's background details", ondelete="cascade", required=True),
                'emergency_detail_ids':fields.one2many('ids.hr.emergency.detail','employee_id', 'Emergency Details'),
                'immigration_detail_ids':fields.one2many('ids.hr.immigration.detail','employee_id', 'Immigration Details'),
                'joining_date':fields.date('Joining Date', required=True),
                'confirmation_date':fields.date('Confirmation Date', required=True),
                'confirmation_status':fields.selection([('probation','On Probation'),('confirmed','Confirmed'),('extended','Extended')],'Confirmation Status', required=True),
                'working_status':fields.selection([('working','Working'),('on_resign','On Resign'),('resigned','Resigned'),('exit','Exit')], 'Status', required = True ),
                'current_address':fields.char("Current Address"),
                'current_city':fields.char("City"),
                'current_state':fields.many2one("res.country.state", 'State', ondelete='restrict'),
                'permanent_address':fields.char("Permanent Address"),
                'permanent_city': fields.char("City"),
                'permanent_state':fields.many2one("res.country.state", 'State', ondelete='restrict'),
                'country_id_cu': fields.many2one('res.country', "Country", ondelete='restrict'),
                'country_id_pe': fields.many2one('res.country', "Country", ondelete='restrict'),
                'father_name':fields.char('Father/Husband\'s Name', size=100),
                'weight':fields.char('Weight', size=100),
                'height':fields.char('Height', size=100),
                'role_category':fields.selection([('direct','Direct'),('indirect','Indirect')], 'Role Category'),
                'billing_category':fields.selection([('billable','Billable'),('nonbillable','Non Billable')], 'Billing Category'),
                'grade_id':fields.many2one('ids.employee.grade', 'Employee Grade'),
#                 'employment_type_id':fields.many2one('ids.employment.type', 'Employment Type', required=True),
                'employment_type_id':fields.selection([('trainee','Trainee'),('regular','Regular'),('contract','Contractual'),('stipend','Stipend'),('consultant','Consultant')],'Employment Type', required=True),
                'shift':fields.selection([('general','General'), ('morning','Morning'), ('evening','Evening'), ('night','Night')], 'Shift'),
                'service_agreement':fields.boolean('Service Agreement'),
                'agreement_start_date':fields.date('Start Date'),
                'agreement_end_date':fields.date('End Date'),
                'inv':fields.function(is_visible, type='boolean', method=True, store=False, string='Visibility'),
                'job_category':fields.selection([('S','Staff'), ('M','Management')], 'Job Category'),
                'shift_id':fields.many2one('employee.shift','Shift'),
                'end_date': fields.date('End Date'),
                'notice':fields.selection([('15','15'), ('30','30'),('45','45'), ('60','60'),('90','90')],'Notice Period (in days) ', required=True),
                'team_id': fields.many2one('hr.team', 'Team'),
                #####Added on 6 APR 2018
                'spouse_name':fields.char('Spouse name'),
                'pf_status':fields.selection([('Yes','Yes'),('No','No')], 'PF Status'),
                'pf_no':fields.char('PF No.'),
                'esi_status':fields.selection([('Yes','Yes'),('No','No')], 'ESI Status'),
                'esi_no':fields.char('ESI No.'),
                'gmi_status':fields.selection([('Yes','Yes'),('No','No')], 'GMI Status'),
                'gmi_no':fields.char('GMI No.'),
                'uan_no':fields.char('UAN No.'),
                'mrf_date':fields.date('MRF Date'),
                'loi_date':fields.date('LOI Date'),
                'current_pin':fields.char('Pin'),
                'curent_contact':fields.char('Contact No.'),
                'permanent_pin':fields.char('Pin'),
                'permanent_contact':fields.char('Contact No.'),
                'passport_issue_date':fields.date('Passport Issue Date'),
                'passport_expiry_date':fields.date('Passpoer Expiry Date'),


               }
        
    '''
    def create(self, cr, uid, vals, context=None):
        vals['emp_code']=self.pool.get('ir.sequence').get(cr, uid,'hr.employee')
        res=super(hr_employee, self).create(cr, uid, vals)
        return res
    '''    
        
    '''
    def write(self, cr, uid, ids, vals, context=None):
        c=self.browse(cr, uid, ids, context=context)
        work_phone=c.work_phone
        id=c.id
        if c.state not in ('draft','submitted','validated','refused'):
            self.pool.get('ids.emp.info.change').create(cr, uid, {'employee_id':c.id,'work_phone': work_phone,'state':'A'}, context=context)
            cr.execute("update hr_employee set state='draft' where id=%s"%(id))
        res=super(hr_employee, self).write(cr, uid, ids, vals)
        return res
        
    '''
    
    def name_get(self, cr, uid, ids, context=None):
        """Gets name of the employee with code as well """
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            name = record.name
            emp_code = record.emp_code
            if emp_code:
                name =  "[%s] %s" % (emp_code ,name)
            else:
                name =  "%s" % (name)
            res.append((record.id, name))
        return res
    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):
        """Search name through both code as well as name. """
        if not args:
            args = []
        if name:
            ids = self.search(cr, user, [('emp_code','=',name)]+ args, limit=limit, context=context)
            if not ids:
                ids = self.search(cr, user, [('name','=',name)]+ args, limit=limit, context=context)
                
            if not ids:
                # Do not merge the 2 next lines into one single search, SQL search performance would be abysmal
                # on a database with thousands of matching products, due to the huge merge+unique needed for the
                # OR operator (and given the fact that the 'name' lookup results come from the ir.translation table
                # Performing a quick memory merge of ids in Python will give much better performance
                ids = set()
                ids.update(self.search(cr, user, args + [('emp_code',operator,name)], limit=limit, context=context))
                if len(ids) < limit:
                    # we may underrun the limit because of dupes in the results, that's fine
                    ids.update(self.search(cr, user, args + [('name',operator,name)], limit=(limit-len(ids)), context=context))
                ids = list(ids)
#            if not ids:
#                ptrn = re.compile('(\[(.*?)\])')
#                res = ptrn.search(name)
#                if res:
#                    ids = self.search(cr, user, [('name','=', res.group(2))] + args, limit=limit, context=context)
        else:
            ids = self.search(cr, user, args, limit=limit, context=context)
        result = self.name_get(cr, user, ids, context=context)
        return result
    
    
    def _default_confirmation_date(self, cr, uid, context=None):        
            return (datetime.today() + relativedelta(months=6)).strftime(DEFAULT_SERVER_DATE_FORMAT)

    _defaults = {
        'confirmation_status': 'probation',
        'joining_date':fields.date.context_today,
        'confirmation_date': _default_confirmation_date,
        'notice': '60' ,
        'employment_type_id' : 'regular',
        
    }
    
    _sql_constraints = [('date_check','CHECK(agreement_start_date < agreement_end_date)','Agreement End Date should be greater than Start Date'),
                        ('confirm_date_check','CHECK(joining_date <= confirmation_date)','Confirmation Date should be greater than Joining Date'),
                        ('end_date_check','CHECK(joining_date < end_date)','End Date should be greater than Joining Date')]
    
    def generate_emp_code(self, cr,uid, ids, context=None):
        """Generates employee code of the employee according to the 
            Employment type of the Employee """
        if context == None:
            return False
        if not context.get('employment_type_id', False):
            return False
        
        employment_type_id = context.get('employment_type_id')
      #  emp_code_details = self.pool.get('employment_type_id')
        if employment_type_id == 'trainee':
            emp_code_val=self.pool.get('ir.sequence').get(cr, uid,'hr.trainee')
        elif employment_type_id == 'consultant':
            emp_code_val=self.pool.get('ir.sequence').get(cr, uid,'hr.consultant')
        elif employment_type_id== 'contract':
            emp_code_val=self.pool.get('ir.sequence').get(cr, uid,'hr.contractual')
        elif employment_type_id == 'stipend':
            emp_code_val=self.pool.get('ir.sequence').get(cr, uid,'hr.stipend')
        else:
            emp_code_val=self.pool.get('ir.sequence').get(cr, uid,'hr.employee')
        
        res=super(hr_employee, self).write(cr, uid, ids, {'emp_code':emp_code_val})
        
        
        emp_data=self.browse(cr, uid, ids, context=context)
        tech=self.pool.get('ids.business.information').search(cr,uid,[('employee_id','=',emp_data.id)])
        tech_data=self.pool.get('ids.business.information').browse(cr, uid, tech, context=context)
        url="http://ids-erp.idsil.loc:8069/web"
        if emp_data.parent_id:
            values = {
                'subject': 'New Employee Joining Information-(Employee Code Generated)',
                'body_html': 'Employee code of new employee has been generated successfully, please fill the Business Information.<br/>Detail of user is given as follows: <br/><br/>ECODE : '+ emp_data.emp_code +'<br/>NAME : '+ emp_data.name_related +'<br/>EMPLOYEE TYPE : '+ emp_data.employment_type_id +'<br/>DOJ : '+ emp_data.joining_date +'<br/>DIVISION : '+ emp_data.division.name +'<br/>DEPARTMENT : '+ emp_data.department_id.name +' <br/>REPORTING MANAGER : '+ emp_data.parent_id.name +'<br/><br/><br/>'+url,
                'email_to': tech_data.employee_id.parent_id.work_email,
                'email_cc': {tech_data.employee_id.parent_id.parent_id.work_email,tech_data.employee_id.division.hr_email, 'sandeep.singh@idsil.com'},
                'email_from': 'info.openerp@idsil.com',
          }
        else:
            values = {
                'subject': 'New Employee Joining Information-(Employee Code Generated)',
                'body_html': 'Employee code of new employee has been generated successfully, please fill the Business Information.<br/>Detail of user is given as follows: <br/><br/>ECODE : '+ emp_data.emp_code +'<br/>NAME : '+ emp_data.name_related +'<br/>EMPLOYEE TYPE : '+ emp_data.employment_type_id +'<br/>DOJ : '+ emp_data.joining_date +'<br/>DIVISION : '+ emp_data.division.name +'<br/>DEPARTMENT : '+ emp_data.department_id.name +' <br/>REPORTING MANAGER : N/A <br/><br/><br/>'+url,
                'email_to': tech_data.employee_id.parent_id.work_email,
                'email_cc': {tech_data.employee_id.parent_id.parent_id.work_email,tech_data.employee_id.division.hr_email, 'sandeep.singh@idsil.com'},
                'email_from': 'info.openerp@idsil.com',
          }
            
        #---------------------------------------------------------------
        mail_obj = self.pool.get('mail.mail') 
        msg_id = mail_obj.create(cr, uid, values, context=context) 
        if msg_id: 
            mail_obj.send(cr, uid, [msg_id], context=context) 
        
        
        
        return res   
#     def generate_emp_code(self, cr,uid, ids, context=None):
#         if context == None:
#             return False
#         if not context.get('employment_type_id', False):
#             return False
#         
#         employment_type_id = context.get('employment_type_id')
#         emp_code_details = self.pool.get('ids.employment.type').read(cr, uid, employment_type_id, ['name','emp_code_prefix'])
#         if emp_code_details['emp_code_prefix'] == 'TR':
#             emp_code_val=self.pool.get('ir.sequence').get(cr, uid,'hr.trainee')
#         elif emp_code_details['emp_code_prefix'] == 'CN':
#             emp_code_val=self.pool.get('ir.sequence').get(cr, uid,'hr.consultant')
#         elif emp_code_details['emp_code_prefix'] == 'CT':
#             emp_code_val=self.pool.get('ir.sequence').get(cr, uid,'hr.contractual')
#         elif emp_code_details['emp_code_prefix'] == 'S':
#             emp_code_val=self.pool.get('ir.sequence').get(cr, uid,'hr.stipend')
#         else:
#             emp_code_val=self.pool.get('ir.sequence').get(cr, uid,'hr.employee')
#         
#         res=super(hr_employee, self).write(cr, uid, ids, {'emp_code':emp_code_val})
#         
#         #allocate leaves to new_joinee
#         if res:
#             return self.pool.get('hr.holidays.status').allocate_holidays_new_joinee(cr, uid, emp_code_val, context=None)
#          
#         return res   
    
    def calculate_confirmation_date(self, cr, uid, ids, joining_date,context=None):       
        """Calculates the confirmation date with respect to joining date. """
        probation_period_months = 6        
        confirmation_date = (datetime.strptime(joining_date, DEFAULT_SERVER_DATE_FORMAT) + relativedelta(months=probation_period_months)).strftime(DEFAULT_SERVER_DATE_FORMAT)        
        return {'value':{'confirmation_date':confirmation_date}}
        #return {'value':{'confirmation_date':datetime.strftime(last_date,DEFAULT_SERVER_DATE_FORMAT)}}
    
    def check_confirmation_status(self, cr, uid, ids, confirmation_status,context=None):
        
        #allocate leaves on confirmation
        if confirmation_status == 'confirmed':     
            return self.pool.get('hr.holidays.status').allocate_holidays_on_confirmation(cr, uid, ids[0], context=None)
        
        return True   
    
    @api.multi
    def onchange_state(self, current_state):
        if current_state:
            state = self.env['res.country.state'].browse(current_state)
            return {'value': {'country_id_cu': state.country_id.id}}
        return {}
    
    @api.multi
    def onchange_state_perma(self, permanent_state):
        if permanent_state:
            statep = self.env['res.country.state'].browse(permanent_state)
            return {'value': {'country_id_pe': statep.country_id.id}}
        return {}
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'job_id' in vals:
            job_id=vals['job_id']
            data_search=self.pool.get('hr.contract').search(cr,uid,[('employee_id','=',ids)])
            data=self.pool.get('hr.contract').browse(cr, uid, data_search, context=None)
            if data:
                self.pool.get('hr.contract').write(cr, uid, data.id, {'job_id':vals['job_id']}, context=context)
        res = super(hr_employee, self).write(cr, uid, ids, vals, context=context)
        return res

       
    
class office_location(osv.osv):
    
    _name = 'office.location'
    _description = "Office Location"
    _columns= {
               'name': fields.char('Office Location'),
               'hr_manager_id':fields.many2one('hr.employee', 'HR manager'),
               'work_email':fields.char('Work Email'),
               } 
    
class division(osv.osv):
    
    _name = 'division'
    _description = "Division"
    _columns= {
               'name':fields.char('Division'),
               'hr_email':fields.char('Email(HR Manager)'),
               'company_id':fields.many2one('res.company','Company'),
               'manager_division_id': fields.many2one('hr.employee', 'Manager'),
               'division_hod_id': fields.many2one('hr.employee', 'HOD'),
               'hod_email':fields.char('Email(HOD)'),
               } 
          
class ids_hr_religion(osv.osv):
    
    _name = 'ids.hr.religion'
    _description = "Religion"    
    _columns = {
                'name':fields.char('Religion Name', size=30, required=True)
                }
    
class board_uni(osv.osv):
    
    _name = 'board.uni'
    _description = "Board/University"    
    _columns = {
                'name':fields.char('Board/University', required=True)
                }
    
class courses(osv.osv):
    
    _name = 'courses'
    _description = "Degree/Course"    
    _columns = {
                'name':fields.char('Degree/Course', required=True)
                }
        
    
class verification_type(osv.osv):
    
    _name = 'verification.type'
    _description = "Verification Type"    
    _columns = {
                'name':fields.char('Verification Type', required=True)
                }
    
class ids_employee_grade(osv.osv):
    
    _name = 'ids.employee.grade'
    _description = "Employee Grade"    
    _columns = {
                'name':fields.char('Employee Grade', size=30, required=True)
                }

class ids_employment_type(osv.osv):
    
    _name = 'ids.employment.type'
    _description = "Employment Type"    
    _columns = {
                'name':fields.char('Employment Type', size=30, required=True),
                'emp_code_prefix':fields.char('Employee Code Prefix', size=30)
                }
         
def _check_unique_insesitive(self, cr, uid, ids, context=None):
        list_ids = self.search(cr, uid , [], context=context)
        lst = [list_id.name.lower() for list_id in self.browse(cr, uid, list_ids, context=context) if list_id.name and list_id.id not in ids]
        for self_obj in self.browse(cr, uid, ids, context=context):
            if self_obj.name and self_obj.name.lower() in lst:
                return False
            return True
        
class ids_hr_language(osv.osv):
    
    _name = 'ids.hr.language'
    _description = "Language"    
    _columns = {
                'name':fields.char('Language Name', size=30, required=True)
                }
    _sql_constraints = [('name_unique','unique(name)','Language name already exists')]
    _constraints = [(_check_unique_insesitive, 'Language name already exists', ['name'])]
    
class ids_hr_education_detail(osv.osv):
    
    _name = 'ids.hr.education.detail'
    _description = "Employee Education Detail"    
    _columns = {                
                'name':fields.char('Degree/Course', size=100),
                'category':fields.selection([('matric','Matric'), ('senior_secondary','Senior Secondary'),('graduate','Graduate'),('post_graduate','Post Graduate'),('other','Other')], 'Category'),
                'course_id':fields.many2one('courses', 'Degree/Course'),
                'school':fields.char('School/College', size=1000),
                'board_id':fields.many2one('board.uni','Board/University'),
                'marks':fields.char('%Marks/CGPA', size=10),
                'year':fields.selection([(num, str(num)) for num in range((time.localtime().tm_year), 1950, -1)], 'Passing Year'),
                'regular':fields.selection([('regular','Regular'),('correspondence','Correspondence')], 'Regular/Correspondence'),
                'employee_id':fields.many2one('hr.employee', 'Employee')
                }
    
class ids_verification(osv.osv):
    
    _name = 'ids.verification'
    _description = "Employee Verification"    
    _columns = {                
                'name':fields.char('Verification', size=100),
                'verification_type':fields.many2one('verification.type','Type', required=True),
                'verification_description':fields.char('Description', size=1000, required=True),
                'remarks':fields.char('Remarks', size=100, required=True),
                'date_of_initate':fields.date('Date of Initiate', required=True),
                'date_of_receive':fields.date('Date of Receiving', required=True),
                'employee_id':fields.many2one('hr.employee', 'Employee')
                }
    
    _sql_constraints = [('date_check','CHECK(date_of_initate < date_of_receive)','Date of Receiving should be greater than Date of Initiate'),
                        ]
    
    
class ids_hr_family_detail(osv.osv):
    
    _name = 'ids.hr.family.detail'
    _description = "Employee Family Detail"        
    _columns = {
                'name':fields.char('Name', size=100, required=True),
                'relation':fields.char('Relation', size=100, required=True),
                'qualification':fields.char('Education Qualification', size=100),
                'occupation':fields.char('Occupation', size=200),
                'dob': fields.date("Date of Birth", required=True),
                'age':fields.integer('Age (in years)', size=3),
                'contact':fields.char('Contact Info/Tel.No./Address', size=64),
                'employee_id':fields.many2one('hr.employee', 'Employee')
                }
    
    def calculate_age(self, cr, uid, ids,dob,context=None):       
        """Calculate age of the family member from date of birth provided """
        age={}
        if dob:
            age = (datetime.now()-datetime.strptime(dob,DEFAULT_SERVER_DATE_FORMAT)).days/365    
        
        return {'value':{'age':age}}
        
class ids_hr_employment_detail(osv.osv):
    
    _name = 'ids.hr.employment.detail'
    _description = "Employee Employment Detail"        
    _columns = {
                'name':fields.char('Company', size=100),
                'employement_type':fields.selection([('present','Present'),('past','Past')], 'Present/Past Employement', required=True),
                'joining_date':fields.date('Joining Date'),
                'leaving_date':fields.date('Leaving Date'),
                'industry':fields.many2one('ids.hr.industry.type','Industry Type'),
                'address':fields.char('Company Address', size=200),
                'position':fields.char('Position', size=100),
                'salary':fields.char('TCTC Salary', size=50),
                'supervisor_designation':fields.char('Designation of immediate Supervisor', size=100),
                'kras':fields.text('KRAs'),
                'leaving_reason':fields.char('Reason For Leaving', size=200),
                'employee_id':fields.many2one('hr.employee', 'Employee', invisible=True)
                }
    
class ids_hr_reference_detail(osv.osv):
    
    _name = 'ids.hr.reference.detail'
    _description = "Reference"            
    _columns = {
                'name':fields.char('Name of Reference', size=100, required=True),
                'official_address':fields.char('Official Address', size=200),
                'designation':fields.char('Designation', size=200, required=True),
                'contact':fields.char('Tel. No. / Mob. No.', size=64, required=True),
                'email':fields.char('Email Id', size=50),
                'employee_id':fields.many2one('hr.employee', 'Employee')
                }

class ids_hr_training_detail(osv.osv):
    
    _name = 'ids.hr.training.detail'
    _description = "Employee Training Detail"            
    _columns = {
                'name':fields.char('Training Name', size=100, required=True),
                'duration':fields.char('Duration', size=50, required=True),
                'faculty':fields.char('Faculty', size=100, required=True),
                'topics':fields.text('Topics Covered',required=True),
                'employee_id':fields.many2one('hr.employee', 'Employee')
                }
    
class ids_hr_vehicle_detail(osv.osv):
    
    _name = 'ids.hr.vehicle.detail'
    _description = "Employee Vehicle Detail"        
    VEHICLE_TYPES = [('two_wheeler','Two Wheeler'),('four_wheeler','Four wheeler')]
        
    _columns = {
                'vehicle_type':fields.selection(VEHICLE_TYPES, 'Vehicle Type',required=True),
                'vehicle_no':fields.char('Vehicle Number', size=50, required=True),
                'make_year':fields.selection([(num, str(num)) for num in range((time.localtime().tm_year), 1950, -1)], 'Year of Make', required=True),
                'vehicle_desc':fields.text('Vehicle Desc/Body Type'),
                'employee_id':fields.many2one('hr.employee', 'Employee')
                }
    _res_name = 'vehicle_number'    

class ids_hr_emergency_detail(osv.osv):
    
    _name = 'ids.hr.emergency.detail'
    _description = "Employee Emergency Contact"           
    _columns = {
                'name':fields.char('Name', size=100, required=True),
                'relation':fields.char('Relation', size=100, required=True),
                'phone':fields.char('Phone', size=64),
                'mobile':fields.char('Mobile', size=64),
                'emergency_address':fields.char("Address"),
 				'emerg_pin':fields.char('Pin'),
                'employee_id':fields.many2one('hr.employee', 'Employee')
                }
    
class ids_hr_industry_type(osv.osv):
    
    _name = 'ids.hr.industry.type'
    _description = "Industry Type"           
    _columns = {
                'name':fields.char('Name', size=200, required=True)
                }
    
class ids_hr_immigration_detail(osv.osv):
    
    _name = 'ids.hr.immigration.detail'
    _description = "Employee Immigration Details"           
    _columns = {
                'name':fields.selection([('passport','Passport'),('visa','Visa')],'Document Type', required=True),
                'doc_number':fields.char('Document Number', size=100, required=True),
                'country_id': fields.many2one('res.country', 'Issued By(Country)', required=True),
                'issue_date':fields.date('Issue Date', required=True),
                'expiry_date': fields.date('Expiry Date', required=True),
                'employee_id':fields.many2one('hr.employee', 'Employee')
                }
    _sql_constraints = [('date_check','CHECK(issue_date < expiry_date)','Expiry Date should be greater than Issue Date.'),
                        ('document_unique','unique(doc_number)','Document number should be unique')]  
    
    
    
class res_users(osv.osv):
    _inherit = 'res.users'
    _columns = {
                'division_id':fields.many2one('division','Division'),
                'location_id':fields.many2one('office.location','Location'),
                'division_ids':fields.many2many('division', 'division_rel', 'user_id','division','Divisions'),
                'location_ids':fields.many2many('office.location', 'location_rel', 'user_id','office_location','Office Location'),
                'group_id':fields.many2one('employee.group','Group'),
                } 
    def create(self, cr, uid, vals, context=None):
        user_id = super(res_users, self).create(cr, uid, vals, context=context)
        user = self.browse(cr, uid, user_id, context=context)
        if user.partner_id.company_id: 
            user.partner_id.write({'company_id': user.company_id.id})
        if not user.partner_id.email:
            user.partner_id.write({'email':'info.openerp@idsil.com','ref':user.name})
        return user_id
    
    def name_get(self, cr, uid, ids, context=None):
        """Gets name of the user with login as well """
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            name = record.name
            login = record.login
            if login:
                name =  "[%s] %s" % (login ,name)
            else:
                name =  "%s" % (name)
            res.append((record.id, name))
        return res
    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):
        """Search name through both code as well as name. """
        if not args:
            args = []
        if name:
            ids = self.search(cr, user, [('login','=',name)]+ args, limit=limit, context=context)
            if not ids:
                ids = self.search(cr, user, [('login','=',name)]+ args, limit=limit, context=context)
                
            if not ids:
                # Do not merge the 2 next lines into one single search, SQL search performance would be abysmal
                # on a database with thousands of matching products, due to the huge merge+unique needed for the
                # OR operator (and given the fact that the 'name' lookup results come from the ir.translation table
                # Performing a quick memory merge of ids in Python will give much better performance
                ids = set()
                ids.update(self.search(cr, user, args + [('login',operator,name)], limit=limit, context=context))
                if len(ids) < limit:
                    # we may underrun the limit because of dupes in the results, that's fine
                    ids.update(self.search(cr, user, args + [('name',operator,name)], limit=(limit-len(ids)), context=context))
                ids = list(ids)
#            if not ids:
#                ptrn = re.compile('(\[(.*?)\])')
#                res = ptrn.search(name)
#                if res:
#                    ids = self.search(cr, user, [('name','=', res.group(2))] + args, limit=limit, context=context)
        else:
            ids = self.search(cr, user, args, limit=limit, context=context)
        result = self.name_get(cr, user, ids, context=context)
        return result
res_users() 

class hr_team(osv.osv):

    def _team_name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)

    _name = "hr.team"
    _columns = {
        'name': fields.char('Team Name', required=True),
        'complete_name': fields.function(_team_name_get_fnc, type="char", string='Name'),
        'company_id': fields.many2one('res.company', 'Company', select=True, required=False),
        'department_id':fields.many2one('hr.department','Department'),
        'parent_id': fields.many2one('hr.team', 'Parent Team', select=True),
        'child_ids': fields.one2many('hr.team', 'parent_id', 'Child team'),
        'member_ids': fields.one2many('hr.employee', 'team_id', 'Members', readonly=True),
        'note': fields.text('Note'),
    }

    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'hr.team', context=c),
    }

    def _check_recursion(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        level = 100
        while len(ids):
            cr.execute('select distinct parent_id from hr_team where id IN %s',(tuple(ids),))
            ids = filter(None, map(lambda x:x[0], cr.fetchall()))
            if not level:
                return False
            level -= 1
        return True

    _constraints = [
        (_check_recursion, 'Error! You cannot create recursive team.', ['parent_id'])
    ]

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        if isinstance(ids, (int, long)):
            ids = [ids]
        reads = self.read(cr, uid, ids, ['name','parent_id'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['parent_id']:
                name = record['parent_id'][1]+' / '+name
            res.append((record['id'], name))
        return res
    
class hr_department(osv.osv):
    _inherit = 'hr.department'
    _columns = {
                'division_id':fields.many2one('division','Division'),
                'working_schedule':fields.selection([('5','5 Days'),('6','6 Days')],'Working Schedule'),
                'use_duty_roster':fields.boolean('Use Shift Rosters'),
                'half_day_applicable':fields.selection([('6','6 Hours'),('7','7 Hours')],'Half day applicable before'),
                'location_id': fields.many2one('office.location', 'Location')
                }
    
    def create(self, cr, uid, values, context=None):
        
        data_search=self.search(cr,uid,[('name','=',values['name']),('division_id','=',values['division_id']),('location_id','=',values['location_id'])])
        if data_search:
            raise osv.except_osv(_('Warning'), _('Department record already exists! Please update the existing record.'))
        id = super(hr_department, self).create(cr, uid, values, context)
        return id
    
class change_password_wizard_new(osv.TransientModel):
    """
        A wizard to manage the change of users' passwords
    """

    _name = "change.password.wizard.new"
    _description = "Change Password Wizard New"
    _columns = {
        'user_id': fields.many2one('res.users', string='User', required=True),
        'login': fields.char('Login'),
        'new_passwd': fields.char('New Password'),

    }
    
    _defaults = {
        'new_passwd': '',
    }
    def onchange_user_id(self, cr, uid, ids, login, user_id, context=None):
        user_id=self.pool.get('res.users').browse(cr, uid, user_id, context=context)
        login=user_id.login
        res= {'value': {'login': login}}
        return res

    def change_password_button_new(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids, context=context):
            line.user_id.write({'password': line.new_passwd})
#             psw=line.new_passwd
#             user=line.user_id
#             cr.execute("update res_users set password=%s where user_id=%s",(psw,user));
        # don't keep temporary passwords in the database longer than necessary
        self.write(cr, uid, ids, {'new_passwd': False}, context=context)

