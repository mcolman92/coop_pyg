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

class TipoCuotaSocial(models.Model):
    _name = 'tipo.cuota.social'
    name = fields.Char('Codigo :', size=3, required=True)
    descripcion = fields.Char('Descripcion :', size=60, required=True)
    product_id = fields.Many2one('product.product', 'Producto', required =True)
    activo= fields.Boolean('Activo?: ')

