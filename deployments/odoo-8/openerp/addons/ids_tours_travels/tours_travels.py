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

import time

from openerp import netsvc
from openerp.osv import fields, osv
from openerp.tools.translate import _

import openerp.addons.decimal_precision as dp

class ids_tours_travels(osv.osv):
    
    def _get_currency(self, cr, uid, context=None):
        """get currency of the company. """
        user = self.pool.get('res.users').browse(cr, uid, [uid], context=context)[0]
        return user.company_id.currency_id.id

    def _employee_get(obj, cr, uid, context=None):
        """Get the value of employee through login user. """
        if context is None:
    	    context = {}
        
        ids = obj.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
        
        if ids:
    	    return ids[0]
        
        return False

    _name = "ids.tours.travels"
    _inherit = ['mail.thread']
    _description = "IDS Tours and Travles"
    _order = "id desc"
        
    _columns = {                
	    
        'name': fields.char('Description', size=128, required=True, readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}),
        'id': fields.integer('Sheet ID', readonly=True),
        'date': fields.date('Date', select=True, readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}),
        'journal_id': fields.many2one('account.journal', 'Force Journal', help = "The journal used when the expense is done."),
        'employee_id': fields.many2one('hr.employee', "Employee", required=True, readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}),
        'user_id': fields.many2one('res.users', 'User', required=True),
        'date_confirm': fields.date('Confirmation Date', select=True, help="Date of the confirmation of the sheet expense. It's filled when the button Confirm is pressed."),
        'date_valid': fields.date('Validation Date', select=True, help="Date of the acceptation of the sheet expense. It's filled when the button Accept is pressed."),
        'user_valid': fields.many2one('res.users', 'Validation By', readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}),                
        'from_date': fields.date('Travel Duration', select=True, readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}),
        'to_date': fields.date('', select=True, readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}),
        'advance_requested': fields.selection([
            ('yes', 'Yes'),
            ('no', 'No'),
            ], 'Advance Requested', readonly=True, required=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}),
        'advance_amount': fields.float('Advance Amount', digits_compute=dp.get_precision('Product Price'), readonly=True, required=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}),
	    'advance_details': fields.text('Advance Details', readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}),
	    'line_ids': fields.one2many('ids.tours.travels.line', 'tours_travle_id', 'Tours And Travel Lines', readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}),
        'note': fields.text('Purpose'),        
        'department_id':fields.many2one('hr.department','Department', readonly=True),
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'state': fields.selection([
            ('draft', 'New'),
            ('cancelled', 'Refused'),
            ('confirm', 'Waiting Approval'),
            ('accepted', 'Approved'),
            ('done', 'Done'),
            ],
        'status', readonly=True, track_visibility='onchange',
            help='When the expense request is created the status is \'Draft\'.\n It is confirmed by the user and request is sent to admin, the status is \'Waiting Confirmation\'.\
            \nIf the admin accepts it, the status is \'Accepted\'.\n If the accounting entries are made for the expense request, the status is \'Waiting Payment\'.'),
        'tour_id': fields.char("Travles/Expense Number", size=25, readonly=True),
    }
    _defaults = {
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'hr.employee', context=c),
        'date': fields.date.context_today,
	    'from_date': fields.date.context_today,
	    'to_date': fields.date.context_today,
        'state': 'draft',
        'employee_id': _employee_get,
        'user_id': lambda cr, uid, id, c={}: id,
	    'advance_requested': 'no',
    }

    _rec_name = 'tour_id'
    
    _sql_constraints = [
        ('from_date_check', "CHECK (to_date >= from_date)", "Travels To date should be greater than From date."),
        ('travel_duration_date_check', "CHECK (date_confirm <= to_date and date_confirm >= from_date)", "Travels confirmation date should be less than or equal to From date and greater than or equal to To date.")
	
    ] 
    
    def create(self, cr, uid, vals, context=None):
        """Create the unique tour id used for reimbursement. """
        vals['tour_id']=self.pool.get('ir.sequence').get(cr, uid,'ids.tours.travels')
        res=super(ids_tours_travels, self).create(cr, uid, vals)
        return res

    def onchange_employee_id(self, cr, uid, ids, employee_id, context=None):
        """Get associated values with employee id. """
        emp_obj = self.pool.get('hr.employee')
        department_id = False
        company_id = False
        
        if employee_id:
	        employee = emp_obj.browse(cr, uid, employee_id, context=context)
	        department_id = employee.department_id.id
	        company_id = employee.company_id.id
	    
        return {'value': {'department_id': department_id, 'company_id': company_id}}

    '''def onchange_currency_id(self, cr, uid, ids, currency_id=False, company_id=False, context=None):
        
	    res =  {'value': {'journal_id': False}}
        journal_ids = self.pool.get('account.journal').search(cr, uid, [('type','=','purchase'), ('currency','=',currency_id), ('company_id', '=', company_id)], context=context)
	
        if journal_ids:
            res['value']['journal_id'] = journal_ids[0]
            
	    return res'''
    
    def tours_travels_confirm(self, cr, uid, ids, context=None):
        """Workflow initiated-submit to manager. """
        for tours_travel in self.browse(cr, uid, ids):
            if tours_travel.employee_id and tours_travel.employee_id.parent_id.user_id:
                self.message_subscribe_users(cr, uid, [tours_travel.id], user_ids=[tours_travel.employee_id.parent_id.user_id.id])
                
        travel=self.browse(cr, uid, ids, context=None)
        url="http://ids-erp.idsil.loc:8069/web"
        values = {
        'subject': 'Employee Tours and Travels Expenses' + '- ' + travel.employee_id.name,
        'body_html': travel.employee_id.name+ ' ' + 'has created the Tours and Travels expenses.Please take necessary action.<br/><br/><br/>Kindly do not reply.<br/>---This is auto generated email---<br/>Regards:<br/>ERP HR Team<br/>IDS Infotech. <br/><br/>Url:'+url,
        'email_to': travel.employee_id.parent_id.work_email,
        'email_from': 'info.openerp@idsil.com',
          }
        #---------------------------------------------------------------
        mail_obj = self.pool.get('mail.mail') 
        msg_id = mail_obj.create(cr, uid, values, context=context) 
        if msg_id: 
            mail_obj.send(cr, uid, [msg_id], context=context)
        
        
        
        return self.write(cr, uid, ids, {'state': 'confirm', 'date_confirm': time.strftime('%Y-%m-%d')}, context=context)	

    def tours_travels_accept(self, cr, uid, ids, context=None):
        """Validated by Manager """
        travel=self.browse(cr, uid, ids, context=None)
        url="http://ids-erp.idsil.loc:8069/web"
        values = {
        'subject': 'Employee Tours and Travels Expenses' + '- ' + travel.employee_id.name,
        'body_html':  'The Tours and Travels Expenses created by'+' '+travel.employee_id.name+ ' ' + 'has Approved for First Approval.<br/><br/><br/>Kindly do not reply.<br/>---This is auto generated email---<br/>Regards:<br/>ERP HR Team<br/>IDS Infotech LTD.<br/><br/>Url:'+url,
        'email_to': travel.employee_id.parent_id.parent_id.work_email,
        'email_cc': travel.employee_id.work_email, 
        'email_from': 'info.openerp@idsil.com',
          }
        #---------------------------------------------------------------
        mail_obj = self.pool.get('mail.mail') 
        msg_id = mail_obj.create(cr, uid, values, context=context) 
        if msg_id: 
            mail_obj.send(cr, uid, [msg_id], context=context)
        
        
        return self.write(cr, uid, ids, {'state': 'accepted', 'date_valid': time.strftime('%Y-%m-%d'), 'user_valid': uid}, context=context)

    def tours_travels_canceled(self, cr, uid, ids, context=None):
        """cancelled reimbursement """

        travel=self.browse(cr, uid, ids, context=None)
        url="http://ids-erp.idsil.loc:8069/web"
        values = {
        'subject': 'Employee Tours and Travels Expenses' + '- ' + travel.employee_id.name,
        'body_html':  'The Tours and Travels Expenses created by'+' '+travel.employee_id.name+ ' ' + 'has Refused.<br/><br/><br/>Kindly do not reply.<br/>---This is auto generated email---<br/>Regards:<br/>ERP HR Team<br/>IDS Infotech LTD.<br/><br/>Url:'+url,
        'email_to': travel.employee_id.parent_id.work_email,
        'email_cc': travel.employee_id.work_email, 
        'email_from': 'info.openerp@idsil.com',
          }
        #---------------------------------------------------------------
        mail_obj = self.pool.get('mail.mail') 
        msg_id = mail_obj.create(cr, uid, values, context=context) 
        if msg_id: 
            mail_obj.send(cr, uid, [msg_id], context=context)
        
        return self.write(cr, uid, ids, {'state': 'cancelled'}, context=context)
    
    def tours_travels_create(self, cr, uid, ids, context=None):
        """Reimbursement Approved. """

        travel=self.browse(cr, uid, ids, context=None)
        url="http://ids-erp.idsil.loc:8069/web"
        values = {
        'subject': 'Employee Tours and Travels Expenses' + '- ' + travel.employee_id.name,
        'body_html':  'The Tours and Travels Expenses created by'+' '+travel.employee_id.name+ ' ' + 'has Approved.<br/><br/><br/>Kindly do not reply.<br/>---This is auto generated email---<br/>Regards:<br/>ERP HR Team<br/>IDS Infotech LTD.<br/><br/>Url:'+url,
        'email_to': travel.employee_id.parent_id.work_email,
        'email_cc': travel.employee_id.work_email, 
        'email_from': 'info.openerp@idsil.com',
          }
        #---------------------------------------------------------------
        mail_obj = self.pool.get('mail.mail') 
        msg_id = mail_obj.create(cr, uid, values, context=context) 
        if msg_id: 
            mail_obj.send(cr, uid, [msg_id], context=context)
        
	    self.write(cr, uid, ids, {'state': 'done', 'date_valid': time.strftime('%Y-%m-%d'), 'user_valid': uid}, context=context)
	
	

