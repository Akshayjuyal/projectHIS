#-*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
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

from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from openerp import netsvc
from openerp.osv import fields, osv
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools.translate import _
from openerp import SUPERUSER_ID

class hr_reward(osv.Model):
    
    _name = 'ids.hr.reward'
    _description = 'Employee Rewards & Recognitions'
    
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    
    def _default_employee(self, cr, uid, context=None):
        """Get default employee. """
        emp_ids = self.pool.get('hr.employee').search(cr, uid, [('user_id','=',uid)], context=context)
        return emp_ids and emp_ids[0] or False
    
    def is_visible(self, cr, uid, ids, name, args, context=None):
        """get award_type with the selection of award_id. """
        bl = ''
        result = {}             
        if not ids:
            return []
        else:
            
            for self_obj in self.browse(cr, uid, ids, context=context):                
                reward_id = self_obj.id
                award_type_id = self_obj.award_id.id
                
                if award_type_id:
                    data = self.pool.get('ids.hr.reward.award').read(cr, uid, award_type_id, ['award_type'], context=context)                    
                    if data:
                        bl = data['award_type']                
                
                result[self_obj.id] = bl                      
                
        return result 
    
    _columns = {
        'employee_id': fields.many2one('hr.employee', 'Name of the Nominee', required=True, readonly=True,
                               states={'draft': [('readonly',False)]},domain="[('working_status', '!=', 'exit')]"),
        'emp_code': fields.related('employee_id', 'emp_code', type='char',
                                            relation='hr.employee', string='Employee Code',
                                            store=True, readonly=True),        
        'job_id': fields.many2one('hr.job', 'Current Position', readonly=True,
                               states={'draft': [('readonly',False)]}),
        'department_id': fields.related('employee_id', 'department_id', type='many2one',
                                            relation='hr.department', string='Department',
                                            store=True, readonly=True),        
        'nominator_id': fields.many2one('hr.employee', 'Nominated By', required=True, readonly=True),
        'nominator_emp_code': fields.related('nominator_id', 'emp_code', type='char',
                                            relation='hr.employee', string='Employee Code',
                                            store=True, readonly=True), 
        'nominator_job_id':fields.related('nominator_id', 'job_id', type='many2one',
                                            relation='hr.job', string='Position',
                                            store=True, readonly=True),
	    'nominator_department_id': fields.related('nominator_id', 'department_id', type='many2one',
                                            relation='hr.department', string='Department',
                                            store=True, readonly=True),
        'award_id':fields.many2one('ids.hr.reward.award', 'Award Recommended:', required=True, readonly=True, states={'draft': [('readonly',False)]}),
        'period_month':fields.selection([('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'),
            ('5', 'May'), ('6', 'June'), ('7', 'July'), ('8', 'August'), ('9', 'September'),
            ('10', 'October'), ('11', 'November'), ('12', 'December')], 'Month', readonly=True, states={'draft': [('readonly',False)]}),
        'period_quarter':fields.selection([('1', 'Quarter1'), ('2', 'Quarter2'), ('3', 'Quarter3'), ('4', 'Quarter4')],'Quarter', readonly=True, states={'draft': [('readonly',False)]}),
        'period_year':fields.selection([(str(num), str(num)) for num in range((time.localtime().tm_year), (time.localtime().tm_year)-2, -1)], 'Year', readonly=True, states={'draft': [('readonly',False)]}),
        'achievements':fields.text('Achievements',required=True),        
        'impact':fields.text('Impact'),
        'award_date':fields.date('Date'),
        'productivity':fields.float('Productivity(40)'),
        'quality':fields.float('Quality(40)'),
        'attendance':fields.float('Attendance(10)'),
        'behaviour':fields.float('Attitude/General Behavior(10)'),
        'remarks_reward':fields.text('Remarks', size=200),                
        'state': fields.selection([
                                   ('draft', 'Draft'),
                                   ('confirm', 'Waiting for Approval'),     
                                   ('approve', 'Approved'),                                   
                                   ('done', 'Allocated'),
                                   ('cancel', 'Cancelled'),
                                  ],
                                  'State', readonly=True),
        'confirm_mgr_id': fields.many2one('hr.employee', 'Confirm', readonly=True, help='This area is automatically filled by the user who confirms the reward'),
        'done_mgr_id': fields.many2one('hr.employee', 'Approve', readonly=True, help='This area is automatically filled by the user who approves the reward'),
        'cancel_mgr_id': fields.many2one('hr.employee', 'Cancel', readonly=True, help='This area is automatically filled by the user who cancels the reward'),
        'awd_type':fields.function(is_visible, type='char', method=True, store=False, string='Visibility'),
    }
    
    _rec_name = 'emp_code'
    
    _defaults = {
        'state': 'draft',
        'nominator_id': _default_employee,
        'award_date':datetime.now()
    }
    
    _track = {
        'state': {
            'ids_hr_reward.mt_alert_reward_confirmed': lambda self, cr,uid, obj, ctx=None: obj['state'] == 'confirm',            
            'ids_hr_reward.mt_alert_reward_done': lambda self, cr,uid, obj, ctx=None: obj['state'] == 'done',
        },
    }
    
    def create(self, cr, uid, vals, context=None): 
        """Constraint on selecting period in months, quarter, year on creating reward. """       
        if 'period_month' in vals:
            now=datetime.now()
            month=now.month
            year=now.year
            prev=month-1
            if month==1:
                prev=12
            if vals['period_month'] not in (str(month),str(prev),False):
                raise osv.except_osv(_('Warning!'), _('Please select the appropriate month.')) 
        
        if 'period_quarter' in vals:
            months=0
            qrtr_prev=0
            now=datetime.now()
            month=now.month
            if month==1:
                months=10
            if month==2:
                months=11
            if month==3:
                months=12
            if month==4:
                months=1
            if month==5:
                months=2
            if month==6:
                months=3
            if month==7:
                months=4
            if month==8:
                months=5
            if month==9:
                months=6
            if month==10:
                months=7
            if month==11:
                months=8
            if month==12:
                months=9
            qrtr = ((months-1)/3)  + 1
            if qrtr==1:
                qrtr_prev=4
            else:
                qrtr_prev=qrtr-1
            if vals['period_quarter'] not in (str(qrtr),str(qrtr_prev),False):
                raise osv.except_osv(_('Warning!'), _('Please select the appropriate quarter.')) 
        
        
        if 'period_year' in vals:
            now=datetime.now()
            month=now.month
            year=now.year
            prev=year-1
            after=year+1
            if month<>12 and month<>1:
                if vals['period_year'] not in (str(year),False):
                    raise osv.except_osv(_('Warning!'), _('Please select the appropriate year.')) 
          
        if 'award_date' in vals:
            now=datetime.now()
            current = now.strftime('%Y-%m-%d')
            if vals['award_date']>current:
                raise osv.except_osv(_('Warning!'), _('Please select Date as current Date or less than Current Date.')) 
        
        if 'productivity' in vals:
            if vals['productivity']>40:
                raise osv.except_osv(_('Warning!'), _('Productivity waitages should not more than 40.')) 
                  
        if 'quality' in vals:
            if vals['quality']>40:
                raise osv.except_osv(_('Warning!'), _('Quality waitages should not more than 40.')) 
                
        if 'attendance' in vals:
            if vals['attendance']>10:
                raise osv.except_osv(_('Warning!'), _('Attendance waitages should not more than 10.')) 
                  
        if 'behaviour' in vals:
            if vals['behaviour']>10:
                raise osv.except_osv(_('Warning!'), _('Attitude/General Behavior waitages should not more than 10.')) 
                  
            
        
                   
        emp_ids = self.pool.get('ids.hr.reward').search(cr, uid, [('employee_id','=',vals['employee_id']), ('award_id','=',vals['award_id']), ('period_month','=',vals['period_month']), ('period_quarter','=',vals['period_quarter']), ('period_year','=',vals['period_year']), ('state','!=','cancel')], context=context)
        if emp_ids:
            raise osv.except_osv(_('Warning!'), _('Reward is already in progress for this Period.'))
        res=super(hr_reward, self).create(cr, uid, vals)
        return res
    
    def write(self, cr, uid, ids, vals, context=None):
        """Constraint on selecting period in months, quarter, year while editting. """ 
        if 'period_month' in vals:
            now=datetime.now()
            month=now.month
            year=now.year
            prev=month-1
            if vals['period_month']not in (str(month),str(prev),False):
                raise osv.except_osv(_('Warning!'), _('Please select the appropriate month.')) 
          
        if 'period_quarter' in vals:
            months=0
            now=datetime.now()
            month=now.month
            if month==1:
                months=10
            if month==2:
                months=11
            if month==3:
                months=12
            if month==4:
                months=1
            if month==5:
                months=2
            if month==6:
                months=3
            if month==7:
                months=4
            if month==8:
                months=5
            if month==9:
                months=6
            if month==10:
                months=7
            if month==11:
                months=8
            if month==12:
                months=9
            qrtr = ((months-1)/3)  + 1
            if qrtr==1:
                qrtr_prev=4
            else:
                qrtr_prev=qrtr-1
            if vals['period_quarter'] not in (str(qrtr),str(qrtr_prev),False):
                raise osv.except_osv(_('Warning!'), _('Please select the appropriate quarter.')) 
        
        if 'period_year' in vals:
            now=datetime.now()
            month=now.month
            year=now.year
            prev=year-1
            after=year+1
            if month<>12 and month<>1:
                if vals['period_year'] not in (str(year),False):
                    raise osv.except_osv(_('Warning!'), _('Please select the appropriate year.')) 
        
        if 'award_date' in vals:
            now=datetime.now()
            current = now.strftime('%Y-%m-%d')
            if vals['award_date']>current:
                raise osv.except_osv(_('Warning!'), _('Please select Date as current Date or less than Current Date.')) 
               
        if 'productivity' in vals:
            if vals['productivity']>40:
                raise osv.except_osv(_('Warning!'), _('Productivity waitages should not more than 40.')) 
                  
        if 'quality' in vals:
            if vals['quality']>40:
                raise osv.except_osv(_('Warning!'), _('Quality waitages should not more than 40.')) 
                
        if 'attendance' in vals:
            if vals['attendance']>10:
                raise osv.except_osv(_('Warning!'), _('Attendance waitages should not more than 10.')) 
                  
        if 'behaviour' in vals:
            if vals['behaviour']>10:
                raise osv.except_osv(_('Warning!'), _('Attitude/General Behavior waitages should not more than 10.')) 
                      
        
        vals_old = {}
        vals_new = {}
        for obj in self.pool.get('ids.hr.reward').browse(cr, uid, ids, context=context):
            vals_old['award_id'] = obj.award_id.id
            vals_old['period_month'] = obj.period_month
            vals_old['period_quarter'] = obj.period_quarter
            vals_old['period_year'] = obj.period_year
            vals_old['employee_id'] = obj.employee_id.id
        
                          
        vals_new['employee_id'] = vals['employee_id'] if vals.get('employee_id') else vals_old['employee_id']
        vals_new['award_id'] = vals['award_id'] if vals.get('award_id') else vals_old['award_id']
        vals_new['period_month'] = vals['period_month'] if vals.get('period_month') else vals_old['period_month']
        vals_new['period_quarter'] = vals['period_quarter'] if vals.get('period_quarter') else vals_old['period_quarter']
        vals_new['period_year'] = vals['period_year'] if vals.get('period_year') else vals_old['period_year']        
        
        emp_ids = self.pool.get('ids.hr.reward').search(cr, uid, [('employee_id','=',vals_new['employee_id']), ('id','not in',ids), ('award_id','=',vals_new['award_id']), ('period_month','=',vals_new['period_month']), ('period_quarter','=',vals_new['period_quarter']), ('period_year','=',vals_new['period_year']), ('state','!=','cancel')], context=context)
        if emp_ids:
            raise osv.except_osv(_('Warning!'), _('Reward is already in progress for this Period.'))      
       
        res=super(hr_reward, self).write(cr, uid, ids, vals)
        return res
        
    def _needaction_domain_get(self, cr, uid, context=None):
        
        users_obj = self.pool.get('res.users')
        
        domain = []
        if users_obj.has_group(cr, uid, 'base.group_hr_manager'):
            domain = [('state','=','confirm')]
            return domain
        
        return False
    
    def unlink(self, cr, uid, ids, context=None):
        
        for xfer in self.browse(cr, uid, ids, context=context):
            if xfer.state not in ['draft']:
                raise osv.except_osv(_('Unable to Delete Reward!'),
                                     _('Rewards/Recognitions has been initiated. Either cancel the reward or create another reward to undo it.'))
        
        return super(hr_reward, self).unlink(cr, uid, ids, context=context)
    
    def onchange_employee(self, cr, uid, ids, employee_id, context=None):
        """Get some associated fields on change of employee_id. """
        res = {'value': {'job_id': False}}
               
        if employee_id:    
            ee = self.pool.get('hr.employee').browse(cr, uid, employee_id, context=context)
            res['value']['job_id'] = ee.job_id.id
            res['value']['department_id'] = ee.department_id.id
            res['value']['emp_code'] = ee.emp_code                   
                    
        return res
    
    def onchange_nominated_by(self, cr, uid, ids, employee_id, context=None):
        """Get some associated fields on change of nominator_id. """
        res = {'value': {'nominator_job_id': False}}
        if employee_id:    
            ee = self.pool.get('hr.employee').browse(cr, uid, employee_id, context=context)            
            res['value']['nominator_job_id'] = ee.job_id.id
            res['value']['nominator_department_id'] = ee.department_id.id
            res['value']['nominator_emp_code'] = ee.emp_code            
                    
        return res
    
    def onchange_award(self, cr, uid, ids, award_id, context=None):
        """get award type with selection of particular award.  """
        res = {'value': {'awd_type': False, 'period_month': False, 'period_quarter': False}}
               
        if award_id:    
            data = self.pool.get('ids.hr.reward.award').read(cr, uid, award_id, ['award_type'], context=context)                    
            if data:
                res['value']['awd_type'] = data['award_type']                 
                    
        return res
    
    
    def state_confirm(self, cr, uid, ids, context=None): 
        """Workflow initiated- Submit to HOD. """ 
        self._check_validate(cr, uid, ids, context=context)
        id=self.pool.get('ids.hr.reward')
        change=self.browse(cr, uid, ids, context=None)
        period_month=''
        period_quarter=''
        if change.period_month=='1':
            period_month="January"
        if change.period_month=='2':
            period_month="February"
        if change.period_month=='3':
            period_month="March"
        if change.period_month=='4':
            period_month="April"
        if change.period_month=='5':
            period_month="May"
        if change.period_month=='6':
            period_month="June"
        if change.period_month=='7':
            period_month="July"
        if change.period_month=='8':
            period_month="August"
        if change.period_month=='9':
            period_month="September"
        if change.period_month=='10':
            period_month="October"
        if change.period_month=='11':
            period_month="November"
        if change.period_month=='12':
            period_month="December"
            
        if change.period_quarter=='1':
            period_quarter="Quarter1"
        if change.period_quarter=='2':
            period_quarter="Quarter2"
        if change.period_quarter=='3':
            period_quarter="Quarter3"
        if change.period_quarter=='4':
            period_quarter="Quarter4"
        values={}
        url="http://ids-erp.idsil.loc:8069/web"
        if change.period_month:
            values = {
            'subject': 'R&R Nomination -' + ' ' + change.employee_id.name+' '+ 'for'+' '+period_month+' '+ change.period_year,
            'body_html': 'Reward & Recognition nomination' + ' '  + change.employee_id.name+' '+ 'for month'+' '+period_month +' '+ change.period_year + ' ' + 'Intiated.<br/><br/><br/>Kindly do not reply.<br/>---This is auto generated email---<br/>Regards:<br/>ERP HR Team<br/>IDS Infotech LTD.<br/>Url:'+url,
            'email_to': change.nominator_id.parent_id.work_email,
            'email_from': 'info.openerp@idsil.com',
              }
        if change.period_quarter:
            values = {
            'subject': 'R&R Nomination -' + ' ' + change.employee_id.name+' '+ 'for'+' '+period_quarter+' '+ change.period_year,
            'body_html': 'Reward & Recognition nomination' + ' '  + change.employee_id.name+' '+ 'for'+' '+period_quarter +' '+ change.period_year + ' ' + 'Intiated.<br/><br/><br/>Kindly do not reply.<br/>---This is auto generated email---<br/>Regards:<br/>ERP HR Team<br/>IDS Infotech LTD.<br/>Url:'+url,
            'email_to': change.nominator_id.parent_id.work_email,
            'email_from': 'info.openerp@idsil.com',
              }
        if change.period_year and change.award_id.award_type=='yearly':
            values = {
            'subject': 'R&R Nomination -' + ' ' + change.employee_id.name+' '+ 'for year'+' '+ change.period_year,
            'body_html': 'Reward & Recognition nomination' + ' '  + change.employee_id.name+' '+ 'for year'+' '+ change.period_year + ' ' + 'Intiated.<br/><br/><br/>Kindly do not reply.<br/>---This is auto generated email---<br/>Regards:<br/>ERP HR Team<br/>IDS Infotech LTD.<br/>Url:'+url,
            'email_to': change.nominator_id.parent_id.work_email,
            'email_from': 'info.openerp@idsil.com',
              }
        #---------------------------------------------------------------
        mail_obj = self.pool.get('mail.mail') 
        msg_id = mail_obj.create(cr, uid, values, context=context) 
        if msg_id: 
            mail_obj.send(cr, uid, [msg_id], context=context)
        self.write(cr, uid, ids, {'state': 'confirm'}, context=context)
        
        return True
    
    def state_approve(self, cr, uid, ids, context=None):
        """approval by HOD. """ 
        id=self.pool.get('ids.hr.reward')
        change=self.browse(cr, uid, ids, context=None) 
        url="http://ids-erp.idsil.loc:8069/web"
        period_month=''
        period_quarter=''
        if change.period_month=='1':
            period_month="January"
        if change.period_month=='2':
            period_month="February"
        if change.period_month=='3':
            period_month="March"
        if change.period_month=='4':
            period_month="April"
        if change.period_month=='5':
            period_month="May"
        if change.period_month=='6':
            period_month="June"
        if change.period_month=='7':
            period_month="July"
        if change.period_month=='8':
            period_month="August"
        if change.period_month=='9':
            period_month="September"
        if change.period_month=='10':
            period_month="October"
        if change.period_month=='11':
            period_month="November"
        if change.period_month=='12':
            period_month="December"
            
        if change.period_quarter=='1':
            period_quarter="Quarter1"
        if change.period_quarter=='2':
            period_quarter="Quarter2"
        if change.period_quarter=='3':
            period_quarter="Quarter3"
        if change.period_quarter=='4':
            period_quarter="Quarter4"
        if change.period_month:
            values = {
            'subject': 'R&R Nomination -' + ' ' + change.employee_id.name+' '+ 'for'+' '+period_month+' '+ change.period_year,
            'body_html': 'Reward & Recognition nomination' + ' '  + change.employee_id.name+' '+ 'for month'+' '+period_month +' '+ change.period_year + ' ' + 'is approved.<br/><br/><br/>Kindly do not reply.<br/>---This is auto generated email---<br/>Regards:<br/>ERP HR Team<br/>IDS Infotech LTD.<br/>Url:'+url,
            'email_to': change.nominator_id.work_email,
            'email_cc': change.nominator_id.division.hr_email,
            'email_from': 'info.openerp@idsil.com',
              }
        if change.period_quarter:
            values = {
            'subject': 'R&R Nomination -' + ' ' + change.employee_id.name+' '+ 'for'+' '+period_quarter+' '+ change.period_year,
            'body_html': 'Reward & Recognition nomination' + ' '  + change.employee_id.name+' '+ 'for'+' '+period_quarter +' '+ change.period_year + ' ' + 'is approved.<br/><br/><br/>Kindly do not reply.<br/>---This is auto generated email---<br/>Regards:<br/>ERP HR Team<br/>IDS Infotech LTD.<br/>Url:'+url,
            'email_to': change.nominator_id.work_email,
            'email_cc': change.nominator_id.division.hr_email,
            'email_from': 'info.openerp@idsil.com',
              }
        if change.period_year and change.award_id.award_type=='yearly':
            values = {
            'subject': 'R&R Nomination -' + ' ' + change.employee_id.name+' '+ 'for year'+' '+ change.period_year,
            'body_html': 'Reward & Recognition nomination' + ' '  + change.employee_id.name+' '+ 'for year'+' '+ change.period_year + ' ' + 'is approved.<br/><br/><br/>Kindly do not reply.<br/>---This is auto generated email---<br/>Regards:<br/>ERP HR Team<br/>IDS Infotech LTD.<br/>Url:'+url,
            'email_to': change.nominator_id.work_email,
            'email_cc': change.nominator_id.division.hr_email,
            'email_from': 'info.openerp@idsil.com',
              }
        #---------------------------------------------------------------
        mail_obj = self.pool.get('mail.mail') 
        msg_id = mail_obj.create(cr, uid, values, context=context) 
        if msg_id: 
            mail_obj.send(cr, uid, [msg_id], context=context)
        self.write(cr, uid, ids, {'state': 'approve'}, context=context)
        
        return True
    
    def state_done(self, cr, uid, ids, context=None):
        """award allocated by Location HR. """
        id=self.pool.get('ids.hr.reward')
        url="http://ids-erp.idsil.loc:8069/web"
        change=self.browse(cr, uid, ids, context=None) 
        period_month=''
        period_quarter=''
        if change.period_month=='1':
            period_month="January"
        if change.period_month=='2':
            period_month="February"
        if change.period_month=='3':
            period_month="March"
        if change.period_month=='4':
            period_month="April"
        if change.period_month=='5':
            period_month="May"
        if change.period_month=='6':
            period_month="June"
        if change.period_month=='7':
            period_month="July"
        if change.period_month=='8':
            period_month="August"
        if change.period_month=='9':
            period_month="September"
        if change.period_month=='10':
            period_month="October"
        if change.period_month=='11':
            period_month="November"
        if change.period_month=='12':
            period_month="December"
            
        if change.period_quarter=='1':
            period_quarter="Quarter1"
        if change.period_quarter=='2':
            period_quarter="Quarter2"
        if change.period_quarter=='3':
            period_quarter="Quarter3"
        if change.period_quarter=='4':
            period_quarter="Quarter4"
        if change.period_month:
            values = {
            'subject': 'R&R Nomination -' + ' ' + change.employee_id.name+' '+ 'for'+' '+period_month+' '+ change.period_year,
            'body_html': 'Award is Allocated for nomination' + ' '  + change.employee_id.name+' '+ 'for month'+' '+period_month +' '+ change.period_year + ' ' + '.<br/><br/><br/>Kindly do not reply.<br/>---This is auto generated email---<br/>Regards:<br/>ERP HR Team<br/>IDS Infotech LTD.<br/>Url:'+url,
            'email_to': change.nominator_id.parent_id.work_email,
            'email_cc':  [change.nominator_id.work_email,'amrita.k@idsil.com'],
            'email_from': 'info.openerp@idsil.com',
              }
        if change.period_quarter:
            values = {
            'subject': 'R&R Nomination -' + ' ' + change.employee_id.name+' '+ 'for'+' '+period_quarter+' '+ change.period_year,
            'body_html': 'Award is Allocated for nomination' + ' '  + change.employee_id.name+' '+ 'for'+' '+period_quarter +' '+ change.period_year + ' ' + '.<br/><br/><br/>Kindly do not reply.<br/>---This is auto generated email---<br/>Regards:<br/>ERP HR Team<br/>IDS Infotech LTD.<br/>Url:'+url,
            'email_to': change.nominator_id.parent_id.work_email,
            'email_cc':  [change.nominator_id.work_email,'amrita.k@idsil.com'],
            'email_from': 'info.openerp@idsil.com',
              }
        if change.period_year and change.award_id.award_type=='yearly':
            values = {
            'subject': 'R&R Nomination -' + ' ' + change.employee_id.name+' '+ 'for year'+' '+ change.period_year,
            'body_html': 'Award is Allocated for nomination' + ' '  + change.employee_id.name+' '+ 'for year'+' '+ change.period_year + ' ' + '.<br/><br/><br/>Kindly do not reply.<br/>---This is auto generated email---<br/>Regards:<br/>ERP HR Team<br/>IDS Infotech LTD.<br/>Url:'+url,
            'email_to': change.nominator_id.parent_id.work_email,
            'email_cc':  [change.nominator_id.work_email,'amrita.k@idsil.com'],
            'email_from': 'info.openerp@idsil.com',
              }
        #---------------------------------------------------------------
        mail_obj = self.pool.get('mail.mail') 
        msg_id = mail_obj.create(cr, uid, values, context=context) 
        if msg_id: 
            mail_obj.send(cr, uid, [msg_id], context=context)
    
        self.write(cr, uid, ids, {'state': 'done'}, context=context)
                    
        return True
    
    def state_cancel(self, cr, uid, ids, context=None): 
        """In case,Award gets refused. """
        id=self.pool.get('ids.hr.reward')
        url="http://ids-erp.idsil.loc:8069/web"
        change=self.browse(cr, uid, ids, context=None)
        period_month=''
        period_quarter=''
        if change.period_month=='1':
            period_month="January"
        if change.period_month=='2':
            period_month="February"
        if change.period_month=='3':
            period_month="March"
        if change.period_month=='4':
            period_month="April"
        if change.period_month=='5':
            period_month="May"
        if change.period_month=='6':
            period_month="June"
        if change.period_month=='7':
            period_month="July"
        if change.period_month=='8':
            period_month="August"
        if change.period_month=='9':
            period_month="September"
        if change.period_month=='10':
            period_month="October"
        if change.period_month=='11':
            period_month="November"
        if change.period_month=='12':
            period_month="December"
            
        if change.period_quarter=='1':
            period_quarter="Quarter1"
        if change.period_quarter=='2':
            period_quarter="Quarter2"
        if change.period_quarter=='3':
            period_quarter="Quarter3"
        if change.period_quarter=='4':
            period_quarter="Quarter4"
        if change.period_month:
            values = {
            'subject': 'R&R Nomination -' + ' ' + change.employee_id.name+' '+ 'for'+' '+period_month+' '+ change.period_year,
            'body_html': 'Your Reward & Recognition nomination' + ' '  + change.employee_id.name+' '+ 'for month'+' '+period_month +' '+ change.period_year + ' ' + 'is refused.<br/><br/><br/>Kindly do not reply.<br/>---This is auto generated email---<br/>Regards:<br/>ERP HR Team<br/>IDS Infotech LTD.<br/>Url:'+url,
            'email_to': change.nominator_id.work_email,
            'email_from': 'info.openerp@idsil.com',
              }
        if change.period_quarter:
            values = {
            'subject': 'R&R Nomination -' + ' ' + change.employee_id.name+' '+ 'for'+' '+period_quarter+' '+ change.period_year,
            'body_html': 'Your Reward & Recognition nomination' + ' '  + change.employee_id.name+' '+ 'for'+' '+period_quarter +' '+ change.period_year + ' ' + 'is refused.<br/><br/><br/>Kindly do not reply.<br/>---This is auto generated email---<br/>Regards:<br/>ERP HR Team<br/>IDS Infotech LTD.<br/>Url:'+url,
            'email_to': change.nominator_id.work_email,
            'email_from': 'info.openerp@idsil.com',
              }
        if change.period_year and change.award_id.award_type=='yearly':
            values = {
            'subject': 'R&R Nomination -' + ' ' + change.employee_id.name+' '+ 'for year'+' '+ change.period_year,
            'body_html': 'Your Reward & Recognition nomination' + ' '  + change.employee_id.name+' '+ 'for year'+' '+ change.period_year + ' ' + 'is refused.<br/><br/><br/>Kindly do not reply.<br/>---This is auto generated email---<br/>Regards:<br/>ERP HR Team<br/>IDS Infotech LTD.<br/>Url:'+url,
            'email_to': change.nominator_id.work_email,
            'email_from': 'info.openerp@idsil.com',
              }
        #---------------------------------------------------------------
        mail_obj = self.pool.get('mail.mail') 
        msg_id = mail_obj.create(cr, uid, values, context=context) 
        if msg_id: 
            mail_obj.send(cr, uid, [msg_id], context=context)
        
        self.write(cr, uid, ids, {'state': 'cancel'}, context=context)
                    
        return True
    
    def _check_validate(self, cr, uid, ids, context=None):
        """Constarints on Validation of awrd allocated. """
        users_obj = self.pool.get('res.users')        
        
        if not users_obj.has_group(cr, uid, 'base.group_business_head'):
            
            for self_obj in self.browse(cr, uid, ids, context=context):
                if self_obj.employee_id.user_id.id == uid: 
                    raise osv.except_osv(_('Warning!'), _('You cannot nominate yourself.'))
                           
                emp_info = self.pool.get('hr.employee').browse(cr, uid, [self_obj.nominator_id.id], context=context)           
                if emp_info:
                    if emp_info[0].parent_id.id == self_obj.employee_id.id:
                        raise osv.except_osv(_('Warning!'), _('You cannot nominate your manager.'))                    
    
class ids_hr_reward_award(osv.osv):
    
    _name = 'ids.hr.reward.award'
    _description = "Reward Awards"    
    _columns = {
                'name':fields.char('Award Name: ', size=200, required=True),
                'award_type':fields.selection([('monthly','Monthly'),('quarterly','Quarterly'), ('yearly','Yearly')],'Award Type: ', required=True)
                }
