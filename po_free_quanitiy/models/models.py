from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    free_qty = fields.Float(string='Free Quantity')


    @api.depends('invoice_lines.move_id.state', 'invoice_lines.quantity', 'qty_received', 'product_uom_qty', 'order_id.state')
    def _compute_qty_invoiced(self):
        res = super(PurchaseOrderLine,self)._compute_qty_invoiced()
        for line in self:
            # compute qty_to_invoice
            if line.order_id.state in ['purchase', 'done']:
                if line.product_id.purchase_method == 'purchase':
                    line.qty_to_invoice = line.product_qty - line.qty_invoiced
                elif line.product_id.purchase_method == 'receive' and line.free_qty > 0 and line.qty_received > 0:
                    line.qty_to_invoice = line.qty_received - line.qty_invoiced - line.free_qty
                else:
                    line.qty_to_invoice = line.qty_received - line.qty_invoiced
            else:
                line.qty_to_invoice = 0

    def _prepare_stock_move_vals(self, picking, price_unit, product_uom_qty, product_uom):
        self.ensure_one()
        print('_prepare_stock_move_vals')
        res = super(PurchaseOrderLine,self)._prepare_stock_move_vals(picking, price_unit, product_uom_qty, product_uom)
        if self.free_qty > 0:
            res.update({
                'product_uom_qty': self.product_uom_qty + self.free_qty,
            })
        return res

