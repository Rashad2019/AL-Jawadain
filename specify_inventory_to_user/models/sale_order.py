from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.onchange('user_id')
    def onchange_user_id(self):
        super().onchange_user_id()
        if self.env.user.assigned_warehouse_id:
            self.warehouse_id = self.env.user.assigned_warehouse_id
        else:
            self.warehouse_id = self.user_id.with_company(self.company_id.id)._get_default_warehouse_id().id
