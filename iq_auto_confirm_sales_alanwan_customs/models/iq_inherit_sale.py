# -*- coding: utf-8 -*-

from odoo import models, fields, api,SUPERUSER_ID,_,exceptions


class iq_confirminherit_saleorder(models.Model):
    _inherit = 'sale.order'
    
    


    def action_confirm(self):
        print("22222222222223333333333333333")
        
        
        for line in self.order_line:
            #if self.user_has_groups('iq_sales_alanwan_customs.f_salepersonaccess_group_id'):
            if line.product_id.tracking == 'lot':
                    if not line.iq_lot_no:
                        lot = self.env['stock.production.lot'].search([('product_id','=',line.product_id.id),('expiration_date','!=',False),('expiration_date','>=',self.date_order)],limit=1,order='expiration_date asc')
                        line.iq_lot_no = lot.id
                    
        res = super(iq_confirminherit_saleorder, self).action_confirm()
        imediate_move = self.env['stock.immediate.transfer']
        for order in self:

                warehouse = order.warehouse_id
                user = self.env.user
                if self.env.context and "user" in self.env.context:
                    user = self.env.context.get('user')
                if warehouse.iq_done_delivery and order.picking_ids: 
                    for picking in self.picking_ids:
                        if not picking.user_id:
                            picking.with_user(user).write({"user_id": user.id})

                        picking.with_user(user).action_assign()
                        picking.with_user(user).action_confirm()
                        for mv in picking.move_ids_without_package:
                            mv.quantity_done = mv.product_uom_qty


                        picking.with_user(user).button_validate()


                if warehouse.iq_done_invoice and not order.invoice_ids:
                    order.with_user(user)._create_invoices()
    
                if warehouse.iq_done_invoice and order.invoice_ids:
                    for invoice in order.invoice_ids:
                        invoice.with_user(user).action_post()

        return res  
    
    
    
    

            
        
