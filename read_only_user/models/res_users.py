
from odoo import models, fields


class Users(models.Model):
    _inherit = 'res.users'

    read_only_user = fields.Boolean(default=False)

    def set_read_only_user(self):
        for user in self:
            user.read_only_user = True

    def unset_read_only_user(self):
        for user in self:
            user.read_only_user = False
