
from lxml import etree

from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    zone_id = fields.Many2many(
        comodel_name="partner.zone",
        string="Zone",
        ondelete="restrict",
        index=True,
    )