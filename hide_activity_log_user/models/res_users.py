
from odoo import models, fields


class Users(models.Model):
    _inherit = 'res.users'

    hide_chatter = fields.Boolean(default=False)
    hide_chatter_on_products = fields.Boolean(default=True)
