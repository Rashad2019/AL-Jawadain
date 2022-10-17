# -*- coding: utf-8 -*-

from odoo import models, fields, api,SUPERUSER_ID,_,exceptions


class iq_inherit_saleorder(models.Model):
    _inherit = 'sale.order'
    
    
    iq_address = fields.Char(related='partner_id.street',string='Address')
    iq_phone = fields.Char(related='partner_id.phone',string='Phone')

    iq_discount_type = fields.Selection([('percent','Percentage'),('amount','Amount')],
                                        string='Discount Type',readonly=True,
                                        states={'draft': [('readonly',False)],'sent': [('readonly',False)]},
                                        default='percent')
    iq_discount_amount = fields.Float('Discount Amount',readonly=True,
                                      states={'draft': [('readonly',False)],'sent': [('readonly',False)]})

    @api.onchange('iq_discount_amount','iq_discount_type')
    def iq_get_discount(self):
        print("sssssss")
        if self.iq_discount_amount != 0:
            iq_count = 0
            line_disc = 0
            disc = 0
            for x in self.order_line:
                iq_count = iq_count + 1
            if self.iq_discount_type == 'percent':
                line_disc = self.iq_discount_amount
            else:
                line_disc = self.iq_discount_amount / iq_count

            for x in self.order_line:
                x.write({
                    'iq_disc': line_disc,
                    'iq_discount_type': self.iq_discount_type,
                })
