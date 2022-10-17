
from odoo import api, fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('reject', 'Reject')], string='State', default='draft', tracking=1)

    def button_approve(self):
        self.write({"state": "approved"})

    def button_reject(self):
        self.write({"state": "reject"})

    @api.model_create_multi
    def create(self, vals_list):
        # code
        return super(Partner, self).create(vals_list)

    def write(self, vals):
        # code
        return super(Partner, self).write(vals)