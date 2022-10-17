from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_invoice_print_salesperson(self):
        return self.env.ref('custom_invoice_report.account_invoice_small_custom').report_action(self)
