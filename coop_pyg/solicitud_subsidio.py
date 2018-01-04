#-*- coding: utf-8 -*-
from openerp import models, fields, api

class SolicitudSubsidio(models.Model):
    _name = 'solicitud.subsidio'
    nro_solicitud = fields.Char('Numero de solicitud :', size=6 , required=True , help="Ingrese su numero de solicitud")
    name = fields.Many2one('res.partner',string='Socio', required=True , domain=[('socio','=', True)])
    date_solicitud = fields.Date('Fecha de Solicitud:', required=True)
    state = fields.Selection([('draft','Nuevo'),('aceptado','Aprobado'), ('rechazado','Rechazado'),('cancel','Cancelado')],default='draft',string="Estado de la solicitud:")
    subsidio_id = fields.Many2one('subsidio', string='Tipo de subsidio :', required=True , domain=[('activo','=',True)])
    monto_aprobado = fields.Float('Monto aprobado :',(7,2) , required=True)
    comentario=fields.Text('Comentarios')
   
    @api.one 
    def aprobar_solicitud(self):        
        self.write({'state':'aceptado'})       
        return True
    
    @api.one 
    def rechazar_solicitud(self):
        self.write({'state':'rechazado'})
        return True

    @api.one 
    def cancelar_solicitud(self):
        self.write({'state':'cancel'})
        return True