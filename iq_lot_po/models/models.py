# -*- coding: utf-8 -*-
from odoo import models, fields, api


class inheritiq_inherit_lot_po_lines(models.Model):
    _inherit = 'purchase.order.line'

    
    
    iq_lot_id = fields.Many2one('stock.production.lot',string='Lot ID/', copy=False)
    
    iq_lot_name = fields.Char(string="Lot Name")
    iq_lot_ex_date = fields.Datetime(string="Expiration Date")
    iq_lot_prod_date = fields.Datetime(string="Production Date")
    
#     @api.onchange("product_id")
#     def _onchange_product_id_set_lot_domain(self):
#         available_lot_ids = []
#         if self.product_id:
#             lots= self.env['stock.production.lot'].search([('product_id','=',self.product_id.id)])
#             if lots:
#                 for x in lots:
#                     available_lot_ids.append(x.id)
#        
#         return {"domain": {"iq_lot_no": [("id", "in", available_lot_ids)]}}
    
    
class inheritPurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def button_confirm(self):
        res = super(inheritPurchaseOrder, self).button_confirm()
        
        for picking_id in self.picking_ids:
            for move_id in picking_id.move_lines:
                for line in self.order_line:
                    if line == move_id.purchase_line_id:
                        if line.product_id.tracking == 'lot':
                            print("77777777777777777777",line.product_id.name,line.iq_lot_name)
                            
                            # to do :reminder if fill expiration date will update the old one in lot
                            if line.iq_lot_name:
                                lot_check = self.env['stock.production.lot'].search([('product_id','=',line.product_id.id),('name','=',line.iq_lot_name)])
                                if lot_check:
                                    
                                    if line.iq_lot_prod_date :
                                        print("line.iq_lot_prod_date77777777",line.iq_lot_prod_date)
                                        lot_check.sudo().write({
                                        
                                        'iq_prod_date': line.iq_lot_prod_date,
                                        })
                                    if line.iq_lot_ex_date :
                                        print("line.iq_lot_ex_date77777777",line.iq_lot_ex_date)
                                        lot_check.sudo().write({
                                        
                                        'expiration_date': line.iq_lot_ex_date,
                                        })    
                                        
                                    
                                    
                                    line.iq_lot_id = lot_check.id
                                else:
                                    new_lot = self.env['stock.production.lot'].create({
                                        'name': line.iq_lot_name,
                                         'product_id': line.product_id.id,
                                         'company_id': line.order_id.company_id.id,
                                        'iq_prod_date': line.iq_lot_prod_date,
                                        'expiration_date': line.iq_lot_ex_date, })
                                    line.iq_lot_id = new_lot.id
                            else:
                                line.iq_lot_id =False
                                
                        else:
                            print("8888888888888888888")
                            line.iq_lot_id =False
                            
                        move_id.set_pick_lot_no(line)
        return res
    
    
class StockMove(models.Model):
    _inherit = "stock.move"
    
      

    def set_pick_lot_no(self, line):
        if self.product_id.tracking == 'lot':
            lot_id = line.iq_lot_id
            if self.move_line_ids:
                for move_line_id in self.move_line_ids:
                    move_line_id.write({
                        'lot_id': lot_id.id,
                        'lot_name': lot_id.name,
                        'expiration_date': lot_id.expiration_date,
                        'iq_prod_date': lot_id.iq_prod_date,
                        'product_uom_qty': line.product_qty,
                        'qty_done': line.product_qty, 
                        'product_uom_id': self.product_id.uom_id.id,
                        'location_id': self.location_id.id, 
                        'location_dest_id': self.location_dest_id.id})
            else:
                self.env['stock.move.line'].create({
                    'lot_id': lot_id.id,
                    'lot_name': lot_id.name,
                    'expiration_date': lot_id.expiration_date,
                    'iq_prod_date': lot_id.iq_prod_date,
                    'product_uom_qty': line.product_qty,
                    'qty_done': line.product_qty,
                    'product_uom_id': self.product_id.uom_id.id,
                    'location_id': self.location_id.id,
                    'location_dest_id': self.location_dest_id.id,
                    'move_id': self.id,
                    'product_id': self.product_id.id
                })
#     
    
    
    
    
