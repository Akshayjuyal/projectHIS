# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2015 Medma - http://www.medma.net
#    All Rights Reserved.
#    Medma Infomatix (info@medma.net)
#
#    Coded by: 
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

from openerp.osv import osv, orm, fields
from openerp.addons.base.ir.ir_qweb import HTMLSafe
from datetime import datetime, timedelta, time
from openerp.tools.translate import _

class hr_employee(osv.osv):
    _inherit = 'hr.employee'

   
    def send_birthday_email(self, cr, uid, ids=None, context=None):
        emp_obj = self.pool.get('hr.employee')
        temp_obj = self.pool.get('email.template')
        group_obj = self.pool.get('mail.group')
        wish_template_id = self.pool['ir.model.data'].get_object_reference(cr, uid, 'birthday_wish', 'email_template_birthday_wish')[1]
        group_id = self.pool['ir.model.data'].get_object_reference(cr, uid, 'birthday_wish', 'group_birthday')[1]
        today = datetime.now()
        today_month_day = '%-' + today.strftime('%m') + '-' + today.strftime('%d')
        emp_ids = emp_obj.search(cr, uid, [('birthday', 'like', today_month_day)])
        if emp_ids:
            for emp_id in emp_obj.browse(cr, uid, emp_ids,context=context):
                if emp_id.work_email:
                    temp_obj.send_mail(cr, uid, emp_id.company_id.birthday_mail_template and emp_id.company_id.birthday_mail_template.id or wish_template_id,
                                   emp_id.id, force_send=True, context=context)
                group_obj.message_post(cr, uid, group_id, body=_('Happy Birthday Dear %s.') % (emp_id.name_related), emp_ids=[emp_id.id], context=context)
                self.message_post(cr, uid, emp_id.id, body=_('Happy Birthday.'), context=context)
        return None
