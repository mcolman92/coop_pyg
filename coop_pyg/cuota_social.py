#-*- coding: utf-8 -*-
from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import Warning
from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)
import sys
reload(sys)
sys.setdefaultencoding('utf8')

class CuotaSocial(models.Model):
    _name = 'cuota.social'
    partner_id = fields.Many2one('res.partner','Socio:', domain=[('socio','=', True)], readonly=True)
    name = fields.Char('Descripcion :', size=60, readonly=True)
    date_expiry = fields.Date('Fecha de vencimiento', readonly=True)
    state = fields.Selection([('paid','Pagado'),('pending','Pendiente'),('cancel','Cancelado')], readonly = True, string="Estado:",compute='_state_invoice', store=True)
    invoice_id = fields.Many2one('account.invoice', 'Factura :', readonly = True)
    tipo_cuota_social_id = fields.Many2one('tipo.cuota.social', 'Tipo de cuota social', readonly = True)
    debit = fields.Float('Debe:', (12, 2), readonly = True)
    credit = fields.Float('Haber:', (12, 2), readonly = True)
    periodo_id = fields.Many2one('account.period', 'Periodo', readonly = True)

    @api.one
    @api.depends('invoice_id.state')
    def _state_invoice(self):
        state_invoice = self.invoice_id.state
        if state_invoice == "paid":
            self.state = 'paid'
        else:
            if state_invoice == "cancel":
                self.state = 'cancel'
            else:
                self.state = 'pending'








