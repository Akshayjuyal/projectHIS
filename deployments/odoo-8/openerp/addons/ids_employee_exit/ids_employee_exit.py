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

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp import netsvc
from openerp.osv import fields, osv
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools.translate import _
from openerp import SUPERUSER_ID

    
class ids_employee_exit(osv.Model):
    
    _name = 'ids.employee.exit'
    _description = 'Employee Full &amp; Final'
    _inherit = ['mail.thread', 'ir.needaction_mixin'] 
       
    _columns = {
        'fnf_number':fields.char('F&F Number', size=15, readonly=True),
        'employee_id': fields.many2one('hr.employee', 'Employee Name', required=True, domain="['|',('working_status', '=', 'resigned'),('working_status', '=', 'exit')]"),
        'job_id': fields.related('employee_id', 'job_id', type='many2one', relation='hr.job', string='Job Position', store=True, readonly=True),  
        'department_id': fields.related('employee_id', 'department_id', type='many2one', relation='hr.department', string='Department', store=True, readonly=True),
        'joining_date': fields.related('employee_id', 'joining_date', type='date', relation='hr.employee', string='Joining Date', store=True, readonly=True),
        'confirmation_status': fields.related('employee_id', 'confirmation_status', type='char', relation='hr.employee', string='Employee status', store=True, readonly=True),
        'resign_id': fields.many2one('ids.hr.employee.separation', 'Resign ID'),
        'nodues_id': fields.many2one('emp.no.dues','No Dues ID'),
        'capture_date': fields.related('resign_id', 'capture_date', type='date', relation='ids.hr.employee.separation', string='Resignation Date ', store=True),
        'last_date': fields.related('resign_id', 'last_date', type='date', relation='ids.hr.employee.separation', string='Last Working Day', store=True),
        'dob':fields.related('employee_id','birthday',type='char',relation='hr.employee',string='Date Of Birth', store=True, readonly=True),
        'division_id':fields.related('employee_id','division',type='many2one',relation='division',string='Division', store=True, readonly=True),
        'location_id':fields.related('employee_id','office_location',type='many2one',relation='office.location',string='Location', store=True, readonly=True),
        'gender':fields.related('employee_id','gender',type='char',relation='hr.employee',string='Gender', store=True, readonly=True),
        'mobile_no':fields.related('employee_id','mobile_phone',type='char',relation='hr.employee',string='Mobile No', store=True, readonly=True),
        'state': fields.selection([('draft', 'Draft'),('phase1', 'Phase-1'),
                                           ('phase2', 'Phase-2'),
                                           ('phase3', 'Phase-3'),
                                           ('completed', 'Completed')
                                           ], 'Status', readonly=True),
        
        #Leave Details Columns
        'leave_detail_ids':fields.one2many('ids.employee.ff.leave','fullfinal_id', 'Leave Details', readonly=True, store=True, ondelete="cascade"),
        #Notice Period Details Columns
        'np_required':fields.selection([('yes', 'Yes'),
                                           ('no', 'No'),('na', 'N/A')], 'Notice Period Required', required=True),
        'reason_no':fields.text('Reason For No'),
        'shortfall':fields.float('Shortfall in Notice Period(Days)'),
        'shortfall_reason':fields.text('Reasons for shortfall'),
        #Gratuity Details Columns
        'last_wages':fields.float('Amount of wages last claimed'),
        'service_period':fields.char('Total period of service'),
        'eligibility':fields.selection([('yes', 'Yes'),
                                           ('no', 'No')], 'Eligibility', required=True),
        'gratuity_years':fields.integer('Gratuity Years'),
        'amount_claimed':fields.float('Amount of gratuity claimed'),
        #Agreement Details Columns
        'service_agreement':fields.selection([('yes', 'Yes'),
                                           ('no', 'No')], 'Service Agreement', required=True),
        'start_date':fields.date('Start Date'),
        'end_date':fields.date('End Date'),
        'recoverable_applicable':fields.selection([('yes', 'Yes'),
                                           ('no', 'No')], 'Recoverable Applicable', required=True),
        'amount':fields.float('Amount'),
        'valid_date':fields.date('Valid Date'),
        #Attendance Details Columns
        'last_month_days':fields.float('25th to 30th/31th of previous month(Days)'),
        'cur_month_days':fields.float('1st till last working day(Days)'),
        #Bonus Information Columns
        'bonus':fields.selection([('yes', 'Yes'),
                                           ('no', 'No')], 'Bonus', required=True),
        'bonus_amount':fields.float('Amount'),
        'lta':fields.selection([('yes', 'Yes'),
                                           ('no', 'No')], 'LTA', required=True),
        'lta_amount':fields.float('Amount'),
        'loyalty':fields.selection([('yes', 'Yes'),
                                           ('no', 'No')], 'Loyalty', required=True),
        'loyalty_amount':fields.float('Amount'),
        #Allowance Details Columns
        'night_allow':fields.float('Night Allowance'),
        'night_month':fields.selection([('1', 'January'),
                                           ('2', 'February'),('3', 'March'),('4', 'April'),('5', 'May'),('6', 'June'),
                                           ('7', 'July'),('8', 'August'),('9', 'September'),('10', 'October'),('11', 'November'),
                                           ('12', 'December')], 'Month'),
        'ot_allow':fields.float('Overtime Allowance'),
        'ot_month':fields.selection([('1', 'January'),
                                           ('2', 'February'),('3', 'March'),('4', 'April'),('5', 'May'),('6', 'June'),
                                           ('7', 'July'),('8', 'August'),('9', 'September'),('10', 'October'),('11', 'November'),
                                           ('12', 'December')], 'Month'),
        'attendance_allow':fields.float('Attendance Allowance'),
        'attendance_month':fields.selection([('1', 'January'),
                                           ('2', 'February'),('3', 'March'),('4', 'April'),('5', 'May'),('6', 'June'),
                                           ('7', 'July'),('8', 'August'),('9', 'September'),('10', 'October'),('11', 'November'),
                                           ('12', 'December')], 'Month'),
        'prod_incentive':fields.float('Production Incentive'),
        'incentive_month':fields.selection([('1', 'January'),
                                           ('2', 'February'),('3', 'March'),('4', 'April'),('5', 'May'),('6', 'June'),
                                           ('7', 'July'),('8', 'August'),('9', 'September'),('10', 'October'),('11', 'November'),
                                           ('12', 'December')], 'Month'),
        #No Dues Details Columns(Facility)
        'icard_return':fields.selection([('yes', 'Yes'),
                                           ('no', 'No'),('na', 'N/A')], 'I-Card Return', required=True),
        'access_card_return':fields.selection([('yes', 'Yes'),
                                           ('no', 'No'),('na', 'N/A')], 'Access Card Return', required=True),
        'keys_return':fields.selection([('yes', 'Yes'),
                                           ('no', 'No'),('na', 'N/A')], 'Keys Return', required=True),
        'headphone_return':fields.selection([('yes', 'Yes'),
                                           ('no', 'No'),('na', 'N/A')], 'Head Phone Return', required=True),
        'name_delete':fields.selection([('yes', 'Yes'),
                                           ('no', 'No'),('na', 'N/A')], 'Name delete from attendance Registers', required=True),
        'canteen_dues':fields.selection([('yes', 'Yes'),
                                           ('no', 'No'),('na', 'N/A')], 'Canteen dues Cleared', required=True),
        'library_book':fields.selection([('yes', 'Yes'),
                                           ('no', 'No'),('na', 'N/A')], 'Library Books Return', required=True),
        'remarks':fields.char('Remarks'),
        'submitted_by_facility':fields.many2one('res.users','Submitted By'),
        'submitted_on_facility':fields.datetime('Submitted On'),
        
        #No Dues Details Columns(Operation)
        'email_control':fields.char('Email Control'),
        'email_remarks':fields.char('Remarks'),
        'internet_control':fields.char('Internet Control'),
        'internet_remarks':fields.char('Remarks'),
        'remote_control':fields.char('Remote Control'),
        'remote_remarks':fields.char('Remarks'),
        'software_requirement':fields.char('Software Requirement'),
        'software_remarks':fields.char('Remarks'),
        'application_share':fields.char('Application Share Access'),
        'application_remarks':fields.char('Remarks'),
        'data_backup':fields.char('Databack-up Details'),
        'data_backup_remarks':fields.char('Remarks'),
        'handover_takeover':fields.selection([('yes', 'Yes'),
                                           ('no', 'No'),('na', 'N/A')], 'Handover Takeover Done', required=True),
        'handover_remarks':fields.char('Remarks(if any items not return)'),
        'submitted_by_operation':fields.many2one('res.users','Submitted By'),
        'submitted_on_operation':fields.datetime('Submitted On'),
        
        #No Dues Details Columns(Technical)
        'login_name_tech':fields.char('Login Name'),
        'login_name_disable':fields.selection([('yes', 'Yes'),
                                           ('no', 'No'),('na', 'N/A')], 'Disable'),
        'login_remarks_tech':fields.char('User-Name Remarks'),
        'allocation_it_asset':fields.selection([('yes', 'Yes'),
                                           ('no', 'No'),('na', 'N/A')], 'Allocation of IT Assets'),
        'it_assets_disable':fields.selection([('yes', 'Yes'),
                                           ('no', 'No'),('na', 'N/A')], 'Disable'),
        'asset_remarks_tech':fields.char('Asset Remarks'),
        'email_id_tech':fields.selection([('yes', 'Yes'),
                                           ('no', 'No'),('na', 'N/A')], 'Email ID Created'),
        'email_id_disable':fields.selection([('yes', 'Yes'),
                                           ('no', 'No'),('na', 'N/A')], 'Disable'),
        'email_remarks_tech':fields.char('Email Remarks'),
        'internet_control_tech':fields.selection([('yes', 'Yes'),
                                           ('no', 'No'),('na', 'N/A')], 'Internet Access Control'),
        'internal_disable':fields.selection([('yes', 'Yes'),
                                           ('no', 'No'),('na', 'N/A')], 'Disable'),
        'internet_remarks_tech':fields.char('Internet Remarks'),
        'backup_setup_tech':fields.selection([('yes', 'Yes'),
                                           ('no', 'No'),('na', 'N/A')], 'Back-Up Setup'),
        'backup_setup_disable':fields.selection([('yes', 'Yes'),
                                           ('no', 'No'),('na', 'N/A')], 'Disable'),
        'backup_remarks_tech':fields.char('Back-up Remarks'),
        'software_requirement_tech':fields.selection([('yes', 'Yes'),
                                           ('no', 'No'),('na', 'N/A')], 'Software Provisioning and Access Control'),
        'software_disable':fields.selection([('yes', 'Yes'),
                                           ('no', 'No'),('na', 'N/A')], 'Disable'),
        'software_remarks_tech':fields.char('Software Provisioning Remarks'),
        'application_share_tech':fields.selection([('yes', 'Yes'),
                                           ('no', 'No'),('na', 'N/A')], 'Application Share Access'),
        'appliaction_share_disable':fields.selection([('yes', 'Yes'),
                                           ('no', 'No'),('na', 'N/A')], 'Disable'),
        'application_remarks_tech':fields.char('Share Access Remarks'),
        'submitted_by_technical':fields.many2one('res.users','Submitted By'),
        'submitted_on_technical':fields.datetime('Submitted On'),
        
        # Remarks Column
        'group_hr_remarks':fields.text('Group HR Remarks'),
        'group_head_remarks':fields.text('Group Head Remarks'),
        'corp_hr_remarks':fields.text('Corp HR Remarks'),
        'hr_head_remarks':fields.text('HR Head Remarks'),
        'image_sign': fields.binary("Sign",
            help="This field holds the image used as sign, limited to 1024x1024px."),
        
        
    }
    _rec_name = 'fnf_number'
    
    _defaults = {
        'state': 'draft',
        'capture_date':fields.date.context_today,
    }
    
   
    def create(self, cr, uid, vals, context=None):
        """Create the unique id """
        vals['fnf_number']=self.pool.get('ir.sequence').get(cr, uid,'ids.employee.exit')
        res=super(ids_employee_exit, self).create(cr, uid, vals)
        return res
    
    def unlink(self, cr, uid, ids, context=None):        
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.state not in ['draft']:
                raise osv.except_osv(_('Warning!'),_('You cannot delete a full and final entry which is not in draft state.'))
        return super(ids_employee_exit, self).unlink(cr, uid, ids, context)    
    
    def submit_draft(self, cr, uid, ids, context=None):   
        """Draft Submit. """ 
        return self.write(cr, uid, ids, {'state':'phase1'})
    
    def submit_phase1(self, cr, uid, ids, context=None):   
        """PHASE-1 Submit. """ 
        return self.write(cr, uid, ids, {'state':'phase2'})
    
    def cancel_phase1(self, cr, uid, ids, context=None):   
        """PHASE-1 Cancel. """ 
        return self.write(cr, uid, ids, {'state':'draft'})
    
    def submit_phase2(self, cr, uid, ids, context=None):   
        """PHASE-2 Submit. """ 
        return self.write(cr, uid, ids, {'state':'phase3'})
    
    def submit_phase3(self, cr, uid, ids, context=None):   
        """PHASE-3 Submit. """ 
        return self.write(cr, uid, ids, {'state':'completed'})
    
    def cancel_phase3(self, cr, uid, ids, context=None):   
        """PHASE-3 Cancel. """ 
        return self.write(cr, uid, ids, {'state':'phase2'})
    
    def _calculate_years_between_two_dates(self, cr, uid, ids, start_date, end_date,context=None):              
        d1 = datetime.strptime(start_date, DEFAULT_SERVER_DATE_FORMAT).date()
        d2 = datetime.strptime(end_date, DEFAULT_SERVER_DATE_FORMAT).date()
        r = relativedelta(d2,d1)
        year = str(r.years)
        month = str(r.months)
        day = str(r.days)
        service_period = year + ' years,'+ month + ' month,'+ day + ' days'
        gt_years = r.years
        if r.months>5:
            gt_years = r.years+1
        return service_period,gt_years
    
    def onchange_last_wages(self, cr, uid, ids, last_wages, eligibility, gratuity_years, context=None):
        res = {'value': {'amount_claimed': False}}
        if eligibility == 'yes':
            res['value']['amount_claimed'] = (gratuity_years*last_wages*15)/26
        else:
            res['value']['amount_claimed'] = 0
        return res
    
    def calculate_shortfall(self, cr, uid, ids, employee_id, np_required, capture_date, last_date, context=None):
        shortfall = 0     
        if np_required=='yes':
            notice_period_days=0
            if employee_id:
                employee = self.pool.get('hr.employee').browse(cr, uid,employee_id)     
                notice_period_days = int(employee.notice)
            last = datetime.strptime(capture_date, "%Y-%m-%d")+timedelta(days=notice_period_days)
            shortfall = (last-datetime.strptime(last_date, "%Y-%m-%d")).days
        return {'value':{'shortfall':shortfall}}
    
            
    def onchange_employee(self, cr, uid, ids, employee_id, context=None):
        res = {'value': {
                         'job_id': False, 
                         'department_id':False, 
                         'joining_date':False, 
                         'confirmation_status':False, 
                         'resign_id':False, 
                         'capture_date':False, 
                         'last_date':False,
                         'nodues_id':False, 
                         
                         }
               }
        
        joining_date = ''
        last_date = ''
        
        if employee_id:
            exit_ids = self.search(cr, uid, [('employee_id', '=', employee_id)], context=context)
            if len(exit_ids) > 0:
                raise osv.except_osv(_('Warning!'),
                                     _('Full & Final has already been in progress/done for this employee.'))
            
            ee = self.pool.get('hr.employee').browse(cr, uid, employee_id, context=context)
            if ee:
                notice_period_days = int(ee.notice)
                if notice_period_days>0:
                    res['value']['np_required'] = 'yes'
                res['value']['job_id'] = ee.job_id.id
                res['value']['department_id'] = ee.department_id.id
                res['value']['dob'] = ee.birthday
                res['value']['division_id'] = ee.division.id
                res['value']['location_id'] = ee.office_location.id
                res['value']['gender'] = ee.gender
                res['value']['mobile_no'] = ee.mobile_phone
                joining_date = res['value']['joining_date'] = ee.joining_date
                res['value']['confirmation_status'] = ee.confirmation_status.title()
                emp_ff_leave_obj = self.pool.get('ids.employee.ff.leave')
                leave_ids = emp_ff_leave_obj._get_leave_details(cr, uid, ids, employee_id, context=None)
                res['value']['leave_detail_ids'] = leave_ids
                if ee.service_agreement == True:
                    res['value']['service_agreement'] = 'yes'
                    res['value']['start_date'] = ee.agreement_start_date
                    res['value']['end_date'] = ee.agreement_end_date
                else:
                    res['value']['service_agreement'] = 'no'
            
            emp_sep_id = self.pool.get('ids.hr.employee.separation').search(cr, uid , [('employee_id','=',employee_id),('state','=','done')], context=context)
            if emp_sep_id:
                es = self.pool.get('ids.hr.employee.separation').browse(cr, uid, emp_sep_id[0], context=context)
                if es:                
                    res['value']['resign_id'] = es.id
                    res['value']['capture_date'] = es.capture_date
                    last_date = res['value']['last_date'] = es.last_date
            emp_contract = self.pool.get('hr.contract').search(cr, uid , [('employee_id','=',employee_id)], context=context)
            if emp_contract:
                ec = self.pool.get('hr.contract').browse(cr, uid, emp_contract[0], context=context)
                if ec:                
                    res['value']['last_wages'] = ec.basic
            
            emp_nodues_id = self.pool.get('emp.no.dues').search(cr, uid , [('employee_id','=',employee_id)], context=context)
            if emp_nodues_id:
                en = self.pool.get('emp.no.dues').browse(cr, uid, emp_nodues_id[0], context=context)
                if en:                
                    res['value']['nodues_id'] = en.id
                    res['value']['icard_return'] = en.icard_return
                    res['value']['access_card_return'] = en.access_card_return
                    res['value']['keys_return'] = en.keys_return
                    res['value']['headphone_return'] = en.headphone_return
                    res['value']['name_delete'] = en.name_delete
                    res['value']['canteen_dues'] = en.canteen_dues
                    res['value']['library_book'] = en.library_book
                    res['value']['remarks'] = en.remarks
                    res['value']['submitted_by_facility'] = en.submitted_by_facility
                    res['value']['submitted_on_facility'] = en.submitted_on_facility
                    
                    res['value']['email_control'] = en.email_control
                    res['value']['email_remarks'] = en.email_remarks
                    res['value']['internet_control'] = en.internet_control
                    res['value']['internet_remarks'] = en.internet_remarks
                    res['value']['remote_control'] = en.remote_control
                    res['value']['remote_remarks'] = en.remote_remarks
                    res['value']['software_requirement'] = en.software_requirement
                    res['value']['software_remarks'] = en.software_remarks
                    res['value']['application_share'] = en.application_share
                    res['value']['application_remarks'] = en.application_remarks
                    res['value']['data_backup'] = en.data_backup
                    res['value']['data_backup_remarks'] = en.data_backup_remarks
                    res['value']['handover_takeover'] = en.handover_takeover
                    res['value']['handover_remarks'] = en.handover_remarks
                    res['value']['submitted_by_operation'] = en.submitted_by_operation
                    res['value']['submitted_on_operation'] = en.submitted_on_operation
                    
                    res['value']['login_name_tech'] = en.login_name_tech
                    res['value']['login_name_disable'] = en.login_name_disable
                    res['value']['login_remarks_tech'] = en.login_remarks_tech
                    res['value']['allocation_it_asset'] = en.allocation_it_asset
                    res['value']['it_assets_disable'] = en.it_assets_disable
                    res['value']['asset_remarks_tech'] = en.asset_remarks_tech
                    res['value']['email_id_tech'] = en.email_id_tech
                    res['value']['email_id_disable'] = en.email_id_disable
                    res['value']['email_remarks_tech'] = en.email_remarks_tech
                    res['value']['internet_control_tech'] = en.internet_control_tech
                    res['value']['internal_disable'] = en.internal_disable
                    res['value']['internet_remarks_tech'] = en.internet_remarks_tech
                    res['value']['backup_setup_tech'] = en.backup_setup_tech
                    res['value']['backup_setup_disable'] = en.backup_setup_disable
                    res['value']['backup_remarks_tech'] = en.backup_remarks_tech
                    res['value']['software_requirement_tech'] = en.software_requirement_tech
                    res['value']['software_disable'] = en.software_disable
                    res['value']['software_remarks_tech'] = en.software_remarks_tech
                    res['value']['application_share_tech'] = en.application_share_tech
                    res['value']['appliaction_share_disable'] = en.appliaction_share_disable
                    res['value']['application_remarks_tech'] = en.application_remarks_tech
                    res['value']['submitted_by_technical'] = en.submitted_by_technical
                    res['value']['submitted_on_technical'] = en.submitted_on_technical
            
            if (joining_date and last_date):
                res['value']['gratuity_years'] = self._calculate_years_between_two_dates(cr, uid, ids, joining_date, last_date, context=None)[1]
                res['value']['service_period'] = self._calculate_years_between_two_dates(cr, uid, ids, joining_date, last_date, context=None)[0]
        return res
        
    
    
