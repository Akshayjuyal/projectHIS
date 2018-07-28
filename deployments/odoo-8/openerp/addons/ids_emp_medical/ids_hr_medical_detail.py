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
from openerp import netsvc

class ids_hr_medical_detail(osv.osv):    
    _name = 'ids.hr.medical.detail'
    _description = "Employee Medical Detail"           
    _rec_name = 'blood_groups'    
    _columns = {
                'blood_group':fields.char('Please mention your blood group:', size=100),
                'blood_groups':fields.selection([('1','A+'),('2','B+'),('3','A-'),('4','B-'),('5','O+'),('6','O-'),('7','AB+'),('8','AB-')],'Please mention your blood group:'),
                'medicine':fields.boolean('Are you taking any medicine?'),
                'medicine_desc':fields.char('If yes, for what?', size=200),
                'allergies':fields.boolean('Do you have any allergies?'),
                'allergies_desc':fields.char('If yes, for what?', size=200),
                'medicine_allergy':fields.boolean('Are you allergic to any medicine?'),
                'medicine_allergy_desc':fields.char('If yes, for what?', size=200),
                'hospitalized':fields.boolean('Have you ever been hospitalized in last 3 years?'),
                'hospitalized_desc':fields.char('If yes, for what?', size=200),
                'suffer_from_epilepsy':fields.boolean('Epilepsy, fits or convulsion'),
                'suffer_from_tuberculosis':fields.boolean('Tuberculosis'),
                'suffer_from_anemia':fields.boolean('Anemia'),
                'suffer_from_ulcer':fields.boolean('Stomach ulcer, duodenal ulcer(or a peptic ulcer)'),
                'suffer_from_diabetes':fields.boolean('Diabetes'),
                'suffer_from_cancer':fields.boolean('Cancer'),
                'suffer_from_sex':fields.boolean('Sexuality Transmitted Disease'),
                'suffer_from_asthma':fields.boolean('Asthma'),
                'suffer_from_bp':fields.boolean('High Blood Pressure'),
                'suffer_from_heart':fields.boolean('Heart disease'),
                'suffer_from_other':fields.char('Any other disease(describe):', size=1000),
                'expecting_child':fields.boolean('For women only : Are you expecting a child?'),
                'expecting_delivery':fields.date('If Yes, expected date of delivery:'),
                'last_visit_doctor':fields.char('When did you visit your doctor last in this concern?:', size=100),
                'physician_address':fields.text('Please mention your physician name & address:')                                
               }
