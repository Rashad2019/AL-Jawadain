
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    salespersons_customers_only = fields.Boolean('Salesperson Can Sell to Specified Customers Only',default=False)

    collection_by_balance = fields.Selection([
        # ('same_amount', 'Split evenly on overdue invoices'),
        ('older_all_overdue', 'Collect all overdue amounts, starting with the older invoices'),
        ('newer_all_overdue', 'Collect all overdue amounts, starting with the last invoices')],
        string='Collection by Balance Methods',default='older_all_overdue')

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        config_parameters = self.env["ir.config_parameter"].sudo()
        for record in self:
            config_parameters.sudo().set_param("smart_api.salespersons_customers_only",
                                               record.salespersons_customers_only)
            config_parameters.sudo().set_param("smart_api.collection_by_balance",
                                               record.collection_by_balance)
    def get_values(self):
        res = super(ResConfigSettings,self).get_values()
        config_parameters = self.env["ir.config_parameter"].sudo()
        res.update(
            salespersons_customers_only=config_parameters.sudo().get_param(
                "smart_api.salespersons_customers_only", default=False),
            collection_by_balance=config_parameters.sudo().get_param(
                "smart_api.collection_by_balance",default='older_all_overdue'),
        )
        return res