class ids_employee_ff_leave(osv.Model):
    _name = 'ids.employee.ff.leave'
    _description = 'Employee FF Leave Details'
    
    def _get_leave_details(self, cr, uid, ids, employee_id, context=None):
        hr_holiday_status_obj = self.pool.get('hr.holidays.status')
        leave_type_ids = hr_holiday_status_obj.search(cr, uid , [('active','=',True)], context=context)
        records = hr_holiday_status_obj.get_days(cr, uid, leave_type_ids, employee_id, context=None)               
        
        leave_ids = []       
        for record in records:
            if record:
                leave_ids.append([0,0, {'holiday_status_id':record,'max_leaves':records[record]['max_leaves'],'leaves_taken':records[record]['leaves_taken'],'remaining_leaves':records[record]['remaining_leaves']}])             
                         
        return leave_ids 
    
    _columns = {
        'holiday_status_id':fields.many2one('hr.holidays.status', 'Leave Type', readonly=True),        
        'max_leaves': fields.float('Maximum Allowed'),
        'leaves_taken': fields.float('Leaves Already Taken'),
        'remaining_leaves': fields.float('Remaining Leaves'),                
        'employee_id':fields.many2one('hr.employee', 'Employee'),
        'fullfinal_id':fields.many2one('ids.employee.exit', 'Full and Final')       
    }
    
