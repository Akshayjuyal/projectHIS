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

class hr_expense_expense(osv.osv):

    _inherit="hr.expense.expense"

    '''
	This method enable users to modify expense lines view based on their state and groups.
    '''    
    def is_visible(self, cr, uid, ids, name, args, context=None):
        """Make visibilty to certain groups.  """
        result = {}
		
    	users = self.pool.get('res.users')
    	
    	if len(self.browse(cr, uid, ids, context=context)) > 0:
    		self_obj = self.browse(cr, uid, ids, context=context)[0]
    		
    		if users.has_group(cr, uid, 'ids_emp.group_business_head') and self_obj.state == 'accepted_mgr':
    			result[self_obj.id]=False
    		elif users.has_group(cr, uid, 'ids_hr_expenses.group_hr_expenses') and self_obj.state == 'confirm':
    			result[self_obj.id]=False
    		elif users.has_group(cr, uid, 'base.group_user') and self_obj.state == 'draft':
    			result[self_obj.id] = False
    		else:
    			result[self_obj.id] = True
    		del self_obj
    
    	del users
	
	return result

    _columns = {
	    'line_ids': fields.one2many('hr.expense.line', 'expense_id', 'Expense Lines'),
        'state': fields.selection([
            ('draft', 'New'),
            ('cancelled', 'Refused'),
            ('confirm', 'Waiting Approval'),            
            ('accepted_mgr', 'First Approval'),
            ('accepted', 'Approved'),
            ('done', 'Waiting Payment'),
            ('paid', 'Paid'),
            ],
        'Status', readonly=True, track_visibility='onchange',
            help='When the expense request is created the status is \'Draft\'.\n It is confirmed by the user and request is sent to admin, the status is \'Waiting Confirmation\'.\
            \nIf the admin accepts it, the status is \'Accepted\'.\n If the accounting entries are made for the expense request, the status is \'Waiting Payment\'.'),
	    'first_validate_mgr_id': fields.many2one('hr.employee', 'Second Approval', invisible=False, readonly=True, help='This area is automatically filled by the user who approve/validate the resignation at second level'),
	    'inv':fields.function(is_visible, type='boolean', method=True, store=False, string='Visiblility')
    }


    '''
    This method finds default employee in expense. 
    :param cr: DB cursur.
    :param uid: User Id
    :return: 
    '''
    def _default_employee(self, cr, uid, context=None):
        """Get default employee. """
        emp_ids = self.pool.get('hr.employee').search(cr, uid, [('user_id','=',uid)], context=context)
        return emp_ids and emp_ids[0] or False


    '''
	This method is responsible for change workflow state from confirm to accepted_mgr and also write manager id to db.
	:param cr: DB cursur.
    :param uid: User Id
	:param ids: 
	:default param:context:
    :return: 
    '''
    
    def expense_confirm_submit(self, cr, uid, ids, context=None):
        """Workflow initiated- Submit to MANAGER. """
        expense=self.browse(cr, uid, ids, context=None)
        url="http://ids-erp.idsil.loc:8069/web"
        values = {
        'subject': 'Employee Expenses' + '- ' + expense.employee_id.name,
        'body_html': expense.employee_id.name+ ' ' + 'has created the Expenses.Please take necessary action.<br/><br/><br/>Kindly do not reply.<br/>---This is auto generated email---<br/>Regards:<br/>ERP HR Team<br/>IDS Infotech LTD.<br/><br/>Url:'+url,
        'email_to': expense.employee_id.parent_id.work_email,
        'email_from': 'info.openerp@idsil.com',
          }
        #---------------------------------------------------------------
        mail_obj = self.pool.get('mail.mail') 
        msg_id = mail_obj.create(cr, uid, values, context=context) 
        if msg_id: 
            mail_obj.send(cr, uid, [msg_id], context=context)
        
        return self.write(cr, uid, ids, {'state': 'confirm', 'date_confirm': time.strftime('%Y-%m-%d')}, context=context)
    
    def expense_accept(self, cr, uid, ids, context=None):
        """Expenses accepted by manager and submit to HOD. """
        expense=self.browse(cr, uid, ids, context=None)
        url="http://ids-erp.idsil.loc:8069/web"
        values = {
        'subject': 'Employee Expenses' + '- ' + expense.employee_id.name,
        'body_html':  'The Expenses created by'+' '+expense.employee_id.name+ ' ' + 'has Approved.<br/><br/><br/>Kindly do not reply.<br/>---This is auto generated email---<br/>Regards:<br/>ERP HR Team<br/>IDS Infotech LTD.<br/><br/>Url:'+url,
        'email_to': expense.employee_id.parent_id.work_email,
        'email_cc': expense.employee_id.work_email, 
        'email_from': 'info.openerp@idsil.com',
          }
        #---------------------------------------------------------------
        mail_obj = self.pool.get('mail.mail') 
        msg_id = mail_obj.create(cr, uid, values, context=context) 
        if msg_id: 
            mail_obj.send(cr, uid, [msg_id], context=context)
        
        return self.write(cr, uid, ids, {'state': 'accepted', 'date_valid': time.strftime('%Y-%m-%d'), 'user_valid': uid}, context=context)

    
    
    def expense_accept_by_mgr(self, cr, uid, ids, context=None):
        """Expenses acceptd by HOD. """
        expense=self.browse(cr, uid, ids, context=None)
        url="http://ids-erp.idsil.loc:8069/web"
        values = {
        'subject': 'Employee Expenses' + ' -' + expense.employee_id.name,
        'body_html':  'The Expenses created by'+' '+expense.employee_id.name+ ' ' + 'has Approved for First Approval.<br/><br/><br/>Kindly do not reply.<br/>---This is auto generated email---<br/>Regards:\nERP HR Team\nIDS Infotech LTD.\nUrl:'+url,
        'email_to': expense.employee_id.parent_id.parent_id.work_email,
        'email_cc': expense.employee_id.work_email, 
        'email_from': 'info.openerp@idsil.com',
          }
        #---------------------------------------------------------------
        mail_obj = self.pool.get('mail.mail') 
        msg_id = mail_obj.create(cr, uid, values, context=context) 
        if msg_id: 
            mail_obj.send(cr, uid, [msg_id], context=context)
        
        return self.write(cr, uid, ids, {'state': 'accepted_mgr','first_validate_mgr_id': self._default_employee(cr, uid, context), 'date_valid': time.strftime('%Y-%m-%d'), 'user_valid': uid}, context=context)
    
    def expense_canceled(self, cr, uid, ids, context=None):
        """In case, Expenses canceled.  """
        expense=self.browse(cr, uid, ids, context=None)
        url="http://ids-erp.idsil.loc:8069/web"
        values = {
        'subject': 'Employee Expenses' + '- ' + expense.employee_id.name,
        'body_html':  'The Expenses created by'+' '+expense.employee_id.name+ ' ' + 'has Refused.<br/><br/><br/>Kindly do not reply.<br/>---This is auto generated email---<br/>Regards:<br/>ERP HR Team<br/>IDS Infotech LTD.<br/>Url:'+url,
        'email_to': expense.employee_id.parent_id.work_email,
        'email_cc': expense.employee_id.work_email, 
        'email_from': 'info.openerp@idsil.com',
          }
        #---------------------------------------------------------------
        mail_obj = self.pool.get('mail.mail') 
        msg_id = mail_obj.create(cr, uid, values, context=context) 
        if msg_id: 
            mail_obj.send(cr, uid, [msg_id], context=context)
        
        return self.write(cr, uid, ids, {'state': 'cancelled'}, context=context)
    
