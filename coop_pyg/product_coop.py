#-*- coding: utf-8 -*-
from openerp import models, fields, api


class ProductCoop(models.Model):
    _name = 'product.coop'
    name = fields.Char('Nombre del producto:',required=True, help = "Nombre del producto")
    product = fields.Many2many ('product.product', string='Productos')
    activo = fields.Boolean('Activo')

