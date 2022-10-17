from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    map_view = fields.Char(string='Map')