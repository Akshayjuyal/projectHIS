# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################
from openerp import api, tools
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.addons.report_xls.report_xls import report_xls
import xlwt
import datetime
import unicodedata
import base64
import StringIO
import csv, cStringIO
from datetime import datetime

class HrEmployeeExcelReport(osv.osv):
    
    _name = 'hr.employee.excel.report'
    _description = 'HR Employee Excel Report'

    _columns = {
    'company_id' : fields.many2one('res.company','Company',required=True),
    'status':fields.selection([('Existing','Existing'),('Left','Left')],'Status' ),
    'division_id':fields.many2one('division','Division'),

    }
    
    #@api.multi
    def genarate_excel_report(self, cr, uid, ids, context=None):
        custom_value = {}                 
        emp_obj = self.pool.get('hr.employee')
        workbook = xlwt.Workbook()
        
        
        #Style for Excel
        xlwt.add_palette_colour("custom_colour", 0x21)
        xlwt.add_palette_colour("custom_colour1", 0x22)
        workbook.set_colour_RGB(0x21, 155, 187, 89)
        workbook.set_colour_RGB(0x22, 255, 160, 122)
        
        styles0 = xlwt.easyxf('pattern: pattern solid, fore_colour custom_colour;align: horiz center;', num_format_str='#,##0.00')
        styles1 = xlwt.easyxf('pattern: pattern solid, fore_colour custom_colour1;align: horiz center;', num_format_str='#,##0.00')
        style00 = xlwt.easyxf('pattern: pattern solid, fore_colour yellow;align: horiz left;', num_format_str='#,##0.00')
        style0 = xlwt.easyxf('font: name Times New Roman bold on;align: horiz left;', num_format_str='#,##0.00')
        style1 = xlwt.easyxf('font: name Times New Roman bold on; pattern: pattern solid, fore_colour black;align: horiz center;', num_format_str='#,##0.00')
        style2 = xlwt.easyxf('font:height 400,bold True; pattern: pattern solid, fore_colour black;', num_format_str='#,##0.00')         
        style3 = xlwt.easyxf('font:bold True;', num_format_str='#,##0.00')
        style4 = xlwt.easyxf('font:bold True;  borders:top double;align: horiz right;', num_format_str='#,##0.00')
        style5 = xlwt.easyxf('font: name Times New Roman bold on;align: horiz center;', num_format_str='#,##0')
        style6 = xlwt.easyxf('font: name Times New Roman bold on;', num_format_str='#,##0.00')
        style7 = xlwt.easyxf('font:bold True;  borders:top double;', num_format_str='#,##0.00')

        #Excel Heading Manipulation
                
        sheet = workbook.add_sheet("Employee List")
        sheet.write_merge(0,0,36,49,'Communication Details', styles1)
        sheet.write_merge(0,0,60,77,'Academic Summary', styles1)
        sheet.write_merge(0,0,78,105,'Professional Summary', styles0)
        sheet.write_merge(0,0,106,144,'Salary Summary', styles0)
        
        sheet.write_merge(1,1,0,7,'Personal Information', styles0)
        sheet.write_merge(1,1,8,32,'Job Details', styles1)
        sheet.write_merge(1,1,33,35,'Reporting Person Details', styles0)
        sheet.write_merge(1,1,36,37,'Contact Details', styles1)
        sheet.write_merge(1,1,38,40,'Present Address Details', styles1)
        sheet.write_merge(1,1,41,43,'Permanent Details', styles1)
        sheet.write_merge(1,1,44,49,'Emergency Details', styles1)
        sheet.write_merge(1,1,50,59,'KYC Information', styles0)
        sheet.write_merge(1,1,60,63,'Secondary Qualification', styles1)
        sheet.write_merge(1,1,64,67,'Sr. Secondary Qualification', styles1)
        sheet.write_merge(1,1,68,71,'Graduation', styles1)
        sheet.write_merge(1,1,72,75,'Post Graduation', styles1)
        sheet.write_merge(1,1,76,77,'Professional', styles1)
        sheet.write_merge(1,1,78,82,'Experience_1', styles0)
        sheet.write_merge(1,1,83,87,'Experience_2', styles0)
        sheet.write_merge(1,1,88,92,'Experience_3', styles0)
        sheet.write_merge(1,1,93,97,'Experience_4', styles0)
        sheet.write_merge(1,1,98,102,'Experience_5', styles0)
        sheet.write_merge(1,1,103,105,'Experience_Other', styles0)
        sheet.write_merge(1,1,106,113,'Appraisal Information', styles1)
        sheet.write_merge(1,1,114,144,'Salary Structure', styles0)
        sheet.write_merge(1,1,145,147,'Separation Detail', styles1)
        
        
        
        
        sheet.write(2,0,'Code', style00)
        sheet.write(2,1,'Name', style00)
        sheet.write(2,2,'Father Name', style00)
        sheet.write(2,3,'Gender', style00)
        sheet.write(2,4,'DOB', style00)
        sheet.write(2,5,'Marital Status', style00)
        sheet.write(2,6,'Spouse Name', style00)
        sheet.write(2,7,'DOM', style00)
        sheet.write(2,9,'DOJ', style00)
        sheet.write(2,8,'Division', style00)
        sheet.write(2,10,'Department', style00)
        sheet.write(2,11,'Project', style00)
        sheet.write(2,12,'Designation', style00)
        sheet.write(2,13,'Grade', style00)
        sheet.write(2,14,'Location', style00)
        sheet.write(2,15,'DOC', style00)
        sheet.write(2,16,'Confirmation Status', style00)
        sheet.write(2,17,'PF Status', style00)
        sheet.write(2,18,'PF No.', style00)
        sheet.write(2,19,'ESI Status', style00)
        sheet.write(2,20,'ESI No.', style00)
        sheet.write(2,21,'GMI Status', style00)
        sheet.write(2,22,'GMI No.', style00)
        sheet.write(2,23,'UAN No.', style00)
        sheet.write(2,24,'Contract End Date', style00)
        
        sheet.write(2,25,'Agreement Status', style00)
        sheet.write(2,26,'Agreement Start', style00)
        sheet.write(2,27,'Agreement End', style00)
        sheet.write(2,28,'Functional Category', style00)
        sheet.write(2,29,'Role Category', style00)
        sheet.write(2,30,'Billing Category', style00)
        sheet.write(2,31,'MRF Date', style00)
        sheet.write(2,32,'LOI Date', style00)
        sheet.write(2,33,'Reporting Manger Id', style00)
        sheet.write(2,34,'Reporting Manger Name', style00)
        sheet.write(2,35,'Reporting Manager Designation', style00)
        sheet.write(2,36,'Mobile', style00)
        sheet.write(2,37,'Email ID', style00)
        sheet.write(2,38,'Local Address', style00)
        sheet.write(2,39,'Local Pin', style00)
        sheet.write(2,40,'Local Contact No.', style00)
        sheet.write(2,41,'Address', style00)
        sheet.write(2,42,'Pin', style00)
        sheet.write(2,43,'Contact', style00)
        sheet.write(2,44,'Name', style00)
        sheet.write(2,45,'Relation', style00)
        sheet.write(2,46,'Address', style00)
        sheet.write(2,47,'Pin', style00)
        sheet.write(2,48,'Contact', style00)
        sheet.write(2,49,'Blood Group', style00)
        sheet.write(2,50,'Pan No.', style00)
        
        sheet.write(2,51,'Bank A/c No.', style00)
        sheet.write(2,52,'Bank Name', style00)
        sheet.write(2,53,'Aadhaar No.', style00)
        sheet.write(2,54,'Election Card No.', style00)
        sheet.write(2,55,'Driving License No.', style00)
        sheet.write(2,56,'Ration Card No.', style00)
        sheet.write(2,57,'Passport No.', style00)
        sheet.write(2,58,'Passport Issued Date', style00)
        sheet.write(2,59,'Passport Expiry Date', style00)
        sheet.write(2,60,'M stream.', style00)
        sheet.write(2,61,'Passing Yr', style00)
        sheet.write(2,62,'%age', style00)
        sheet.write(2,63,'M board', style00)
        sheet.write(2,64,'I stream.', style00)
        sheet.write(2,65,'Passing Yr', style00)
        sheet.write(2,66,'%age', style00)
        sheet.write(2,67,'board', style00)
        sheet.write(2,68,'G stream.', style00)
        sheet.write(2,69,'Passing Yr', style00)
        sheet.write(2,70,'%age', style00)
        sheet.write(2,71,'Univ.', style00)
        sheet.write(2,72,'pg_stream.', style00)
        sheet.write(2,73,'Passing Yr', style00)
        sheet.write(2,74,'%age', style00)
        sheet.write(2,75,'Univ.', style00)
        sheet.write(2,76,'Other', style00)
        sheet.write(2,77,'Qualification Category', style00)
        sheet.write(2,78,'Company', style00)
        sheet.write(2,79,'Designation', style00)
        sheet.write(2,80,'From', style00)
        sheet.write(2,81,'To', style00)
        sheet.write(2,82,'Salary', style00)
        
        sheet.write(2,83,'Company', style00)
        sheet.write(2,84,'Designation', style00)
        sheet.write(2,85,'From', style00)
        sheet.write(2,86,'To', style00)
        sheet.write(2,87,'Salary', style00)
        
        sheet.write(2,88,'Company', style00)
        sheet.write(2,89,'Designation', style00)
        sheet.write(2,90,'From', style00)
        sheet.write(2,91,'To', style00)
        sheet.write(2,92,'Salary', style00)
        
        sheet.write(2,93,'Company', style00)
        sheet.write(2,94,'Designation', style00)
        sheet.write(2,95,'From', style00)
        sheet.write(2,96,'To', style00)
        sheet.write(2,97,'Salary', style00)
        
        sheet.write(2,98,'Company', style00)
        sheet.write(2,99,'Designation', style00)
        sheet.write(2,100,'From', style00)
        sheet.write(2,101,'To', style00)
        sheet.write(2,102,'Salary', style00)
        
        sheet.write(2,103,'Total Experience', style00)
        sheet.write(2,104,'Previous Experience', style00)
        sheet.write(2,105,'IDS Experience', style00)
        
        sheet.write(2,106,'Appr_Category', style00)
        sheet.write(2,107,'Appr_Cycle', style00)
        sheet.write(2,108,'Appr_Status', style00)
        sheet.write(2,109,'Last Rev. Date', style00)
        sheet.write(2,110,'Last Rev. Comment', style00)
        sheet.write(2,111,'Mid Rev. date', style00)
        sheet.write(2,112,'Mid Rev. Comment', style00)
        sheet.write(2,113,'New Rev. Date', style00)
        
        sheet.write(2,114,'Last Salary', style00)
        sheet.write(2,115,'TCTC', style00)
        sheet.write(2,116,'CTC', style00)
        sheet.write(2,117,'Basic', style00)
        sheet.write(2,118,'HRA', style00)
        sheet.write(2,119,'CCA', style00)
        sheet.write(2,120,'TA', style00)
        sheet.write(2,121,'Special', style00)
        sheet.write(2,122,'Gross', style00)
        sheet.write(2,123,'ESI EMP', style00)
        sheet.write(2,124,'ESI COMP', style00)
        sheet.write(2,125,'PF EMP', style00)
        sheet.write(2,126,'PF COMP', style00)
        sheet.write(2,127,'MR', style00)
        sheet.write(2,128,'MV', style00)
        sheet.write(2,129,'Bonus', style00)
        sheet.write(2,130,'Variable', style00)
        sheet.write(2,131,'LTA', style00)
        sheet.write(2,132,'Loyalty Bonus', style00)
        sheet.write(2,133,'Telephone', style00)
        sheet.write(2,134,'Conveyance', style00)
        sheet.write(2,135,'Magazine', style00)
        sheet.write(2,136,'NPS', style00)
        sheet.write(2,137,'Gratuity', style00)
        sheet.write(2,138,'GMI', style00)
        sheet.write(2,139,'GPA', style00)
        sheet.write(2,140,'Term  Insurance', style00)
        sheet.write(2,141,'Fixed', style00)
        sheet.write(2,142,'Variable', style00)
        sheet.write(2,143,'Benefit', style00)
        sheet.write(2,144,'Total', style00)
        sheet.write(2,145,'Date Of Resignation', style00)
        sheet.write(2,146,'Date Of Leaving', style00)
        sheet.write(2,147,'Reason Of Leaving', style00)

        row = 3
        for report in self.browse(cr,uid,ids,context=context):
            if report.status=='Existing' and report.division_id:
                emp=emp_obj.search(cr,uid,[('company_id','=',report.company_id.id),('active','=',True),('division','=',report.division_id.id)])
            if report.status=='Existing' and not report.division_id:
                emp=emp_obj.search(cr,uid,[('company_id','=',report.company_id.id),('active','=',True)])
            if report.status=='Left' and report.division_id:
                emp=emp_obj.search(cr,uid,[('company_id','=',report.company_id.id),('active','=',False),('division','=',report.division_id.id)])
            if report.status=='Left' and not report.division_id:
                emp=emp_obj.search(cr,uid,[('company_id','=',report.company_id.id),('active','=',False)])
            for rec in emp_obj.browse(cr,uid,emp,context=context):
                name1=name2=name3=name4=name5=''
                position1=position2=position3=position4=position5=''
                j_date1=j_date2=j_date3=j_date4=j_date5=''
                l_date1=l_date2=l_date3=l_date4=l_date5=''
                salary1=salary2=salary3=salary4=salary5=0
                count=0
                for exp in self.pool.get('ids.hr.employment.detail').search(cr,uid,[('employee_id','=',rec.id)]):
                    for exp_data in self.pool.get('ids.hr.employment.detail').browse(cr,uid,exp,context=context):
                        if count==0:
                            name1=exp_data.name
                            position1=exp_data.position
                            j_date1=exp_data.joining_date
                            l_date1=exp_data.leaving_date
                            salary1=exp_data.salary
                        if count==1:
                            name2=exp_data.name
                            position2=exp_data.position
                            j_date2=exp_data.joining_date
                            l_date2=exp_data.leaving_date
                            salary2=exp_data.salary
                        if count==2:
                            name3=exp_data.name
                            position3=exp_data.position
                            j_date3=exp_data.joining_date
                            l_date3=exp_data.leaving_date
                            salary3=exp_data.salary
                        if count==3:
                            name4=exp_data.name
                            position4=exp_data.position
                            j_date4=exp_data.joining_date
                            l_date4=exp_data.leaving_date
                            salary4=exp_data.salary
                        if count==4:
                            name5=exp_data.name
                            position5=exp_data.position
                            j_date5=exp_data.joining_date
                            l_date5=exp_data.leaving_date
                            salary5=exp_data.salary
                        count=count+1
                stream1=stream2=stream3=stream4=stream5=''
                year1=year2=year3=year4=''
                marks1=marks2=marks3=marks4=''
                board1=board2=board3=board4=''
                for edu in self.pool.get('ids.hr.education.detail').search(cr,uid,[('employee_id','=',rec.id),('category','=','matric')]):
                    for edu_data in self.pool.get('ids.hr.education.detail').browse(cr,uid,edu,context=context):
                        stream1=edu_data.course_id.name
                        year1=edu_data.year
                        marks1=edu_data.marks
                        board1=edu_data.board_id.name
                for edu in self.pool.get('ids.hr.education.detail').search(cr,uid,[('employee_id','=',rec.id),('category','=','senior_secondary')]):
                    for edu_data in self.pool.get('ids.hr.education.detail').browse(cr,uid,edu,context=context):
                        stream2=edu_data.course_id.name
                        year2=edu_data.year
                        marks2=edu_data.marks
                        board2=edu_data.board_id.name
                for edu in self.pool.get('ids.hr.education.detail').search(cr,uid,[('employee_id','=',rec.id),('category','=','graduate')],limit=1):
                    for edu_data in self.pool.get('ids.hr.education.detail').browse(cr,uid,edu,context=context):
                        stream3=edu_data.course_id.name
                        year3=edu_data.year
                        marks3=edu_data.marks
                        board3=edu_data.board_id.name
                for edu in self.pool.get('ids.hr.education.detail').search(cr,uid,[('employee_id','=',rec.id),('category','=','post_graduate')],limit=1):
                    for edu_data in self.pool.get('ids.hr.education.detail').browse(cr,uid,edu,context=context):
                        stream4=edu_data.course_id.name
                        year4=edu_data.year
                        marks4=edu_data.marks
                        board4=edu_data.board_id.name
                for edu in self.pool.get('ids.hr.education.detail').search(cr,uid,[('employee_id','=',rec.id),('category','=','other')],limit=1):
                    for edu_data in self.pool.get('ids.hr.education.detail').browse(cr,uid,edu,context=context):
                        stream5=edu_data.course_id.name
                emergency = self.pool.get('ids.hr.emergency.detail').search(cr,uid,[('employee_id','=',rec.id)],limit=1)
                emergency_data = self.pool.get('ids.hr.emergency.detail').browse(cr,uid,emergency,context=context)
                resign = self.pool.get('ids.hr.employee.separation').search(cr,uid,[('employee_id','=',rec.id)])
                resign_data = self.pool.get('ids.hr.employee.separation').browse(cr,uid,resign,context=context)
                blood_group=''
                if rec.blood_groups=='1':
                    blood_group='A+'
                elif rec.blood_groups=='2':
                    blood_group='B+'
                elif rec.blood_groups=='3':
                    blood_group='A-'
                elif rec.blood_groups=='4':
                    blood_group='B-'
                elif rec.blood_groups=='5':
                    blood_group='O+'
                elif rec.blood_groups=='6':
                    blood_group='O-'
                elif rec.blood_groups=='7':
                    blood_group='AB+'
                else:
                    blood_group='AB-'
                                                                              
                sheet.write(row, 0, rec.emp_code , style0)
                sheet.write(row, 1, rec.name, style0)
                sheet.write(row, 2, rec.father_name or '', style0)
                sheet.write(row, 3, rec.gender or '', style0)
                sheet.write(row, 4, rec.birthday or '0000-00-00', style0)
                sheet.write(row, 5, rec.marital or '', style0)
                sheet.write(row, 6, rec.spouse_name or '', style0)
                sheet.write(row, 7, rec.marriage_date or '0000-00-00', style0)
                sheet.write(row, 8, rec.division.name, style0)
                sheet.write(row, 9, rec.joining_date or '0000-00-00', style0)
                sheet.write(row, 10, rec.department_id.name, style0)
                sheet.write(row, 11, rec.team_id.name, style0)
                sheet.write(row, 12, rec.job_id.name, style0)
                sheet.write(row, 13, rec.grade_id.name, style0)
                sheet.write(row, 14, rec.office_location.name, style0)
                sheet.write(row, 15, rec.confirmation_date, style0)
                sheet.write(row, 16, rec.confirmation_status, style0)
                sheet.write(row, 17, rec.pf_status or '', style0)
                sheet.write(row, 18, rec.pf_no or '', style0)
                sheet.write(row, 19, rec.esi_status or '', style0)
                sheet.write(row, 20, rec.esi_no or '', style0)
                sheet.write(row, 21, rec.gmi_status or '', style0)
                sheet.write(row, 22, rec.gmi_no or '', style0)
                sheet.write(row, 23, rec.uan_no or '', style0)
                sheet.write(row, 24, rec.end_date or '0000-00-00', style0)
                sheet.write(row, 25, rec.service_agreement or '', style0)
                sheet.write(row, 26, rec.agreement_start_date or '0000-00-00', style0)
                sheet.write(row, 27, rec.agreement_end_date or '0000-00-00', style0)
                sheet.write(row, 28, rec.job_category or '', style0)
                sheet.write(row, 29, rec.role_category or '', style0)
                sheet.write(row, 30, rec.billing_category or '', style0)
                sheet.write(row, 31, rec.mrf_date or '0000-00-00', style0)
                sheet.write(row, 32, rec.loi_date or '0000-00-00', style0)
                sheet.write(row, 33, rec.parent_id.emp_code, style0)
                sheet.write(row, 34, rec.parent_id.name, style0)
                sheet.write(row, 35, rec.parent_id.job_id.name, style0)
                sheet.write(row, 36, rec.mobile_phone or '', style0)
                sheet.write(row, 37, rec.work_email or '', style0)
                sheet.write(row, 38, rec.current_address or '', style0)
                sheet.write(row, 39, rec.current_pin or '', style0)
                sheet.write(row, 40, rec.curent_contact or '', style0)
                sheet.write(row, 41, rec.permanent_address or '', style0)
                sheet.write(row, 42, rec.permanent_pin or '', style0)
                sheet.write(row, 43, rec.permanent_contact or '', style0)
                if emergency:
                    sheet.write(row, 44, emergency_data.name  or '', style0)
                    sheet.write(row, 45, emergency_data.relation  or '', style0)
                    sheet.write(row, 46, emergency_data.emergency_address  or '', style0)
                    sheet.write(row, 47, emergency_data.emerg_pin or '', style0)
                    sheet.write(row, 48, emergency_data.mobile or '', style0)
                    sheet.write(row, 49, blood_group or '', style0)
                sheet.write(row, 50, rec.pan_id or '', style0)
                sheet.write(row, 51, rec.bank_account_id.acc_number or '', style0)
                sheet.write(row, 52, rec.bank_account_id.bank.name or '', style0)
                sheet.write(row, 53, rec.aadhar_card_no or '', style0)
                sheet.write(row, 54, rec.voter_card_no or '', style0)
                sheet.write(row, 55, rec.driving_license_no or '', style0)
                sheet.write(row, 56, rec.ration_card_no or '', style0)
                sheet.write(row, 57, rec.passport_id or '', style0)
                sheet.write(row, 58, rec.passport_issue_date or '0000-00-00', style0)
                sheet.write(row, 59, rec.passport_expiry_date or '0000-00-00', style0)
                sheet.write(row, 60, stream1 or '', style0)
                sheet.write(row, 61, year1 or '', style0)
                sheet.write(row, 62, marks1 or '', style0)
                sheet.write(row, 63, board1 or '', style0)
                sheet.write(row, 64, stream2 or '', style0)
                sheet.write(row, 65, year2 or '', style0)
                sheet.write(row, 66, marks2 or '', style0)
                sheet.write(row, 67, board2 or '', style0)
                sheet.write(row, 68, stream3 or '', style0)
                sheet.write(row, 69, year3 or '', style0)
                sheet.write(row, 70, marks3 or '', style0)
                sheet.write(row, 71, board3 or '', style0)
                sheet.write(row, 72, stream4 or '', style0)
                sheet.write(row, 73, year4 or '', style0)
                sheet.write(row, 74, marks4 or '', style0)
                sheet.write(row, 75, board4 or '', style0)
                sheet.write(row, 76, stream5 or '', style0)
                sheet.write(row, 77, rec.education_category or '', style0)
                
                sheet.write(row, 78, name1 , style0)
                sheet.write(row, 79, position1, style0)
                sheet.write(row, 80, j_date1, style0)
                sheet.write(row, 81, l_date1, style0)
                sheet.write(row, 82, salary1, style0)
                sheet.write(row, 83, name2, style0)
                sheet.write(row, 84, position2, style0)
                sheet.write(row, 85, j_date2, style0)
                sheet.write(row, 86, l_date2, style0)
                sheet.write(row, 87, salary2, style0)
                sheet.write(row, 88, name3, style0)
                sheet.write(row, 89, position3, style0)
                sheet.write(row, 90, j_date3, style0)
                sheet.write(row, 91, l_date3, style0)
                sheet.write(row, 92, salary3, style0)
                sheet.write(row, 93, name4, style0)
                sheet.write(row, 94, position4, style0)
                sheet.write(row, 95, j_date4, style0)
                sheet.write(row, 96, l_date4, style0)
                sheet.write(row, 97, salary4, style0)
                sheet.write(row, 98, name5, style0)
                sheet.write(row, 99, position5, style0)
                sheet.write(row, 100, j_date5, style0)
                sheet.write(row, 101, l_date5, style0)
                sheet.write(row, 102, salary5, style0)
