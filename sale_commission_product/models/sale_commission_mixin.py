

from odoo import _, api, fields, models


class SaleCommissionLineMixinInherit(models.AbstractModel):
    _inherit = "sale.commission.line.mixin"


    def _get_commission_amount(self, commission, subtotal, product, quantity):
        """Get the commission amount for the data given. It's called by
        compute methods of children models.

        This means the inheritable method for modifying the amount of the commission.
        """
        self.ensure_one()
        if product.commission_free or not commission or not product.agents:
            return 0.0
        if commission.amount_base_type == "net_amount":
            # If subtotal (sale_price * quantity) is less than
            # standard_price * quantity, it means that we are selling at
            # lower price than we bought, so set amount_base to 0
            subtotal = max([0, subtotal - product.standard_price * quantity])
        if commission.commission_type == "fixed":
            # return subtotal * (commission.fix_qty / 100.0)
            return quantity * commission.fix_qty
        elif commission.commission_type == "section":
            return commission.calculate_section(subtotal)

    @api.depends("agent_id")
    def _compute_commission_id(self):
        for record in self:
            record.commission_id = record.agent_id.commission_id

    def _prepare_agents_vals_partner(self, partner):
        """Utility method for getting agents creation dictionary of a partner."""
        return [(0, 0, self._prepare_agent_vals(partner))]