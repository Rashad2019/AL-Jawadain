# -*- coding: utf-8 -*-

from odoo import models, fields, api


class iq_inherit_users(models.Model):
    _inherit = 'res.users'


    f_recevielotnotfiy = fields.Boolean(string='Enable LOT Notification')
 
    
    
    
    
    
    
  
    
   
