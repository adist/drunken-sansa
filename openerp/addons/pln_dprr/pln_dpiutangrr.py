'''
Created on 2015-02-18 22:20

@author: adista@bizoft
'''
from openerp.osv import osv, fields
import time
import openerp.addons.decimal_precision as dp
from calendar import monthrange
from datetime import timedelta, datetime

def monthdelta(d1, d2):
    delta = 0
    while True:    
        mdays = monthrange(d1.year, d1.month)[1]
        d1 += timedelta(days=mdays)
        if d1 <= d2:
            delta += 1
        else:
            break
    return delta

class pln_dpiutangrr(osv.osv):
    '''
    dpiutangrr = Daftar Piutang Ragu-ragu
    '''
    _name = 'pln.dpiutangrr'
    _description = 'Dftr. Piutang Ragu2'
    _columns = {
        'name' : fields.char(string='Nomor BA', required=True, states={'valid':[('readonly', True)], 'cancel':[('readonly',True)]}),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('cancel', 'Batal'),
            ('valid', 'Valid'),
            ], 'Status', readonly=True, select=True, track_visibility='onchange', help="""
            * Draft: Dokumen masih belum dinyatakan valid.\n
            * Batal: Dokumen dibatalkan. \n
            * Valid: Dokumen dinyatakan Valid oleh sistem. \n
            """
        ), 
        'date': fields.datetime('Creation Date', help="Biasanya adalah tanggal dokumen diunggah", select=True, states={'valid':[('readonly', True)], 'cancel':[('readonly',True)]}),
        'valid_from' : fields.date('Berlaku mulai', states={'valid':[('readonly', True)], 'cancel':[('readonly',True)]}),
        'valid_to' : fields.date('Berlaku hingga', states={'valid':[('readonly', True)], 'cancel':[('readonly',True)]}), 
        # TODOmy: iki enak e relasi res.partner opo hr.employee opo res.users??
#         'apj' : fields.char(string='APJ'), 
#         'upj' : fields.char(string='UPJ'),
        'lines' : fields.one2many('pln.dpiutangrr_line', 'piutangrr_id', string='Detail'),  
    }

    _defaults = {
        'state' : 'draft', 
        'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
    }
    
    def button_valid(self, cr, uid, ids, contex={}):
        this = self.browse(cr, uid, ids)[-1]
        for line in this.lines:
            line._model.write(cr, uid, [line.id], {'state' : 'valid'})
        self.write(cr, uid, [this.id], {'state' : 'valid'})
        return True 
    
    def button_draft(self, cr, uid, ids, contex={}):
        this = self.browse(cr, uid, ids)[-1]
        for line in this.lines:
            line._model.write(cr, uid, [line.id], {'state' : 'draft'})
        self.write(cr, uid, [this.id], {'state' : 'draft'})
        return True 
    
    def button_cancel(self, cr, uid, ids, contex={}):
        this = self.browse(cr, uid, ids)[-1]
        for line in this.lines:
            line._model.write(cr, uid, [line.id], {'state' : 'cancel'})
        self.write(cr, uid, [this.id], {'state' : 'cancel'})
        return True 
    
pln_dpiutangrr()

