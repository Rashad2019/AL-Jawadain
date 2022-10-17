
from odoo import models, api,_
from datetime import date, timedelta


class AccountInvoiceLine(models.Model):
    _inherit = "account.move.line"



    @api.depends("move_id.invoice_user_id")
    def _compute_agent_ids(self):
        self.agent_ids = False  # for resetting previous agents
        for record in self.filtered(
            lambda x: x.move_id.invoice_user_id and x.move_id.move_type[:3] == "out"
        ):
            if not record.commission_free and record.product_id:
                record.agent_ids = record._prepare_agents_vals_partner(
                    record.move_id.invoice_user_id.partner_id
                )

class AccountInvoiceLineAgentInherit(models.Model):
    _inherit = "account.invoice.line.agent"

    def _skip_settlement_based_achivement(self):
        """This function should return False if the commission can be paid.

        :return: bool
        """
        self.ensure_one()
        agent = self.invoice_id.invoice_user_id.partner_id
        agent_product = self.env['product.product.agent'].sudo().search(
            [('product_id','=',self.object_id.product_id.id),('agent','=',agent.id)],limit=1)
        if agent_product:
            agent_product._compute_target_achivement()
        if agent_product and agent_product[0] and agent_product[0].target_achivement >= agent_product[0].target_achivement_compute:
            return False;
        return True



class SaleCommissionMakeSettleInherit(models.TransientModel):
    _inherit = "sale.commission.make.settle"

    def action_settle(self):
        print('action_settle')
        self.ensure_one()
        agent_line_obj = self.env["account.invoice.line.agent"].sudo()
        settlement_obj = self.env["sale.commission.settlement"]
        settlement_line_obj = self.env["sale.commission.settlement.line"]
        settlement_ids = []

        if self.agent_ids:
            agents = self.agent_ids
        else:
            agents = self.env["res.partner"].search([("agent", "=", True)])
        date_to = self.date_to
        for agent in agents:
            date_to_agent = self._get_period_start(agent, date_to)
            # Get non settled invoices
            agent_lines = agent_line_obj.search(
                [
                    ("invoice_date", "<", date_to_agent),
                    ("agent_id", "=", agent.id),
                    ("settled", "=", False),
                ],
                order="invoice_date",
            )
            for company in agent_lines.mapped("company_id"):
                agent_lines_company = agent_lines.filtered(
                    lambda r: r.object_id.company_id == company
                )
                pos = 0
                sett_to = date(year=1900, month=1, day=1)
                while pos < len(agent_lines_company):
                    line = agent_lines_company[pos]
                    pos += 1
                    if line._skip_settlement():
                        continue
                    if line._skip_settlement_based_achivement():
                        continue
                    if line.invoice_date > sett_to:
                        sett_from = self._get_period_start(agent, line.invoice_date)
                        sett_to = self._get_next_period_date(
                            agent,
                            sett_from,
                        ) - timedelta(days=1)
                        settlement = self._get_settlement(
                            agent, company, sett_from, sett_to
                        )
                        if not settlement:
                            settlement = settlement_obj.create(
                                self._prepare_settlement_vals(
                                    agent, company, sett_from, sett_to
                                )
                            )
                        settlement_ids.append(settlement.id)
                    settlement_line_obj.create(
                        {
                            "settlement_id": settlement.id,
                            "agent_line": [(6, 0, [line.id])],
                        }
                    )
        # go to results
        if len(settlement_ids):
            return {
                "name": _("Created Settlements"),
                "type": "ir.actions.act_window",
                "views": [[False, "list"], [False, "form"]],
                "res_model": "sale.commission.settlement",
                "domain": [["id", "in", settlement_ids]],
            }
