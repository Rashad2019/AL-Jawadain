
# -*- coding: utf-8 -*-

from odoo import models, fields, api


class iq_AccountMoveInherit(models.Model):

    _inherit = 'account.move'
    
    
    iq_discount_type = fields.Selection([('percent', 'Percentage'), ('amount', 'Amount')],
                                               string='Discount Type', readonly=True,
                                               states={'draft': [('readonly', False)]},
                                               default='percent')
    iq_discount_amount = fields.Float('Discount Amount', readonly=True,
                                           states={'draft': [('readonly', False)]})
    
    
    
    
    
    @api.onchange('iq_discount_amount','iq_discount_type')
    def iq_get_discount(self):
        if self.purchase_id:
            print("sssssss","888888888888888888888")
            if self.iq_discount_amount != 0:
                    iq_count = 0
                    line_disc = 0
                    for x in self.invoice_line_ids:
                        print("xxxx",x.price_unit)
                        iq_count = iq_count+1
                        line_disc = self.iq_discount_amount/iq_count
                    
                 
                        
                            
                    for x in self.invoice_line_ids:
                        print("xxxx333333333333333",x.price_unit)
                        if self.iq_discount_type == 'percent':
                            x.write({
                                'iq_disc': line_disc,
                                'iq_disc_type': self.iq_discount_type,
                                'discount':line_disc,
                                 })
                        else:
                            if x.unit_price != 0 :
                                line_per = (line_disc/x.unit_price)*100
                                x.write({
                                    'iq_disc': line_disc,
                                    'iq_disc_type': self.iq_discount_type,
                                     'discount':line_per,
                                     })
                                
            
        
    
    
    
#     @api.depends('invoice_line_ids.quantity', 'invoice_line_ids.price_unit', 'invoice_line_ids.tax_ids','invoice_line_ids.iq_disc')
#     def _compute_amount(self):
#         print("in lopppppppppppppppp")
#         for line in self.invoice_line_ids:
#             taxes = line.tax_ids.compute_all(line.price_unit, line.move_id.currency_id, line.quantity, product=line.product_id, partner=line.move_id.partner_id)
#             print("taxes",taxes)
#             if line.move_id.iq_discount_type == 'percent':
#                 if line.iq_disc != 0 :
#                     
#                     discount = (line.price_unit * line.iq_disc * line.quantity)/100
#                     line.update({
#                         'price_total': taxes['total_included'],
#                         'price_subtotal': taxes['total_excluded'] - discount,
#                     })
#            
#                 else:
#                     line.update({
#                         'price_total': taxes['total_included'],
#                         'price_subtotal': taxes['total_excluded'],
#                     })
#    
#                     
#             if line.move_id.iq_discount_type == 'amount':
#                 if line.iq_disc != 0 :
#                     
#                     discount =  line.iq_disc
#                     line.update({
#                         'price_total': taxes['total_included'],
#                         'price_subtotal': taxes['total_excluded'] - discount,
#                     })
#                 else:
#                     line.update({
#                         'price_total': taxes['total_included'],
#                         'price_subtotal': taxes['total_excluded'],
#                     })
                     
    
    
    
class iq_AccountMoveLINEInherit(models.Model):

    _inherit = 'account.move.line'
    
    iq_disc = fields.Float(string='Discount')
    iq_disc_type = fields.Char('Disc Type')
    
    
    
    
#     @api.depends('quantity', 'price_unit', 'tax_ids','iq_disc')
#     def _compute_amount(self):
#         print("in lopppppppppppppppp")
#         for line in self:
#             taxes = line.taxes_id.compute_all(line.price_unit, line.move_id.currency_id, line.quantity, product=line.product_id, partner=line.move_id.partner_id)
#             
#             if line.move_id.iq_discount_type == 'percent':
#                 if line.iq_disc != 0 :
#                     
#                     discount = (line.price_unit * line.iq_disc * line.quantity)/100
#                     line.update({
#                         'price_subtotal': taxes['total_excluded'] - discount,
#                     })
#            
#                 else:
#                     line.update({
#                         'price_subtotal': taxes['total_excluded'],
#                     })
#    
#                     
#             if line.move_id.iq_discount_type == 'amount':
#                 if line.iq_disc != 0 :
#                     
#                     discount =  line.iq_disc
#                     line.update({
#                         'price_subtotal': taxes['total_excluded'] - discount,
#                     })
#                 else:
#                     line.update({
#                         'price_subtotal': taxes['total_excluded'],
#                     })
#                         
                        
                        
                        
                        