
from odoo import models, fields, api
from datetime import datetime, timedelta


class iq_inheritlots(models.Model):
    _inherit = 'stock.production.lot'
     
     
    def name_get(self):
        result = []
 
        for branch in self:
                print("11111",branch.name)
                if branch.expiration_date:
                    ex_date = str(branch.expiration_date)
                    print("ex_date",ex_date)
                else:
                    ex_date = ''
 
                if ex_date != '':
                    name = branch.name + (branch.id and (' - ' + ex_date) or '')
                else:
                    name = branch.name 
                    
                print("11111name",name)
                result.append((branch.id, name))
           
        print("result",result)        
        return result




class iq_inheritlot_sales(models.Model):
    _inherit = 'sale.order.line'
    
    iq_lot_no = fields.Many2one('stock.production.lot',string='رقم التشغيله', copy=False)

    @api.onchange("product_id")
    def product_id_change(self):
        res = super().product_id_change()
        self.iq_lot_no = False
        return res

    @api.onchange("product_id")
    def _onchange_product_id_set_lot_domain(self):
        available_lot_ids = []
        if self.order_id.warehouse_id and self.product_id:
            location = self.order_id.warehouse_id.lot_stock_id
            quants = self.env["stock.quant"].read_group(
                [
                    ("product_id", "=", self.product_id.id),
                    ("location_id", "child_of", location.id),
                    ("quantity", ">", 0),
                    ("lot_id", "!=", False),
                ],
                ["lot_id"],
                "lot_id",
            )
            available_lot_ids = [quant["lot_id"][0] for quant in quants]
        self.iq_lot_no = False
        return {"domain": {"iq_lot_no": [("id", "in", available_lot_ids)]}}
    
    
class StockMove(models.Model):
    _inherit = "stock.move"

    def _update_reserved_quantity(
        self,
        need,
        available_quantity,
        location_id,
        lot_id=None,
        package_id=None,
        owner_id=None,
        strict=True,
    ):
        
        print("looooooooooooooot")
        #if self._context.get("sol_lot_id"):
         #   print("111111lottttt")
        if self.sale_line_id.iq_lot_no:
            lot_id = self.sale_line_id.iq_lot_no
        return super()._update_reserved_quantity(
            need,
            available_quantity,
            location_id,
            lot_id=lot_id,
            package_id=package_id,
            owner_id=owner_id,
            strict=strict,
        )

    def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
        vals = super()._prepare_move_line_vals(
            quantity=quantity, reserved_quant=reserved_quant
        )
        if reserved_quant and self.sale_line_id.iq_lot_no:
            vals["lot_id"] = self.sale_line_id.iq_lot_no.id
        return vals
    
    
    
    
    