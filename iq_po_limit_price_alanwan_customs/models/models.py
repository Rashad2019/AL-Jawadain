# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError


class FRes_sale(models.TransientModel):
    _inherit = 'res.config.settings'
     
     
    limit_on_po_amount = fields.Boolean('Enable Limit On Purchase Amount')
    po_amount = fields.Float('Limit')
     
     
    def set_values(self):
        super(FRes_sale, self).set_values()
        config_parameters = self.env["ir.config_parameter"].sudo()
        for record in self:
            config_parameters.sudo().set_param("iq_po_limit_price_alanwan_customs.limit_on_po_amount", record.limit_on_po_amount)
            config_parameters.sudo().set_param("iq_po_limit_price_alanwan_customs.po_amount", record.po_amount)
 
    def get_values(self):
        res = super(FRes_sale, self).get_values()
        config_parameters = self.env["ir.config_parameter"].sudo()
        res.update(
            limit_on_po_amount=config_parameters.sudo().get_param("iq_po_limit_price_alanwan_customs.limit_on_po_amount", default=False),
             po_amount=config_parameters.sudo().get_param("iq_po_limit_price_alanwan_customs.po_amount", default=0),
        )
        return res
    
    
    
    
    
class FconfirmlimitPurchase(models.Model):
    _inherit = 'purchase.order'
    
    
    
    def button_confirm(self):
      
        if self.user_has_groups('iq_po_limit_price_alanwan_customs.f_popricelimitcaccess_group_id'):
            return super(FconfirmlimitPurchase, self).button_confirm()
        else:
            if self.env['ir.config_parameter'].sudo().get_param('iq_po_limit_price_alanwan_customs.limit_on_po_amount'):
                amount_limit = self.env['ir.config_parameter'].sudo().get_param('iq_po_limit_price_alanwan_customs.po_amount')
                print("amount_limit",amount_limit," self.amount_total", self.amount_total)
               
                if float(amount_limit) >= self.amount_total:
                    return super(FconfirmlimitPurchase, self).button_confirm()
                else:
                    raise UserError(_('لقد تم تجاوز الحد الاعلى الرجاء التواصل مع المدير  !!'))
                
            else:
                return super(FconfirmlimitPurchase, self).button_confirm()
                
