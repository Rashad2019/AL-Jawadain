
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    partner_id = fields.Many2one(
        'res.partner', string='Customer', readonly=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        required=True, change_default=True, index=True, tracking=1,
        domain="['|', '&', ('company_id', '=', False), ('state','=','approved'),'&',('company_id', '=', company_id),('state','=','approved')]")


    @api.model
    def create(self, vals):
        if 'partner_id' in vals:
            partner = self.env['res.partner'].search([('id', '=', vals['partner_id'])])
            if partner and partner.state != 'approved':
                raise ValidationError("Customer Need to be Approved by Sales Manager ")
        return super(SaleOrder, self).create(vals)
