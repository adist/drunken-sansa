'''
Created on Feb 18, 2015

@author: adista@bizoft
'''
from openerp.osv import fields, osv

class hr_employee_category(osv.osv):
    _inherit = 'hr.employee.category'
    _columns = {
        'code' : fields.char(string='Kode'), 
        'type' : fields.selection([('area', 'Area'), ('unitup', 'Unit Up')], string='Tipe', required=True),  
    }
    
    def name_get(self, cr, uid, ids, context=None):
        res = super(hr_employee_category, self).name_get(cr, uid, ids, context=context)
        res = dict(res)
        for this in self.browse(cr, uid, res.keys()):
            if not this.parent_id:
                continue
            res[this.id] = this.code and ' - '.join([this.code, res[this.id]]) or res[this.id]
        return res.items()
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        ids = self.search(cr, user, [('code', operator, name)] + args, limit=limit, context=context)
        ids += self.search(cr, user, [('name', operator, name)] + args, limit=limit, context=context)
        return self.name_get(cr, user, ids, context)
hr_employee_category()

class hr_employee(osv.osv):
    _inherit = 'hr.employee'
    
    def create(self, cr, uid, vals, context={}):
        res = super(hr_employee, self).create(cr, uid, vals, context={})
        if not res:
            return res
        category_ids = vals['category_ids'][0][-1]
        if len(category_ids) != 1:
            raise 
        o_hr_categ = self.pool.get('hr.employee.category').browse(cr, uid, category_ids[-1])
        user_vals = {
            'name' : vals['name'], 
            'login' : '_'.join([str(o_hr_categ.code).lower(), vals['name'].lower()]), 
            'password' : ''.join([vals['name'].lower(),'123']), 
            'employee' : True, 
        }
        o_user = self.pool.get('res.users').create(cr, uid, user_vals, context=context)
        self.write(cr, uid, [res], {'user_id' : o_user}, context=context)
        return res
hr_employee()