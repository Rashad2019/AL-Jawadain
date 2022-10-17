from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    partner_type = fields.Selection([
        ('wholesale', 'Wholesale'),
        ('retail', 'Retail')], string="Customer Type")