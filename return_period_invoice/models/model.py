from odoo import models, fields, api, _

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    no_of_days_to_return = fields.Integer('Return Period',default=15)

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        config_parameters = self.env["ir.config_parameter"].sudo()
        for record in self:
            config_parameters.sudo().set_param("return_period_invoice.no_of_days_to_return",
                                               record.no_of_days_to_return)

    def get_values(self):
        res = super(ResConfigSettings,self).get_values()
        config_parameters = self.env["ir.config_parameter"].sudo()
        res.update(
            no_of_days_to_return=config_parameters.sudo().get_param(
                "return_period_invoice.no_of_days_to_return", default=15),
        )
        return res


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _default_no_of_days_to_return(self):
        no_of_days_to_return = self.env['ir.config_parameter'] \
            .sudo().get_param('return_period_invoice.no_of_days_to_return')
        return no_of_days_to_return if no_of_days_to_return else 15

    no_of_days_to_return = fields.Integer(string='Return Period per Days',default=_default_no_of_days_to_return)

