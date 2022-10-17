# -*- coding: utf-8 -*-

from odoo import models, fields, api


class iq_inventory_alanwan_customs(models.Model):
    _inherit = 'product.template'
    
    
    def write(self, vals):
        print("11111111111111111")
        if vals.get('name'):
            self.message_post(body="Name Modified:  "+self.name+" --> "+ vals.get('name'))
            
        if vals.get('list_price'):
            self.message_post(body="SalesPrice Modified:  "+str(self.list_price)+" --> "+ str(vals.get('list_price')))
            
            
        if vals.get('standard_price'):
            self.message_post(body="Cost Modified :  "+str(self.standard_price)+" --> "+ str(vals.get('standard_price')))
            
            
        res = super(iq_inventory_alanwan_customs, self).write(vals)
        return res
