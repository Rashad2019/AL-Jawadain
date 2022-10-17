
from odoo import api, fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    salesperson_ids = fields.Many2many('res.users', string='SalesPersons',check_company=True)

    @api.model_create_multi
    def create(self, vals_list):
        # code
        for values in vals_list:
            if 'user_id' in values and 'salesperson_ids' in values:
                if values['salesperson_ids'] == [(6, 0, [])]:
                    values['salesperson_ids'] = [(6, 0, [values['user_id']])]
        return super(Partner, self).create(vals_list)


class PartnerUpdateSalesPersonWizard(models.TransientModel):
    _name = "partner.update.salesperson"
    _description = "Update the salesperson for multi partners"

    user_id = fields.Many2one('res.users',string='Salesperson',
               domain=lambda self: [("groups_id","=",
                             self.env.ref("sales_team.group_sale_salesman").id)
                                    ]
                               )


    def update_partner_salesperson(self):

        partners = self.env['res.partner'].browse(self._context.get('active_ids'))
        for partner in partners:
            partner.user_id = self.user_id
            partner.salesperson_ids = [(4, self.user_id.id)]
