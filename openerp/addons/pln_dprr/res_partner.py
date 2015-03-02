'''
Created on 2015-02-18 22:11

@author: adista@bizoft
'''
from openerp.osv import osv, fields

class pln_golongan_tarif(osv.osv):
    _name = 'pln.golongan_tarif'
    _description = 'Golongan Tarif'
    _columns = {
        'sequence' : fields.integer(string='Urutan'), 
        'code' : fields.char(string='Kode'), 
        'name' : fields.char(string='Nama'), 
    }
pln_golongan_tarif()

class pln_daya(osv.osv):
    _name = 'pln.daya'
    _description = 'Daya'
    _columns = {
        'sequence' : fields.integer(string='Urutan'), 
        'code' : fields.char(string='Kode'), 
        'name' : fields.char(string='Daya'), 
    }
pln_daya()

class res_partner(osv.osv):
    _inherit = 'res.partner'
    
    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        res = super(res_partner,self).name_search(cr, uid, name, args, operator=operator, context=context, limit=limit)
        res = dict(res)
        ids = self.search(cr, uid, [('ref', operator, name), ['id', 'not in', res.keys()]] + args, limit=limit, context=context)
        ids += self.search(cr, uid, [('name', operator, name), ['id', 'not in', res.keys()]] + args, limit=limit, context=context)
        return self.name_get(cr, uid, res.keys() + ids, context=context)

    def name_get(self, cr, uid, ids, context=None):
        res = super(res_partner, self).name_get(cr, uid, ids, context=None)
        res = dict(res)
        for this in self.browse(cr, uid, res.keys()):
            name = this.ref and ' - '.join([this.ref, res[this.id]]) or res[this.id]
            res[this.id] = name 
        return res.items()
    
    def _get_no_ba(self, cr, uid, ids, fields_name, args, context={}):
        res = {}
        piutangrr_line_obj = self.pool.get('pln.dpiutangrr_line')
        for this in self.browse(cr, uid, ids):
            ba_line_ids = piutangrr_line_obj.search(cr, uid, [('partner_id', '=', this.id), ('state', '=', 'valid')])
            if ba_line_ids:
                ba_line = piutangrr_line_obj.browse(cr, uid, ba_line_ids)[-1]
                res[this.id] = ba_line.piutangrr_id.name
            else:
                res[this.id] = '-'
        return res
    
    _columns = {
        'golongan_tarif' : fields.many2one('pln.golongan_tarif', string='Golongan Tarif'),
        'daya' : fields.many2one('pln.daya', string='Daya'),  
        'piutangrr_id' : fields.function(_get_no_ba, type='char', string='Nomor BA'), 
    }
res_partner()