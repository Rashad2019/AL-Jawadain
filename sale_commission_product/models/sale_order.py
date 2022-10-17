

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    #
    # @api.onchange("product_id")
    # def product_id_change(self):
    #
    #     res = super(SaleOrderLine, self).product_id_change()
    #
    #     if self.order_id.partner_id and self.product_id:
    #         agent_list = []
    #         partner = self.env["res.partner"].browse(self.order_id.partner_id)
    #
    #         for self.agent in partner.agents:
    #             # default commission_id for agent
    #             # commission_id = agent.commission.id
    #             commission_id = False
    #             commission_id_product = self.env["product.product.agent"]\
    #                 .get_commission_id_product(self.product_id, self.agent)
    #             if commission_id_product:
    #                 commission_id = commission_id_product
    #
    #             agent_list.append({'agent': self.agent.id,
    #                                'commission': commission_id
    #                                })
    #
    #             res['value']['agents'] = [(0, 0, x) for x in agent_list]
    #
    #     return res

    @api.depends("order_id.user_id")
    def _compute_agent_ids(self):
        self.agent_ids = False  # for resetting previous agents
        for record in self.filtered(lambda x: x.order_id.partner_id):
            if not record.commission_free:
                record.agent_ids = record._prepare_agents_vals_partner(
                    record.order_id.user_id.partner_id
                )

    def _prepare_invoice_line(self, **optional_values):
        vals = super()._prepare_invoice_line(**optional_values)
        vals["agent_ids"] = [
            (0, 0, {"agent_id": x.agent_id.id, "commission_id": x.commission_id.id})
            for x in self.agent_ids
        ]
        return vals