class emp_no_dues(osv.Model):
    _name = 'emp.no.dues'
    _description = 'Employee No Dues Details'

    _columns = {
        'nodues_number':fields.char('No Dues Number', size=15, readonly=True),        
        'employee_id': fields.many2one('hr.employee', 'Employee Name', required=True, domain="['|',('working_status', '=', 'resigned'),('working_status', '=', 'exit')]"),
        'job_id': fields.related('employee_id', 'job_id', type='many2one', relation='hr.job', string='Job Position', store=True, readonly=True),  
        'department_id': fields.related('employee_id', 'department_id', type='many2one', relation='hr.department', string='Department', store=True, readonly=True),
        'joining_date': fields.related('employee_id', 'joining_date', type='date', relation='hr.employee', string='Joining Date', store=True, readonly=True),
        'confirmation_status': fields.related('employee_id', 'confirmation_status', type='char', relation='hr.employee', string='Employee status', store=True, readonly=True),
        'resign_id': fields.many2one('ids.hr.employee.separation', 'Resign ID'),
        'capture_date': fields.related('resign_id', 'capture_date', type='date', relation='ids.hr.employee.separation', string='Resignation Date ', store=True),
        'last_date': fields.related('resign_id', 'last_date', type='date', relation='ids.hr.employee.separation', string='Last Working Day', store=True),
        'dob':fields.related('employee_id','birthday',type='char',relation='hr.employee',string='Date Of Birth', store=True, readonly=True),
        'division_id':fields.related('employee_id','division',type='many2one',relation='division',string='Division', store=True, readonly=True),
        'location_id':fields.related('employee_id','office_location',type='many2one',relation='office.location',string='Location', store=True, readonly=True),
        'gender':fields.related('employee_id','gender',type='char',relation='hr.employee',string='Gender', store=True, readonly=True),
        'mobile_no':fields.related('employee_id','mobile_phone',type='char',relation='hr.employee',string='Mobile No', store=True, readonly=True),
        'state': fields.selection([('draft', 'Draft'),('phase1', 'Phase-1'),
                                           ('phase2', 'Phase-2'),
                                           ('phase3', 'Phase-3'),
                                           ('completed', 'Completed')
                                           ], 'Status', readonly=True),
        #No Dues Details Columns(Facility)
        'icard_return':fields.selection([('yes', 'Yes'),
                                           ('no', 'No'),('na', 'N/A')], 'I-Card Return'),
        'access_card_return':fields.selection([('yes', 'Yes'),
                                           ('no', 'No'),('na', 'N/A')], 'Access Card Return'),
        'keys_return':fields.selection([('yes', 'Yes'),
                                           ('no', 'No'),('na', 'N/A')], 'Keys Return'),
        'headphone_return':fields.selection([('yes', 'Yes'),
                                           ('no', 'No'),('na', 'N/A')], 'Head Phone Return'),
        'name_delete':fields.selection([('yes', 'Yes'),
                                           ('no', 'No'),('na', 'N/A')], 'Name delete from attendance Registers'),
        'canteen_dues':fields.selection([('yes', 'Yes'),
                                           ('no', 'No'),('na', 'N/A')], 'Canteen dues Cleared'),
        'library_book':fields.selection([('yes', 'Yes'),
                                           ('no', 'No'),('na', 'N/A')], 'Library Books Return'),
        'remarks':fields.char('Remarks'),
        'submitted_by_facility':fields.many2one('res.users','Submitted By'),
        'submitted_on_facility':fields.datetime('Submitted On'),
        #No Dues Details Columns(Operation)
        'email_control':fields.char('Email Control'),
        'email_remarks':fields.char('Remarks'),
        'internet_control':fields.char('Internet Control'),
        'internet_remarks':fields.char('Remarks'),
        'remote_control':fields.char('Remote Control'),
        'remote_remarks':fields.char('Remarks'),
        'software_requirement':fields.char('Software Requirement'),
        'software_remarks':fields.char('Remarks'),
        'application_share':fields.char('Application Share Access'),
        'application_remarks':fields.char('Remarks'),
        'data_backup':fields.char('Databack-up Details'),
        'data_backup_remarks':fields.char('Remarks'),
        'handover_takeover':fields.selection([('yes', 'Yes'),
                                           ('no', 'No'),('na', 'N/A')], 'Handover Takeover Done'),
        'handover_remarks':fields.char('Remarks(if any items not return)'),
        'submitted_by_operation':fields.many2one('res.users','Submitted By'),
        'submitted_on_operation':fields.datetime('Submitted On'),
        
        #No Dues Details Columns(Technical)
        'login_name_tech':fields.char('Login Name'),
        'login_name_disable':fields.selection([('yes', 'Yes'),
                                           ('no', 'No'),('na', 'N/A')], 'Disable'),
        'login_remarks_tech':fields.char('User-Name Remarks'),
        'allocation_it_asset':fields.selection([('yes', 'Yes'),
                                           ('no', 'No'),('na', 'N/A')], 'Allocation of IT Assets'),
        'it_assets_disable':fields.selection([('yes', 'Yes'),
                                           ('no', 'No'),('na', 'N/A')], 'Disable'),
        'asset_remarks_tech':fields.char('Asset Remarks'),
        'email_id_tech':fields.selection([('yes', 'Yes'),
                                           ('no', 'No'),('na', 'N/A')], 'Email ID Created'),
        'email_id_disable':fields.selection([('yes', 'Yes'),
                                           ('no', 'No'),('na', 'N/A')], 'Disable'),
        'email_remarks_tech':fields.char('Email Remarks'),
        'internet_control_tech':fields.selection([('yes', 'Yes'),
                                           ('no', 'No'),('na', 'N/A')], 'Internet Access Control'),
        'internal_disable':fields.selection([('yes', 'Yes'),
                                           ('no', 'No'),('na', 'N/A')], 'Disable'),
        'internet_remarks_tech':fields.char('Internet Remarks'),
        'backup_setup_tech':fields.selection([('yes', 'Yes'),
                                           ('no', 'No'),('na', 'N/A')], 'Back-Up Setup'),
        'backup_setup_disable':fields.selection([('yes', 'Yes'),
                                           ('no', 'No'),('na', 'N/A')], 'Disable'),
        'backup_remarks_tech':fields.char('Back-up Remarks'),
        'software_requirement_tech':fields.selection([('yes', 'Yes'),
                                           ('no', 'No'),('na', 'N/A')], 'Software Provisioning and Access Control'),
        'software_disable':fields.selection([('yes', 'Yes'),
                                           ('no', 'No'),('na', 'N/A')], 'Disable'),
        'software_remarks_tech':fields.char('Software Provisioning Remarks'),
        'application_share_tech':fields.selection([('yes', 'Yes'),
                                           ('no', 'No'),('na', 'N/A')], 'Application Share Access'),
        'appliaction_share_disable':fields.selection([('yes', 'Yes'),
                                           ('no', 'No'),('na', 'N/A')], 'Disable'),
        'application_remarks_tech':fields.char('Share Access Remarks'),
        'submitted_by_technical':fields.many2one('res.users','Submitted By'),
        'submitted_on_technical':fields.datetime('Submitted On'),
       
        
        }
    
    _rec_name = 'nodues_number'
    
    _defaults = {
        'state': 'draft', 
    }
    
    def create(self, cr, uid, vals, context=None):
        """Create the unique id """
        vals['nodues_number']=self.pool.get('ir.sequence').get(cr, uid,'emp.no.dues')
        res=super(emp_no_dues, self).create(cr, uid, vals)
        return res
    
    def unlink(self, cr, uid, ids, context=None):        
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.state not in ['draft']:
                raise osv.except_osv(_('Warning!'),_('You cannot delete a full and final entry which is not in draft state.'))
        return super(emp_no_dues, self).unlink(cr, uid, ids, context) 
    
    def submit_draft(self, cr, uid, ids, context=None):   
        """Draft Submit. """ 
        return self.write(cr, uid, ids, {'state':'phase1'})
    
    def submit_phase1(self, cr, uid, ids, context=None):   
        """PHASE-1 Submit. """ 
        return self.write(cr, uid, ids, {'state':'phase2','submitted_by_operation': uid,'submitted_on_operation': datetime.now()})
    
    def submit_phase2(self, cr, uid, ids, context=None):   
        """PHASE-2 Submit. """ 
        return self.write(cr, uid, ids, {'state':'phase3','submitted_by_technical': uid,'submitted_on_technical': datetime.now()})
    
    def submit_phase3(self, cr, uid, ids, context=None):   
        """PHASE-3 Submit. """ 
        return self.write(cr, uid, ids, {'state':'completed','submitted_by_facility': uid,'submitted_on_facility': datetime.now()})
    
    def onchange_employee(self, cr, uid, ids, employee_id, context=None):
        res = {'value': {
                         'job_id': False, 
                         'department_id':False, 
                         'joining_date':False, 
                         'confirmation_status':False, 
                         'resign_id':False, 
                         'capture_date':False, 
                         'last_date':False, 
                         
                         }
               }
        
        joining_date = ''
        last_date = ''
        
        if employee_id:
            exit_ids = self.search(cr, uid, [('employee_id', '=', employee_id)], context=context)
            if len(exit_ids) > 0:
                raise osv.except_osv(_('Warning!'),
                                     _('No Dues has already been in progress/done for this employee.'))
            
            ee = self.pool.get('hr.employee').browse(cr, uid, employee_id, context=context)
            if ee:
                res['value']['job_id'] = ee.job_id.id
                res['value']['department_id'] = ee.department_id.id
                res['value']['dob'] = ee.birthday
                res['value']['division_id'] = ee.division.id
                res['value']['location_id'] = ee.office_location.id
                res['value']['gender'] = ee.gender
                res['value']['mobile_no'] = ee.mobile_phone
                joining_date = res['value']['joining_date'] = ee.joining_date
                res['value']['confirmation_status'] = ee.confirmation_status.title()
            
            emp_sep_id = self.pool.get('ids.hr.employee.separation').search(cr, uid , [('employee_id','=',employee_id),('state','=','done')], context=context)
            if emp_sep_id:
                es = self.pool.get('ids.hr.employee.separation').browse(cr, uid, emp_sep_id[0], context=context)
                if es:                
                    res['value']['resign_id'] = es.id
                    res['value']['capture_date'] = es.capture_date
                    last_date = res['value']['last_date'] = es.last_date
            emp_busi_id = self.pool.get('ids.business.information').search(cr, uid , [('employee_id','=',employee_id)], context=context)
            if emp_busi_id:
                eb = self.pool.get('ids.business.information').browse(cr, uid, emp_busi_id[0], context=context)
                if eb:                
                    res['value']['email_control'] = eb.email_control
                    res['value']['internet_control'] = eb.internet_control
                    res['value']['remote_control'] = eb.remote_control
                    res['value']['software_requirement'] = eb.software_requirements
                    res['value']['application_share'] = eb.application_share_access
                    res['value']['data_backup'] = eb.backup_remarks
            emp_tech_id = self.pool.get('ids.technical.information').search(cr, uid , [('employee_id','=',employee_id)], context=context)
            if emp_tech_id:
                et = self.pool.get('ids.technical.information').browse(cr, uid, emp_tech_id[0], context=context)
                if et:                
                    res['value']['allocation_it_asset'] = et.allocation_of_itassets
                    res['value']['email_id_tech'] = et.email_created
                    res['value']['internet_control_tech'] = et.internet_access_control
                    res['value']['backup_setup_tech'] = et.backup_setup
                    res['value']['software_requirement_tech'] = et.software_provisioning_and_access_control
                    res['value']['application_share_tech'] = et.application_share_access
        return res
            
                    
    
    
