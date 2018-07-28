from openerp.osv import fields, osv
from datetime import datetime , timedelta
import time
from openerp.tools.translate import _
    
class biometric_data(osv.osv):
    _name = "biometric.data"
    _columns = {
        'name' : fields.datetime('Date Time'),
        'emp_code' : fields.char('Employee Code'),
        'mechine_id' : fields.integer('Mechine No'),
        'flag':fields.boolean('Flag'),
        'status':fields.char('Status')
    }

class biometric_data_mohali(osv.osv):
    _name = "biometric.data.mohali"
    _columns = {
        'name' : fields.datetime('Date Time'),
        'emp_code' : fields.char('Employee Code'),
        'mechine_id' : fields.integer('Mechine No'),
        'flag':fields.boolean('Flag'),
        'status':fields.char('Status')
    }

class biometric_data_noida(osv.osv):
    _name = "biometric.data.noida"
    _columns = {
        'name' : fields.datetime('Date Time'),
        'emp_code' : fields.char('Employee Code'),
        'mechine_id' : fields.integer('Mechine No'),
        'flag':fields.boolean('Flag'),
        'status':fields.char('Status')
    }

    

