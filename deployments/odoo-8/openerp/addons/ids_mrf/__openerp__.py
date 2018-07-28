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
{
'name': 'IDS MRF Module',
'author':'IDS OpenERP Team',
'depends':['base','hr','hr_recruitment','ids_emp'],
'description':"""MRF module for recruitment process""",
'data':['view/ids_mrf_view.xml',
        'view/mrf_number_sequence_view.xml',
  #      'workflow/ids_mrf_workflow_view.xml',
        'security/user_groups.xml',
#        'security/ir_rule.xml',        
        'security/ir.model.access.csv'
],
'installable':True,
'auto_install':False
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
