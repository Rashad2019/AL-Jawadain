# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import datetime

from odoo import api, fields, models,_




class ProductTemplate(models.Model):
    
    
    _inherit = 'product.template'
    
    iq_prod_date = fields.Datetime('Production Date')


class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    iq_prod_date = fields.Datetime('Production Date',related='product_tmpl_id.iq_prod_date')
    
    
    def _update_proddate_values(self, new_date):
        product_tmp = self.env['product.template'].search([('id','=',self.product_tmpl_id.id)])
        if new_date:
            product_tmp.write({ 'iq_prod_date': new_date,  })
            #self.write({ 'iq_prod_date': new_date,  })
            
            
            


            
            
    
    
    
class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'
    
    
    iq_prod_date = fields.Datetime('Production Date')
    
    
    def _update_proddate_values(self, new_date):
        print("dateeeeeeeeeeeeeeeee",new_date,self.name)
        if new_date:
            
            self.write({ 'iq_prod_date': new_date,  })
            
            
            
    
    
    

class StockMoveLine(models.Model):
    _inherit = "stock.move.line"
    
    
    iq_prod_date = fields.Datetime('Production Date')
    
    
    @api.onchange('iq_prod_date')
    def _onchange_prod_date(self):
        print("999999999date",self.iq_prod_date)
        if self.iq_prod_date:
            if not self.lot_id:
                self.product_id._update_proddate_values(self.iq_prod_date)
            else:
                self.lot_id._update_proddate_values(self.iq_prod_date)
                
             
    
    
    @api.onchange('product_id', 'product_uom_id')
    def _onchange_product_id(self):
        res = super(StockMoveLine, self)._onchange_product_id()
        if self.product_id.iq_prod_date:
                self.iq_prod_date = self.product_id.iq_prod_date
        else:
                self.iq_prod_date = fields.Datetime.today()
                
                
        return res
    

        
        
        
    
    @api.onchange('lot_id')
    def _onchange_lot_id(self):
        if not self.picking_type_use_existing_lots or not self.product_id.use_expiration_date:
            return
        if self.lot_id:
            self.iq_prod_date = self.lot_id.iq_prod_date
        else:
            if self.product_id.iq_prod_date:
                self.iq_prod_date = self.product_id.iq_prod_date
            else:
                self.iq_prod_date = fields.Datetime.today()
                
                
                
 

    def _assign_production_lot(self, lot):
        super()._assign_production_lot(lot)
        self.lot_id._update_proddate_values(self.iq_prod_date)
                
            
            

        
        
        
class StockMove(models.Model):
    _inherit = "stock.move"
   
   

    def _generate_serial_move_line_commands(self, lot_names, origin_move_line=None):
        """Override to add a default `prod date` into the move lines values."""
        move_lines_commands = super()._generate_serial_move_line_commands(lot_names, origin_move_line=origin_move_line)
        if self.product_id.iq_prod_date:
            date = self.product_id.iq_prod_date
            for move_line_command in move_lines_commands:
                move_line_vals = move_line_command[2]
                move_line_vals['iq_prod_date'] = date
                
                
        if self.lot_id.iq_prod_date:
            date = self.lot_id.iq_prod_date
            for move_line_command in move_lines_commands:
                move_line_vals = move_line_command[2]
                move_line_vals['iq_prod_date'] = date
                
                
        return move_lines_commands
    
    
    
class StockQuant(models.Model):
    _inherit = 'stock.quant'

    iq_prod_date = fields.Datetime(compute="get_prod_date", string="Production Date")
    
    def get_prod_date(self):
        for x in self :
            print("xxxxx",x)
            if x.lot_id:
                x.iq_prod_date =x.lot_id.iq_prod_date
            else:
                x.iq_prod_date =x.product_id.iq_prod_date
                
    

#     @api.model
#     def _get_inventory_fields_create(self):
#         """ Returns a list of fields user can edit when he want to create a quant in `inventory_mode`.
#         """
#         res = super()._get_inventory_fields_create()
#         res += ['iq_prod_date']
#         return res
# 
#     @api.model
#     def _get_inventory_fields_write(self):
#         """ Returns a list of fields user can edit when he want to edit a quant in `inventory_mode`.
#         """
#         res = super()._get_inventory_fields_write()
#         res += ['iq_prod_date']
#         return res

   
        
        
        
            
            
            
