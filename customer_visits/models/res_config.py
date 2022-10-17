
from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    location_distance_buffer = fields.Integer('Location Distance Buffer', default=0)


    def set_values(self):
        super(ResConfigSettings, self).set_values()
        config_parameters = self.env["ir.config_parameter"].sudo()
        for record in self:
            config_parameters.sudo().set_param("customer_visits.location_distance_buffer",
                                               record.location_distance_buffer)

    def get_values(self):
        res = super(ResConfigSettings,self).get_values()
        config_parameters = self.env["ir.config_parameter"].sudo()
        res.update(
            location_distance_buffer=config_parameters.sudo().get_param(
                "customer_visits.location_distance_buffer", default=0),
        )
        return res