###########################
# Tours And Travles Grid
###########################

class ids_tours_travels_line(osv.osv):
    
    _name = "ids.tours.travels.line"
    _description = "IDS Tours And Travles Line"

    '''def _amount(self, cr, uid, ids, field_name, arg, context=None):
        if not ids:
            return {}
        cr.execute("SELECT l.id,COALESCE(SUM(l.unit_amount*l.unit_quantity),0) AS amount FROM hr_expense_line l WHERE id IN %s GROUP BY l.id ",(tuple(ids),))
        res = dict(cr.fetchall())
        return res'''
	
    _columns = {
        'date_value': fields.date('Date', required=True),
        'tours_travle_id': fields.many2one('ids.tours.travels', 'Tours And Travel', ondelete='cascade', select=True),
	    'starting_point': fields.char("Starting Point", size=200, required=True),
	    'travel_to': fields.char("Travel To", size=200, required=True),
	    'travel_mode_id': fields.many2one('ids.travel.mode', 'Mode of Travel', required=True),
        'description': fields.text('Description'),
        'ref': fields.char('Reference', size=32),
        'sequence': fields.integer('Sequence', select=True, help="Gives the sequence order when displaying a list of Tours and Travels lines."),
    }
    
    _defaults = {
        'date_value': lambda *a: time.strftime('%Y-%m-%d'),
    }
    
    _order = "sequence, date_value desc"

class ids_travel_mode(osv.osv):
    
    _name = 'ids.travel.mode'
    _description = "IDS Tours and Travel Mode"

    def name_get(self, cr, uid, ids, context={}):
        """Formatting name and mode. """ 
        if not len(ids):
            return []

        res=[]

        for travelMode in self.browse(cr, uid, ids,context=context):
	        res.append((travelMode.id, travelMode.travel_mode.title() + ' / ' + travelMode.name))	    
	
        return res

    _columns = {
                'name':fields.char('Class ', size=150, required=True),
                'travel_mode': fields.selection(
                                                [
                                                 ('train', 'Train'),
                                                 ('road', 'Road'),
                                                 ('air', 'Air'),
                                                 ('personal', 'Personal'),
                                                 ]
                                                , 'Mode of Travel'),
                }

#####################################################################
#Inherit hr expenses line to create relation for tours and travels module#
#####################################################################
class hr_expense_line(osv.osv):

    _inherit="hr.expense.line"
    _description = "Expense Line"

    _columns = {
	    'is_tour' : fields.boolean('Tours?'),
	    'tour_travel_id' : fields.many2one('ids.tours.travels', 'Tour ID', domain=[('state','=','done')])        
    }

    _default = {
        'is_tour':False	
    }
	


