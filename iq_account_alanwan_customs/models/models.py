# -*- coding: utf-8 -*-

from odoo import models, fields, api,_

class iq_account_move_alanwan_customs(models.Model):
    _inherit = 'account.move'

    iq_balance_before = fields.Float(compute="_get_balance_before",store=True,readonly=True,string="Previous Balance")
    iq_balance_after = fields.Float(compute="_get_balance_after",string="Current Balance")

    @api.depends('partner_id')
    def _get_balance_before(self):
        for rec in self:
            rec.iq_balance_before = (rec.partner_id.credit - rec.partner_id.debit)

    @api.onchange('partner_id')
    def _get_balance_after(self):
        for rec in self:

            rec.iq_balance_after = rec.partner_id.credit - rec.partner_id.debit


class iq_account_alanwan_customs(models.Model):
    _inherit = 'account.payment'
    
    
    iq_balance_before = fields.Float(compute="_get_balance_before", store=True ,readonly=True, string = "Previous Balance")
    iq_balance_after = fields.Float(compute="_get_balance_after", string = "Current Balance")
    
#     iq_currency_rate= fields.Float("Currency Rate", compute='_compute_currency_rate', store=True, readonly=True,
#         help='The rate of the currency to the currency of rate applicable at the date of the move')
#     
#     
#     
# 
#     def _compute_currency_rate(self):
#         print("currrrrrrrrrrrrrrrr")
#         for move in self:
#             if move.date:
#                 
#                 rate = self.env['res.currency']._get_conversion_rate(move.company_id.currency_id, move.currency_id, move.company_id, move.date)
#                 
#                 if rate != 0 :
#                     move.iq_currency_rate = 1/rate
#                 else:
#                     move.iq_currency_rate = 1
                    
     
                        
                        
    @api.depends('partner_id')
    def _get_balance_before(self):
        print("111111111222222")
        for rec in self:
            print("dd",rec.partner_id.debit,"cc",rec.partner_id.credit,"aa",rec.amount)
               #  + (rec.amount*rec.iq_currency_rate)
            rec.iq_balance_before = (rec.partner_id.credit - rec.partner_id.debit)
                
            
            
    @api.onchange('partner_id')        
    def _get_balance_after(self):
        print("111111111")
        for rec in self:
            print("dd111",rec.partner_id.debit,"cc",rec.partner_id.credit,"aa",rec.amount)
         
                
            rec.iq_balance_after = rec.partner_id.credit - rec.partner_id.debit 


