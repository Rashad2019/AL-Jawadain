
from odoo import fields, models


class PartnerZone(models.Model):
    _name = "partner.zone"
    _description = "Partner zone"

    code = fields.Char()
    name = fields.Char(string="Zone Name", required=True)
    description = fields.Char(string="Description",translate=True)
    active = fields.Boolean(default=True)
