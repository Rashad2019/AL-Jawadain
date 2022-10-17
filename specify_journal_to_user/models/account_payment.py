from odoo import api, fields, models


class AccountPayment(models.Model):
    _inherit = "account.payment"


    @api.model
    def default_get(self, fields):
        res = super(AccountPayment,self).default_get(fields)
        if 'journal_id' in fields and self.env.user.assigned_journal_id:
            res['journal_id'] = self.env.user.assigned_journal_id.id
        return res

    def write(self, vals):
        # OVERRIDE
        if 'journal_id' not in vals and self.env.user.assigned_journal_id:
            vals['journal_id'] = self.env.user.assigned_journal_id
        res = super(AccountPayment, self).write(vals)
        return res

    @api.depends('journal_id', 'partner_id', 'partner_type', 'is_internal_transfer')
    def _compute_destination_account_id(self):
        self.destination_account_id = False
        for pay in self:
            if pay.is_internal_transfer:
                pay.destination_account_id = pay.journal_id.company_id.transfer_account_id
            elif pay.partner_type == 'customer':
                # Receive money from invoice or send money to refund it.
#                 if self.env.user.assigned_journal_id:
#                     print(self.env.user.assigned_journal_id)
#                     pay.destination_account_id = self.env.user.assigned_journal_id.default_account_id
                if pay.partner_id:
                    pay.destination_account_id = pay.partner_id.with_company(pay.company_id).property_account_receivable_id
                else:
                    pay.destination_account_id = self.env['account.account'].search([
                        ('company_id', '=', pay.company_id.id),
                        ('internal_type', '=', 'receivable'),
                    ], limit=1)
            elif pay.partner_type == 'supplier':
                # Send money to pay a bill or receive money to refund it.
                if pay.partner_id:
                    pay.destination_account_id = pay.partner_id.with_company(pay.company_id).property_account_payable_id
                else:
                    pay.destination_account_id = self.env['account.account'].search([
                        ('company_id', '=', pay.company_id.id),
                        ('internal_type', '=', 'payable'),
                    ], limit=1)


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    @api.depends('company_id', 'source_currency_id')
    def _compute_journal_id(self):
        for wizard in self:
            domain = [
                ('type', 'in', ('bank', 'cash')),
                ('company_id', '=', wizard.company_id.id),
            ]
            journal = None
            if self.env.user.assigned_journal_id:
                if wizard.source_currency_id and self.env.user.assigned_journal_id.currency_id and wizard.source_currency_id == self.env.user.assigned_journal_id.currency_id:
                    journal = self.env.user.assigned_journal_id
            if not journal and wizard.source_currency_id:
                journal = self.env['account.journal'].search(domain + [('currency_id', '=', wizard.source_currency_id.id)], limit=1)
            if not journal and not self.env.user.assigned_journal_id:
                journal = self.env['account.journal'].search(domain, limit=1)
            wizard.journal_id = journal
