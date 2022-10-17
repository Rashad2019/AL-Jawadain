# -*- coding: utf-8 -*-

from odoo import models, fields, api
import json


class iq_po_discount_custom(models.Model):
    _inherit = "purchase.order"

    iq_discount_type = fields.Selection([('percent', 'Percentage'), ('amount', 'Amount')],
                                               string='Discount Type', readonly=True,
                                               states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
                                               default='percent')
    iq_discount_amount = fields.Float('Discount Amount', readonly=True,
                                           states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})

    @api.onchange('currency_id')
    def onchange_currency_id(self):
        for order in self:
            print('test')
            params = {'order_id': order.id}
            if order.order_line:
                for line in order.order_line:
                    seller = line.product_id._select_seller(
                        partner_id=order.partner_id,
                        quantity=line.product_qty,
                        date=order.date_order and order.date_order.date(),
                        uom_id=line.product_uom,
                        params=params)

                    if not seller:
                        if order.currency_id.id != order.company_id.currency_id.id:
                            line.price_unit = order.company_id.currency_id._convert(
                                line.product_id.standard_price,order.currency_id,order.company_id,
                                order.date_order or fields.Date.today())
                        else:
                            line.price_unit = line.product_id.standard_price
                        continue

                    price_unit = self.env['account.tax']._fix_tax_included_price_company(seller.price,
                                                                                         line.product_id.supplier_taxes_id,
                                                                                         line.taxes_id,
                                                                                         order.company_id) if seller else 0.0
                    if price_unit and seller and order.currency_id and seller.currency_id != order.currency_id:
                        price_unit = seller.currency_id._convert(
                            price_unit,order.currency_id,order.company_id,
                            order.date_order or fields.Date.today())

                    if seller and line.product_uom and seller.product_uom != line.product_uom:
                        price_unit = seller.product_uom._compute_price(price_unit,line.product_uom)

                    line.price_unit = price_unit
    
    @api.onchange('iq_discount_amount','iq_discount_type')
    def iq_get_discount(self):
        print("sssssss")
        if self.iq_discount_amount != 0:
                print("ppppppp%%%%",self.amount_total,self.iq_discount_amount)
                iq_count = 0
                line_disc = 0
                for x in self.order_line:
                    iq_count = iq_count+1
                
                if self.iq_discount_type == 'percent':
                    line_disc = self.iq_discount_amount
                else:
                    line_disc = self.iq_discount_amount/iq_count
                    
                    
                    
                for x in self.order_line:
                    x.write({
                        'iq_disc': line_disc,
                        'iq_disc_type': self.iq_discount_type,
                         })
                    
                    
    def _prepare_invoice(self):
        res = super(iq_po_discount_custom, self)._prepare_invoice()
        res['iq_discount_type'] = self.iq_discount_type
        res['iq_discount_amount'] = self.iq_discount_amount

        return res
    
           
        
    
class iq_po_lines_discount_custom(models.Model):
    _inherit = "purchase.order.line"
    
    iq_disc = fields.Float(string='Discount')
    iq_disc_type = fields.Char('Disc Type')
    
    
    def _prepare_account_move_line(self, move=False):
        print("11111111111111")
        res = super(iq_po_lines_discount_custom, self)._prepare_account_move_line()
        res['iq_disc_type'] = self.order_id.iq_discount_type
        res['iq_disc'] = self.iq_disc
        print("res",res)
        if self.order_id.iq_discount_type == 'percent':
            res['discount'] = self.iq_disc
        else:
            if self.price_unit != 0 :
                line_per = (self.iq_disc/self.price_unit)*100
            res['discount'] = line_per
            
        return res
    

    def _prepare_compute_all_values(self):
        res = super(iq_po_lines_discount_custom, self)._prepare_compute_all_values()
 
        self.ensure_one()
        if self.iq_disc != 0 :
            if self.order_id.iq_discount_type == 'percent':
                per_price_unit = self.price_unit * (1 - self.iq_disc / 100)
            else:
                per_price_unit = self.price_unit-self.iq_disc
            return {
            'price_unit': per_price_unit,
            'currency_id': self.order_id.currency_id,
            'product_qty': self.product_qty,
            'product': self.product_id,
            'partner': self.order_id.partner_id,
            }

        else:
            return res
    
    
    
#     
#     @api.depends('product_qty', 'price_unit', 'taxes_id','iq_disc')
#     def _compute_amount(self):
#         for line in self:
#             
#             if line.order_id.iq_discount_type == 'percent':
#                 if line.iq_disc != 0 :
#                     per_price_unit = line.price_unit-(line.price_unit*(line.iq_disc/100))
#                     taxes_perc = line.taxes_id.compute_all(per_price_unit, line.order_id.currency_id, line.product_qty, product=line.product_id, partner=line.order_id.partner_id)
#                     print("taxes3333333",taxes_perc)
#                     line.update({
#                         'price_tax': taxes_perc['total_included'] - taxes_perc['total_excluded'],
#                         'price_total': taxes_perc['total_included'],
#                         'price_subtotal': taxes_perc['total_excluded'] ,
#                     })
#            
#                 else:
#                     taxes_perc = line.taxes_id.compute_all(line.price_unit, line.order_id.currency_id, line.product_qty, product=line.product_id, partner=line.order_id.partner_id)
#                     line.update({
#                         'price_tax': taxes_perc['total_included'] - taxes_perc['total_excluded'],
#                         'price_total': taxes_perc['total_included'],
#                         'price_subtotal': taxes_perc['total_excluded'] ,
#                     })
#    
#                 
#             else:
#                 if line.iq_disc != 0 :
#                     fix_price_unit = line.price_unit-line.iq_disc
#                     taxes_fix = line.taxes_id.compute_all(fix_price_unit, line.order_id.currency_id, line.product_qty, product=line.product_id, partner=line.order_id.partner_id)
#                     print("taxes3333333",taxes_fix)
#                     line.update({
#                         'price_tax': taxes_fix['total_included'] - taxes_fix['total_excluded'],
#                         'price_total': taxes_fix['total_included'],
#                         'price_subtotal': taxes_fix['total_excluded'] ,
#                     })
#            
#                 else:
#                     taxes_fix = line.taxes_id.compute_all(line.price_unit, line.order_id.currency_id, line.product_qty, product=line.product_id, partner=line.order_id.partner_id)
#                     line.update({
#                         'price_tax': taxes_fix['total_included'] - taxes_fix['total_excluded'],
#                         'price_total': taxes_fix['total_included'],
#                         'price_subtotal': taxes_fix['total_excluded'] ,
#                     })    
#                 
                
                

    
    
