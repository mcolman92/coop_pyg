#-*- coding: utf-8 -*-
from openerp import models, fields, api

class PartnerCoop(models.Model):
    _inherit = 'res.partner'
    socio = fields.Boolean('Socio', readonly = True)
    date_solicitud = fields.Date('Fecha de Solicitud:')
    socio_nro = fields.Char('Nro. de Socio:')
    cedula_identidad = fields.Char('Cedula de Identidad:',size=12)
    date_nacimiento = fields.Date('Fecha de nacimiento')
    nacionalidad = fields.Char('Nacionalidad',size=12)
    profesion = fields.Char("Profesion",size=15)
    estado_civil = fields.Char('Estado civil',size=10)
    trabajo = fields.Many2one('res.partner', 'Lugar de Trabajo')
    antiguedad_laboral = fields.Char('Antiguedad Laboral:', size=10)
    conyugue = fields.Many2one('res.partner','Conyuge:')
    proponente = fields.Many2one('res.partner','proponente')



        



    