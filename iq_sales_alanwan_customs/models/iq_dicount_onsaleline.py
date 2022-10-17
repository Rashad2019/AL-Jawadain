
# -*- coding: utf-8 -*-

from odoo import models, fields, api
import json




class iq_so_lines_discount_custom(models.Model):
    _inherit = "sale.order.line"
    
    iq_disc = fields.Float(string='قيمه الخصم')
    iq_discount_type = fields.Selection([('percent', 'نسبه'), ('amount', 'ثابت')],
                                               string='نوع الخصم', readonly=True,
                                               states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    iq_total_beforedisc = fields.Float(string='السعر قبل الخصم',compute="_iq_get_or_price")

    def _iq_get_or_price(self):
        print("111111111111111111")
        for rec in self:
            rec.iq_total_beforedisc = rec.price_unit*rec.product_uom_qty
    
    def _prepare_invoice_line(self, **optional_values):
        print("11111111111111")
        res = super(iq_so_lines_discount_custom, self)._prepare_invoice_line()
        res['iq_discount_type'] = self.iq_discount_type
        res['iq_disc'] = self.iq_disc
        res['iq_total_beforedisc'] = self.iq_total_beforedisc
        
#         if self.iq_discount_type == 'amount':
#                 if self.price_unit != 0 :
#                     disc = (self.iq_disc/self.price_unit )* 100
#                     res['discount'] = disc
#                     
#                     
#                 
#         else:
#                 res['discount'] = self.iq_disc
                
                
        
        
        return res

    def write(self, vals):
        # code
        if 'iq_discount_type' in vals and 'iq_disc' in vals and vals['iq_disc'] > 0:
            vals['discount'] = self.compute_disc(vals)

        res = super(iq_so_lines_discount_custom, self).write(vals)
        print(vals)
        return res

    @api.onchange('iq_disc','iq_discount_type')
    def get_values_disc(self):
        print(self.iq_disc,self.iq_discount_type,"discscscscsccs")
        self.iq_total_beforedisc = self.price_unit*self.product_uom_qty
        if self.iq_disc != 0 :
            if self.iq_discount_type == 'amount':
                print("dididi")
                if self.price_unit != 0 :
                    disc = (self.iq_disc/self.price_unit )* 100
                    self.write({
                        'discount': disc
                        })
            else:
                self.discount = self.iq_disc

    def compute_disc(self, vals):
        discount = 0
        if 'iq_disc' in vals and vals['iq_disc'] != 0:
            if 'iq_discount_type' in vals and vals['iq_discount_type'] == 'amount':
                if 'price_unit' in vals and vals['price_unit'] != 0:
                    disc = (vals['iq_disc'] / vals['price_unit']) * 100
                    discount = disc

            else:
                discount = vals['iq_disc']
        return discount


class iq_soinvoice_lines_discount_custom(models.Model):
    _inherit = "account.move.line"
    
    iq_disc = fields.Float(string='قيمة الخصم')
    iq_discount_type = fields.Selection([('percent', 'نسبه'), ('amount', 'ثابت')],
                                               string='نوع الخصم')
    iq_total_beforedisc = fields.Float(string='السعر قبل الخصم',compute="_iq_get_or_price")
    
    
    def _iq_get_or_price(self):
        print("111111111111111111")
        for rec in self:
            rec.iq_total_beforedisc = rec.price_unit*rec.quantity
    
    
    @api.onchange('iq_disc','iq_discount_type')
    def get_values_disc(self):
        print(self.iq_disc,self.iq_discount_type,"discscscscsccs22222222222")
        if self.iq_disc != 0 :
            if self.iq_discount_type == 'amount':
                print("dididi")
                if self.price_unit != 0 :
                    disc = (self.iq_disc/self.price_unit )* 100
                    self.discount = disc
                       
    
            else:
                self.discount = self.iq_disc
            
    
    
    
    
    
    
    