class pln_dpiutangrr_line(osv.osv):
    _name = 'pln.dpiutangrr_line'
    _description = 'Dftr. Piutang Ragu2 (detail)'
    
    def _get_month_range(self, cr, uid, ids, fields_name, args, context={}):
        res = {}
        for this in self.browse(cr, uid, ids):
            date_start = datetime.strptime(this.date_start, '%Y-%m-%d') 
            date_end = datetime.strptime(this.date_end, '%Y-%m-%d') 
            res[this.id] = monthdelta(date_start, date_end) + 1
        return res
    
    def _get_piutang_ragu2(self, cr, uid, ids, fields_name, args, context={}):
        res = {}
        for this in self.browse(cr, uid, ids):
            sumx = this.piutang_rp + this.piutang_nontagihan_rp - this.bpju_rp - this.ppn_rp - this.materai_rp - this.klp_rp - this.ujl_rp
            res[this.id] = sumx
        return res
    
    def _get_complexity(self, cr, uid, ids, fields_name, args, context={}):
        res = {}
        dprr_obj = self.pool.get('pln.docprr')
        img_cols = [col for col in dprr_obj._columns if col.startswith('img_')]
        for this in self.browse(cr, uid, ids):
            res[this.id] = 0 
            sql = '''select * from pln_docprr where partner_id in %s''' #and state in ('valid')''' 
            cr.execute(sql, (tuple([this.partner_id.id]),))
            qresult = cr.dictfetchall()
            for resx in qresult:
                counter = 0.0
                for valx in resx:
                    if not valx.startswith('img_'): continue
                    if resx[valx]: counter += 1
                res[this.id] = counter / len(img_cols) * 100
                break
        return res
    
    _columns = {
        'piutangrr_id' : fields.many2one('pln.dpiutangrr', 'Nomor BA', states={'valid':[('readonly', True)], 'cancel':[('readonly',True)]}), 
        'partner_id' : fields.many2one('res.partner', 'Pelanggan', required=True, states={'valid':[('readonly', True)], 'cancel':[('readonly',True)]}),
        'date_start' : fields.date(string='Bulan Awal', help='Isi tanggal 1 pada bulan awal dari piutang ragu-ragu milik Pelanggan ybs.'
                                   , states={'valid':[('readonly', True)], 'cancel':[('readonly',True)]}), 
        'date_end' : fields.date(string='Bulan Akhir', help='Isi tanggal terakhir (28 atau 29 atau 30 atau 31) pada bulan akhir dari piutang ragu-ragu milik Pelanggan ybs.'
                                 , states={'valid':[('readonly', True)], 'cancel':[('readonly',True)]}),
        'range' : fields.function(_get_month_range, string='Lembar', type='integer', help='Dalam bulan'),
        'piutang_rp' : fields.float(digits_compute=dp.get_precision('Product Unit of Measure'), string='Rupiah', states={'valid':[('readonly', True)], 'cancel':[('readonly',True)]}), 
        'piutang_nontagihan_rp' : fields.float(digits_compute=dp.get_precision('Product Unit of Measure'), string='Piutang non-Tagihan', states={'valid':[('readonly', True)], 'cancel':[('readonly',True)]}), 
        'bpju_rp' : fields.float(digits_compute=dp.get_precision('Product Unit of Measure'), string='BPJU', states={'valid':[('readonly', True)], 'cancel':[('readonly',True)]}), 
        'ppn_rp' : fields.float(digits_compute=dp.get_precision('Product Unit of Measure'), string='PPN', states={'valid':[('readonly', True)], 'cancel':[('readonly',True)]}), # can we make this columns more simple?
        'materai_rp' : fields.float(digits_compute=dp.get_precision('Product Unit of Measure'), string='Materai', states={'valid':[('readonly', True)], 'cancel':[('readonly',True)]}), 
        'klp_rp' : fields.float(digits_compute=dp.get_precision('Product Unit of Measure'), string='KLP', states={'valid':[('readonly', True)], 'cancel':[('readonly',True)]}), 
        'ujl_rp' : fields.float(digits_compute=dp.get_precision('Product Unit of Measure'), string='UJL', states={'valid':[('readonly', True)], 'cancel':[('readonly',True)]}), 
        'piutangrr_rp' : fields.function(_get_piutang_ragu2, type='float', digits_compute=dp.get_precision('Product Unit of Measure'), string='Piutang Ragu-ragu', help='Jumlah Piutang Ragu-ragu.'),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('cancel', 'Batal'),
            ('valid', 'Valid'),
            ], 'Status', readonly=True, select=True, track_visibility='onchange', help="""
            * Draft: Dokumen masih belum dinyatakan valid.\n
            * Batal: Dokumen dibatalkan. \n
            * Valid: Dokumen dinyatakan Valid oleh sistem. \n
            """
        ),  
        'complete' : fields.function(_get_complexity, string='Kelengkapan', type='float'),
#         'complete' : fields.float(string='Kelengkapan', digits_compute=dp.get_precision('Product Unit of Measure'), help="In %"),
    }
    
    _defaults = {
        'state' : 'draft', 
    }
    
#     def create(self, cr, uid, vals, context={}):
#         res = super(pln_dpiutangrr_line, self).create(cr, uid, vals, context={})
#         compleks = self._get_complexity(cr, uid, [res], False, False, context=context)
#         ctx = context.copy()
#         ctx['skip'] = True
#         self.write(cr, uid, [res], {'complete' : compleks[res]}, context=ctx)
#         return res
#     
#     def write(self, cr, uid, ids, vals, context={}):
#         if context.get('skip', False):
#             return super(pln_dpiutangrr_line, self).write(cr, uid, ids, vals, context={})
#         compleks = self._get_complexity(cr, uid, ids, False, False, context=context)
#         for this in self.browse(cr, uid, ids):
#             sql = 'update ' + self._table + ' set complete=' + str(compleks[this.id]) + 'where id = ' + str(this.id)
#             cr.execute(sql)
#         return super(pln_dpiutangrr_line, self).write(cr, uid, ids, vals, context={})
    
    def name_get(self, cr, uid, ids, context=None):
        res = {}
        for this in self.browse(cr, uid, ids):
            res[this.id] = this.piutangrr_id.name + ' - ' + this.partner_id.name 
        return res.items()
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        ids = self.search(cr, user, [('piutangrr_id.name', operator, name)] + args, limit=limit, context=context)
        ids += self.search(cr, user, [('partner_id.name', operator, name)] + args, limit=limit, context=context)
        return self.name_get(cr, user, ids, context)
    
    def button_valid(self, cr, uid, ids, contex={}):
        self.write(cr, uid, ids, {'state' : 'valid'})
        return True 
    
    def button_draft(self, cr, uid, ids, contex={}):
        self.write(cr, uid, ids, {'state' : 'draft'})
        return True 
    
    def button_cancel(self, cr, uid, ids, contex={}):
        self.write(cr, uid, ids, {'state' : 'cancel'})
        return True 
pln_dpiutangrr_line()