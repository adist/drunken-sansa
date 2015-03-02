'''
Created on 2015-02-19 22:06

@author: adista@bizoft
'''
from openerp.osv import osv, fields

class pln_docprr(osv.osv):
    '''
    docprr = Dokumen/Kelengkapan Piutang Ragu-ragu
    '''
    _name = 'pln.docprr'
    _description = 'Kelengkapan Piutang Ragu2'

    def _get_complexity(self, cr, uid, ids, fields_name, args, context={}):
        res = {}
        img_cols = [col for col in self._columns if col.startswith('img_')]
        sql = '''select * from ''' + self._table + ''' where id in %s ''' 
        cr.execute(sql, (tuple(ids),))
        qresult = cr.dictfetchall()
        for this in qresult:
            counter = 0.0
            for valx in this:
                if not valx.startswith('img_'): continue
                if this[valx]: counter += 1
            res[this['id']] = counter / len(img_cols) * 100
        return res

    _columns = {
        'partner_id' : fields.many2one('res.partner', string='Pelanggan', required=True), 
        'nomor_ba' : fields.related('partner_id', 'piutangrr_id', string='Nomor BA', type='char'),
        'img_taglist': fields.binary('Tagihan Listrik'), 
        'img_tul601': fields.binary('TUL VI-01'), 
        'img_tul603': fields.binary('TUL VI-03'), 
        'img_pkbrampung': fields.binary('PK Bongkar Rampung'), 
        'img_babrampung': fields.binary('BA Bongkar Rampung'), 
        'img_pdlmutasin': fields.binary('PDL Mutasi N'), 
        'img_tug9kwh': fields.binary('TUG 9 - KWH', help='kWh meter'), 
        'img_tug9mcb': fields.binary('TUG 9 - MCB', help='MCB'), 
        'img_tug9kbl': fields.binary('TUG 9 - Kabel SR', help='Kabel SR'), 
        'img_kwhmeter': fields.binary('KWH Meter'), 
        'img_stannumber': fields.binary('Angka stan', help='Foto angka stan.'),
        'complete' : fields.function(_get_complexity, string='Kelengkapan', type='float', help="In %"), 
        'coordinate' : fields.char('Geo Coordinate'),
        'note' : fields.text('Catatan'),  
        'multi_images': fields.text("Multi Images"),
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
    }
    _rec_name = 'nomor_ba'
pln_docprr()    