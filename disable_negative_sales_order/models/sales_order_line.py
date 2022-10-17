
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    disable_negative_sales_orders = fields.Boolean('Disable Negative Sales Orders',default=True)

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        config_parameters = self.env["ir.config_parameter"].sudo()
        for record in self:
            config_parameters.sudo().set_param("disable_negative_sales_order.disable_negative_sales_orders",
                                               record.disable_negative_sales_orders)

    def get_values(self):
        res = super(ResConfigSettings,self).get_values()
        config_parameters = self.env["ir.config_parameter"].sudo()
        res.update(
            disable_negative_sales_orders=config_parameters.sudo().get_param(
                "disable_negative_sales_order.disable_negative_sales_orders", default=False),
        )
        return res


class SalesOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.model
    def create(self, vals):
        disable_negative_sales_orders = self.env['ir.config_parameter']\
            .sudo().get_param('disable_negative_sales_order.disable_negative_sales_orders')
        if disable_negative_sales_orders:
            if 'product_uom_qty' in vals and 'product_id' in vals and 'is_reward_line' not in vals:
                qty_available = 0
                if self.env.user.assigned_warehouse_id and not self.user_has_groups('stock.group_stock_manager'):
                    warehouse = self.env.user.assigned_warehouse_id
                    product = self.env['stock.quant'].search([('product_id', '=',vals['product_id']),('location_id', '=', warehouse.lot_stock_id.id)])
                    qty_available = product.quantity
                else:
                    product = self.env['product.product'].search([('id', '=', vals['product_id'])])
                    qty_available = product.qty_available
                if vals['product_uom_qty'] > qty_available:
                    raise UserError(_('لا يمكنك البيع بالسالب يرجى التواصل مع المسؤول'))
        return super(SalesOrderLine, self).create(vals)

    @api.model
    def write(self, values):
        disable_negative_sales_orders = self.env['ir.config_parameter']\
            .sudo().get_param('disable_negative_sales_order.disable_negative_sales_orders')
        if disable_negative_sales_orders:
            if 'product_uom_qty' in values and 'product_id' in values and 'is_reward_line' not in values:
                qty_available = 0
                if self.env.user.assigned_warehouse_id and not self.user_has_groups('stock.group_stock_manager'):
                    warehouse = self.env.user.assigned_warehouse_id
                    product = self.env['stock.quant'].search([('product_id', '=',values['product_id']),('location_id', '=', warehouse.lot_stock_id.id)])
                    qty_available = product.quantity
                else:
                    product = self.env['product.product'].search([('id', '=', values['product_id'])])
                    qty_available = product.qty_available
                if values['product_uom_qty'] > qty_available:
                    raise UserError(_('لا يمكنك البيع بالسالب يرجى التواصل مع المسؤول'))
        return super(SalesOrderLine, self).write(values)

    @api.onchange("product_uom_qty")
    def onchange_product_uom_qty(self):
        disable_negative_sales_orders = self.env['ir.config_parameter']\
            .sudo().get_param('disable_negative_sales_order.disable_negative_sales_orders')
        if disable_negative_sales_orders:
            if self.product_id and not self.is_reward_line:
                qty_available = 0
                if self.env.user.assigned_warehouse_id and not self.user_has_groups('stock.group_stock_manager'):
                    warehouse = self.env.user.assigned_warehouse_id
                    product = self.env['stock.quant'].search([('product_id', '=', self.product_id.id),('location_id', '=', warehouse.lot_stock_id.id)])
                    qty_available = product.quantity
                else:
                    product = self.env['product.product'].search([('id','=',self.product_id.id)])
                    qty_available = product.qty_available
                if self.product_uom_qty > qty_available:
                    raise UserError(_('لا يمكنك البيع بالسالب يرجى التواصل مع المسؤول'))
        if self._origin:
            product_uom_qty_origin = self._origin.read(["product_uom_qty"])[0]["product_uom_qty"]
        else:
            product_uom_qty_origin = 0

        if self.state == 'sale' and self.product_id.type in ['product',
                                                             'consu'] and self.product_uom_qty < product_uom_qty_origin:
            # Do not display this warning if the new quantity is below the delivered
            # one; the `write` will raise an `UserError` anyway.
            if self.product_uom_qty < self.qty_delivered:
                return {}
            warning_mess = {
                'title': _('Ordered quantity decreased!'),
                'message': _(
                    'You are decreasing the ordered quantity! Do not forget to manually update the delivery order if needed.'),
            }
            return {'warning': warning_mess}
        return {}