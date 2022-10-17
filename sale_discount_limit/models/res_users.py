from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Users(models.Model):
    _inherit = "res.users"

    max_discount = fields.Float(string='Max Allowed Discount',default=20)

    @api.constrains('max_discount')
    def _check_max_discount(self):
        if self.filtered(lambda user: user.max_discount < 0 or user.max_discount > 100):
            raise ValidationError(_('Max Allowed Discount should be between 1-100'))
