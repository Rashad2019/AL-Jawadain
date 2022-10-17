from odoo import api, fields, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    @api.model
    def _get_quants_action(self, domain=None, extend=False):
        ctx = dict(self.env.context or {})
        if not ctx.get('inventory_mode'):
            if self.env.user.assigned_warehouse_id and not self.user_has_groups('stock.group_stock_manager'):
                warehouse = self.env.user.assigned_warehouse_id
                domain += [('location_id','=',warehouse.lot_stock_id.id)]
        return super(StockQuant,self)._get_quants_action(domain)