#                 sheet.write(row, 103, rec.passport_id, style0)
#                 sheet.write(row, 104, rec.passport_id, style0)
#                 sheet.write(row, 105, rec.passport_id, style0)
#                 sheet.write(row, 106, rec.passport_id, style0)
                sheet.write(row, 107, rec.contract_id.cycle or '', style0)
                sheet.write(row, 108, rec.contract_id.anniversary_status or '', style0)
                sheet.write(row, 109, rec.contract_id.last_revision or '', style0)
                sheet.write(row, 110, rec.contract_id.last_remark or '', style0)
                sheet.write(row, 111, rec.contract_id.mid_revision or '', style0)
                sheet.write(row, 112, rec.contract_id.mid_remark or '', style0)
                sheet.write(row, 113, rec.contract_id.next_revision or '', style0)
                sheet.write(row, 114, rec.contract_id.last_tctc, style0)
                sheet.write(row, 115, rec.contract_id.current_tctc, style0)
                sheet.write(row, 116, rec.contract_id.tct, style0)
                sheet.write(row, 117, rec.contract_id.basic, style0)
                sheet.write(row, 118, rec.contract_id.hra, style0)
                sheet.write(row, 119, rec.contract_id.cca, style0)
                sheet.write(row, 120, rec.contract_id.ta, style0)
                sheet.write(row, 121, rec.contract_id.sa, style0)
                sheet.write(row, 122, rec.contract_id.total, style0)
                sheet.write(row, 123, rec.contract_id.esi, style0)
                sheet.write(row, 124, rec.contract_id.deduction_esi, style0)
                sheet.write(row, 125, rec.contract_id.pf, style0)
                sheet.write(row, 126, rec.contract_id.pf_deduction, style0)
                sheet.write(row, 127, rec.contract_id.medical, style0)
                sheet.write(row, 128, rec.contract_id.meal, style0)
                sheet.write(row, 129, rec.contract_id.bonus, style0)
                sheet.write(row, 130, rec.contract_id.perf_variable, style0)
                sheet.write(row, 131, rec.contract_id.ltc, style0)
                sheet.write(row, 132, rec.contract_id.lb, style0)
                sheet.write(row, 133, rec.contract_id.landline_internet, style0)
                sheet.write(row, 134, rec.contract_id.conveyance, style0)
                sheet.write(row, 135, rec.contract_id.magazine, style0)
                sheet.write(row, 136, rec.contract_id.nps, style0)
                sheet.write(row, 137, rec.contract_id.gratuity, style0)
                sheet.write(row, 138, rec.contract_id.group_medical, style0)
                sheet.write(row, 139, rec.contract_id.group_personal, style0)
                sheet.write(row, 140, rec.contract_id.group_term, style0)
                sheet.write(row, 141, rec.contract_id.tct, style0)
                sheet.write(row, 142, rec.contract_id.variable_amount_pm, style0)
                #sheet.write(row, 143, rec.contract_id.magazine, style0)
                sheet.write(row, 144, rec.contract_id.salary, style0)
                sheet.write(row, 145, resign_data.capture_date or '0000-00-00', style0)
                sheet.write(row, 146, resign_data.last_date or '0000-00-00', style0)
                sheet.write(row, 147, resign_data.reason.name or '', style0)
                
                
                
                
                row +=1

        workbook.save('/tmp/employee_summary.xls')
        result_file = open('/tmp/employee_summary.xls','rb').read()
        attach_id = self.pool.get('wizard.excel.report').create(cr,uid,{
                                        'name':'Employee Summary.xls',
                                        'report':base64.encodestring(result_file)
                    })
        return {
            'name': _('Notification'),
            'context': context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'wizard.excel.report',
            'res_id':attach_id,
            'data': None,
            'type': 'ir.actions.act_window',
            'target':'new'
        }
                
class WizardExcelReport(osv.osv):
    _name = "wizard.excel.report"
    
    _columns = {
                
    'report' : fields.binary('Prepared file',filters='.xls', readonly=True),
    'name' : fields.char('File Name', size=32),
    
    }
