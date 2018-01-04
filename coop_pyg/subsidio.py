#-*- coding: utf-8 -*-
from openerp import models, fields, api

class Subsidio(models.Model):
    _name = 'subsidio'
    name = fields.Char('Descripción: ', size=40)
    monto = fields.Float('Monto: ', (7,2))
    condiciones=fields.Text('Condiciones:')
    activo= fields.Boolean('Activo?: ')


  

