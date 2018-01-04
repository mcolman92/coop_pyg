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

class TestCoop(models.Model):
    _name = 'test.coop'
    nro_solicitud = fields.Char('Numero de solicitud :', size=6 , required=True , help="Ingrese su numero de solicitud")
    name = fields.Many2one('res.partner','Solicitante:', required=True, domain=[('socio','=', False)])
    date_solicitud = fields.Date('Fecha de Solicitud:', required=True)
    state = fields.Selection([('draft','Nuevo'),('aceptado','Aprobado'), ('rechazado','Rechazado'),('cancel','Cancelado')],default='draft',string="Estado de la solicitud:")
    comentario=fields.Text('Comentarios')
    initial_fee = fields.Selection([('none', 'Sin cuota de ingreso'),('fixed', 'Monto fijo'), ('percentage', 'Porcentaje del precio')], default='none', string="Cuota de ingreso")
    fixed_fee = fields.Float(digits_compute=dp.get_precision('Product Price'), string="Monto fijo")
    percentage_fee = fields.Float('Porcentaje :',(12, 2))
    #product_fee = fields.Many2one('product.product', string="Producto para cuota de ingreso ")
    product_fee = fields.Many2one('product.coop', string="Producto para cuota de ingreso ", domain = [('activo', '=', True)])
    ## CAMPO AGREGADO PARA LA FACTURA
    receivable_account_ids = fields.Many2many('account.account', string='Cuentas a Cobrar', help='Cuentas a Cobrar que se tendrán en cuenta para evaular la deuda', required=True, domain="[('type', '=', 'receivable'),('company_id', '=', company_id)]",)
    automatic_validation = fields.Boolean('Automatic Validation?', help='Automatic Invoice Validation?', default=True,)
    date_invoice = fields.Date('Date of Next Invoice', default=fields.Date.today,)
    invoice_receivable_account_id = fields.Many2one('account.account', string='Invoice Receivable Account', help='If no account is sellected, then partner receivable account is ''used', domain="[('type', '=', 'receivable'),('company_id', '=', company_id)]",)
    company_id = fields.Many2one('res.company', 'Company', required=True, ondelete='cascade',)



     # @api.onchange('product_fee')
     # def onchange_product_fee(self):
     #     product_coop_id = self.product_fee.id
     #     product_coop = self.env['product.coop'].search([('id','=',product_coop_id)])
     #     self.fixed_fee = product_coop.product.list_price
   
    @api.one 
    def aprobar_solicitud1(self):        
        self.write({'state':'aceptado'})
        solicitante = int(self.name)
        partner = self.env['res.partner'].search([('id', '=', solicitante)])                    
        partner.write({'socio':True})        
        return True
    
    @api.one 
    def rechazar_solicitud1(self):
        self.write({'state':'rechazado'})
        solicitante = int(self.name)
        partner = self.env['res.partner'].search([('id', '=', solicitante)])        
        partner.write({'socio':False})
        return True

    @api.one 
    def cancelar_solicitud1(self):
        self.write({'state':'cancel'})
        solicitante = int(self.name)
        partner = self.env['res.partner'].search([('id', '=', solicitante)])
        partner.write({'socio':False})
        return True

    @api.one
    def create_invoice(self):
        self.create_invoices()


    @api.one
    def create_invoices(self):
        data_inv = self.date_invoice        
        partner_id=int(self.name)
        partner = self.env['res.partner'].browse(partner_id)
        invoice_vals = self._prepare_invoice(partner)
        ids_invoice = []
        #enviamos tipo de documento para compatibilidad con facturas argentinas
        for data in invoice_vals:
            invoice = self.env['account.invoice'].create(data)
        # actualizar los montos para la nueva factura
            invoice.button_reset_taxes()
            if self.automatic_validation:
                invoice.signal_workflow('invoice_draft')
            invoice_id = invoice.id     
            ids_invoice.append(invoice_id)

        group_invoice_coop = self._group_invoice(ids_invoice, data_inv)



    @api.multi
    def _prepare_invoice(self, partner):
        self.ensure_one()
        lista2 = []
        product_coop_id = self.product_fee.id
        product_coop = self.env['product.coop'].search([('id','=',product_coop_id)])
        
        account_id = self.invoice_receivable_account_id.id
        lineas =  self._prepare_invoice_line(partner,product_coop)
        lineas2 = self._recorrer_lista(lineas)
        
        for x in lineas:
            invoice_vals = {
                'type': 'out_invoice',
                'account_id': account_id,
                'partner_id': partner.id,
                'reference': product_coop.name, 
                'invoice_line': [(0, 0, x)], 
                    #'invoice_line': [(6, 0, self._prepare_invoice_line(partner,product_coop))],
                'currency_id': self.company_id.currency_id.id, 
                'payment_term': partner.property_payment_term.id or False, 
                'fiscal_position': partner.property_account_position.id, 
                'date_invoice': self.date_invoice, 
                'company_id': self.company_id.id, 
                'user_id': partner.user_id.id or False
                }
            lista2.append(invoice_vals)
        
        return lista2


        #return invoice_vals

            


    def _recorrer_lista(self, lineas):
        for x in lineas:
            return x

    @api.multi
    def _prepare_invoice_line(self, partner,product_coop):
        self.ensure_one()
        #product_coop_id = self.product_fee.id
        #product_coop = self.env['product.coop'].search([('id','=',product_coop_id)])
        lista = []
        company = self.company_id
        for reg in product_coop.product:
            name = _('%s.\n''Cuota de ingreso nvo socio ') % (reg.name)
            amount = reg.list_price
            line_data = self.env['account.invoice.line'].with_context(force_company=company.id).product_id_change(reg.id, reg.uom_id.id, qty=1.0, name='', type='out_invoice', partner_id=partner.id, fposition_id=partner.property_account_position.id, company_id=company.id)

            account_id = int(reg.property_account_income)
            line_vals = {'product_id': reg.id, 'name': name, 'price_unit': amount,'quantity': 1.0,'account_id': account_id, 'invoice_line_tax_id': [(6, 0, line_data['value'].get('invoice_line_tax_id', []))],}
            #vals_inv_line = [(0, 0, line_vals)]
            #lista.append(vals_inv_line)
            lista.append(line_vals)
            

        return lista   


    @api.multi
    def _group_invoice(self,ids_invoice, date_inv):
        invoice_merge = self.env['invoice.merge'].browse()
        invoice_merge_action = invoice_merge.merge_invoices_coop(ids_invoice, date_inv)
        account_invoice_obj = self.env['account.invoice'].search([('id', '=', ids_invoice)])
        account_invoice_obj.unlink()
        return True
        #return line_vals


    # @api.multi
    # def _prepare_invoice_line(self, partner,product_coop):
    #     self.ensure_one()
    #     product_coop_id = self.product_fee.id
    #     #product_coop = self.env['product.coop'].search([('id','=',product_coop_id)])
    #     lista = []
    #     company = self.company_id
    #     brow = self.env['product.coop'].browse(product_coop_id)
    #     for reg in browse.product.id:
    #         name = _('%s.\n''Cuota de ingreso nvo socio ') % (product_coop.product.name)
    #         amount = product_coop.product.list_price
    #         line_data = self.env['account.invoice.line'].with_context(force_company=company.id).product_id_change(product_coop.product.id, product_coop.product.uom_id.id, qty=1.0, name='', type='out_invoice', partner_id=partner.id, fposition_id=partner.property_account_position.id, company_id=company.id)

    #         account_id = int(product_coop.product.property_account_income)
    #         line_vals = {'product_id': product_coop.product.id, 'name': name, 'price_unit': amount,'quantity': 1.0,'account_id': account_id, 'invoice_line_tax_id': [(6, 0, line_data['value'].get('invoice_line_tax_id', []))],}
    #         vals_inv_line = [(0, 0, line_vals)]
    #         lista.append(vals_inv_line)
    #         #return line_vals

    #     return lista    
    #     #return line_vals