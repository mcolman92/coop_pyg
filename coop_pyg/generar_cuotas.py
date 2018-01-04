from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import Warning
from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)
import sys
reload(sys)
sys.setdefaultencoding('utf8')

class GenerarCuotas(models.TransientModel):
    _name = "generar.cuotas"
    _description = "Generacion de cuotas sociales"

    all_partner = fields.Boolean('Todos los socios', default = False)
    partner_id = fields.Many2many('res.partner', string='Socio/s :', required = False, domain=[('socio', '=', True)])
    cuota_id = fields.Many2one('tipo.cuota.social', 'Cuota social a generar :', required = True)
    fiscalyear_id = fields.Many2one('account.fiscalyear', 'Ejercicio Fiscal :', required = True)
    period_from = fields.Many2one('account.period', 'Periodo Inicial :', required = True)
    period_to = fields.Many2one('account.period', 'Periodo Final :', required = True)
    #CAMPO AGREGADO PARA LA FACTURA
    company_id = fields.Many2one('res.company', 'Company', required=True, ondelete='cascade',)

    @api.one 
    def generar_cuotas_sociales(self):
        self.create_invoices()

    @api.one
    def create_invoices(self):
        product_coop_id = self.cuota_id.id
        product_coop = self.env['tipo.cuota.social'].search([('id','=',product_coop_id)])
        periodo_start = int(self.period_from)
        periodo_stop = int(self.period_to)
        date_invoice_start = self.env['account.period'].browse(periodo_start)
        dominio_periodo = self.env['account.period'].search([('id', '>=', periodo_start), ('id','<=', periodo_stop)])            
        #periodo_browse = dominio_periodo.browse(dominio_periodo)
        #partner_id=int(self.partner_id)
        #partner = self.env['res.partner'].browse(partner_id)
        if self.all_partner:
            domian_all = self.env['res.partner']
            partner_id = domian_all.search([('socio', '=', True)])
        else:
            partner_id = self.partner_id
            
        for socio_id in partner_id:
            partner = socio_id
            for period in dominio_periodo:
                invoice_vals = self._prepare_invoice(partner, period)
                ids_invoice = []
                contador = 0        
                for data in invoice_vals:
                    invoice = self.env['account.invoice'].create(data)               
                    invoice.button_reset_taxes()
                    invoice.signal_workflow('invoice_draft')
                    invoice_id = invoice.id     
                    ids_invoice.append(invoice_id)
                    contador = contador + 1
                    dict_cuota_social = {'partner_id': partner.id,
                        'name': product_coop.descripcion ,
                        'date_expiry': period.date_stop,
                        'state':'pending',
                        'invoice_id': invoice.id,
                        'tipo_cuota_social_id': product_coop.id ,
                        'debit': product_coop.product_id.list_price,
                        'periodo_id': period.id,
                        }
                    cuota_social = self.env['cuota.social'].create(dict_cuota_social)


    @api.multi
    def _prepare_invoice(self, partner, period):
        self.ensure_one()
        #periodo = int(self.period_from)

        #date_invoice_start = self.env['account.period'].browse(period.id)
        lista2 = []
        product_coop_id = self.cuota_id.id
        product_coop = self.env['tipo.cuota.social'].search([('id','=',product_coop_id)])      
        account_id = partner.property_account_receivable.id
        lineas =  self._prepare_invoice_line(partner,product_coop, period)
        
        for x in lineas:
            invoice_vals = {
                'type': 'out_invoice',
                'account_id': account_id,
                'partner_id': partner.id,
                'reference': product_coop.descripcion, 
                'invoice_line': [(0, 0, x)], 
                'currency_id': self.company_id.currency_id.id, 
                'payment_term': partner.property_payment_term.id or False, 
                'fiscal_position': partner.property_account_position.id, 
                'date_invoice': period.date_start,
                'date_due': period.date_stop, 
                'company_id': self.company_id.id, 
                'user_id': partner.user_id.id or False
                }
            lista2.append(invoice_vals)
        
        return lista2

    @api.multi
    def _prepare_invoice_line(self, partner,product_coop,period):
        self.ensure_one()
        #periodo = self.period_from

        lista = []
        company = self.company_id
        for reg in product_coop.product_id:
            name = _('%s.\n %s''') % (reg.name, period.name)
            amount = reg.list_price
            line_data = self.env['account.invoice.line'].with_context(force_company=company.id).product_id_change(reg.id, reg.uom_id.id, qty=1.0, name='', type='out_invoice', partner_id=partner.id, fposition_id=partner.property_account_position.id, company_id=company.id)
            account_id = int(reg.property_account_income)
            line_vals = {'product_id': reg.id, 'name': name, 'price_unit': amount,'quantity': 1.0,'account_id': account_id, 'invoice_line_tax_id': [(6, 0, line_data['value'].get('invoice_line_tax_id', []))],}
            lista.append(line_vals)          

        return lista   


