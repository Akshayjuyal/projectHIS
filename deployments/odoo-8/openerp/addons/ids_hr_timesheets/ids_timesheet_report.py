import time 
from openerp import SUPERUSER_ID
from openerp import tools
from openerp.osv import fields, osv
from datetime import datetime, date , timedelta
from openerp import exceptions
from openerp.exceptions import Warning



class ids_timesheet_report(osv.osv_memory):
    _name = 'ids.timesheet.report'
    _description = "IDS Timesheet Report"
    _columns = {
                'from_date' :fields.datetime('Date from'),
                'to_date'   :fields.datetime('Date to'),
                'output_type': fields.selection([('pdf', 'Portable Document (pdf)'),
                                                 ('xls', 'Excel Spreadsheet (xls)')],
                                                'Report format', help='Choose the format for the output', required=True),
                }
    
    _defaults = {
                'output_type'    : 'xls',
                }
    
    
    def print_timesheet_report(self, cr, uid, ids, context=None):
        employee_obj = self.pool.get('hr.employee')
        employee_obj1 = self.pool.get('resource.resource')
        print "uid=====================", uid
        cr.execute("select id from hr_employee where id=(select id from resource_resource where user_id=%s)"%uid);
        empid = cr.fetchone()
        print "emp-id============================", empid
        emp_level = employee_obj.search(cr, uid, [('parent_id', '=', empid)], context=context)
        if emp_level:
            if empid:
                emp_level.extend((empid))
        if not emp_level:
            uid = 1
            
        emp_second_level = employee_obj.search(cr, uid, [('parent_id', '=', emp_level)], context=context)
        emp_level.extend((emp_second_level))
        
        emp_third_level = employee_obj.search(cr, uid, [('parent_id', '=', emp_second_level)], context=context)
        emp_level.extend((emp_third_level))
 
        emp_fourth_level = employee_obj.search(cr, uid, [('parent_id', '=', emp_third_level)], context=context)
        emp_level.extend((emp_fourth_level))
        for case in self.browse(cr, uid, ids):
            data = {}
            data['ids'] = context.get('active_ids', [])
            data['model'] = context.get('active_model', 'ir.ui.menu')
            data['output_type'] =  case.output_type
            data['variables'] = {
                                'date_from' : case.from_date or '2016-01-01 00:00:00',
                                'date_to' : case.to_date or time.strftime('%Y-%m-%d %H:%M:%S'), 
                                'uid'         : uid and uid or 1,
                                'empid'       : empid or 0,
                                'emp_level'   : emp_level or 0,
                                'output_type' : case.output_type,
                                }
            print 'data', data
            return {
                    'type': 'ir.actions.report.xml',
                    'report_name':'ids_timesheet_report',
                    'datas':data,
                    }