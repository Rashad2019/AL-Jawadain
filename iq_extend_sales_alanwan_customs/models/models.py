# -*- coding: utf-8 -*-


from odoo import models, fields, api,SUPERUSER_ID,_,exceptions



class iq_extendinherit_saleorderlinesprices(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('price_unit','product_uom_qty')
    def get_all_price_b_disc(self):
        self.iq_total_beforedisc = self.price_unit*self.product_uom_qty

class iq_extendinherit_saleorder(models.Model):
    _inherit = 'sale.order'
    
    iq_total_befor_disc = fields.Monetary(compute='iq_get_total', string='Total Before Discount')
    iq_total_disc = fields.Monetary(compute='iq_get_total', string='Total Discount')

    def iq_get_total(self):
        total_b_disc = 0
        total_disc = 0
        for x in self.order_line:
            total_b_disc = total_b_disc + x.iq_total_beforedisc
            total_disc = total_disc + (x.iq_total_beforedisc - x.price_subtotal)

        self.iq_total_befor_disc = total_b_disc
        self.iq_total_disc = total_disc


        
class iq_soinvoice_lineprices_discount_custom(models.Model):
    _inherit = "account.move.line"       
        
    @api.onchange('price_unit','quantity')
    def get_all_price_b_disc(self):
        self.iq_total_beforedisc =  self.price_unit*self.quantity
        
        
        
class iq_extendinherit_movenvoice(models.Model):
    _inherit = 'account.move'
    
    iq_total_befor_disc = fields.Monetary(compute='iq_get_total',string='Total Before Discount')
    
    iq_total_disc = fields.Monetary(compute='iq_get_total',string='Total Discount')

    def iq_get_total(self):
        total_b_disc = 0
        total_disc = 0
        for x in self.invoice_line_ids:
            total_b_disc = total_b_disc + x.iq_total_beforedisc
            total_disc = total_disc + (x.iq_total_beforedisc - x.price_subtotal)
            
        self.iq_total_befor_disc = total_b_disc
        self.iq_total_disc = total_disc
