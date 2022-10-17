# -*- coding: utf-8 -*-

from odoo import models, fields, api


class iq_inherit_warehouse(models.Model):
    _inherit = 'stock.warehouse'
    
    
    iq_done_delivery= fields.Boolean('حركه استقبال معتمده')
    iq_done_invoice= fields.Boolean('فاتورة معتمده')