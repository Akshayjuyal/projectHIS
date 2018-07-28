{
'name': 'IDS Employee Information Change Request  Module',
'author':'IDS',
'depends':['web','base','mail', 'ids_emp_medical', 'ids_hr_employee_background', 'hr', 'hr_holidays','hr_contract', 'ids_hr_holidays_extension'],
'description':"""IDS Employee Personal Information Change Request """,
'data':[
        'security/ir.model.access.csv',
        'view/ids_emp_change.xml',
        'view/widget.xml',
       ],
       
       
'qweb': ['static/src/xml/custom_widget.xml',],
'installable':True,
'auto_install':False
}
