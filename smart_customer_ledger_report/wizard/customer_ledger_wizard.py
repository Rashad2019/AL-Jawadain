
from odoo import api, fields, models,_

class CustomerLedgerWizard(models.TransientModel):
    _name = 'customer.ledger.wizard'
    _description = 'Customer Ledger Wizard'

    user_id = fields.Many2one('res.users',string='Salesperson',
               domain=lambda self: [("groups_id","=",
                             self.env.ref("sales_team.group_sale_salesman").id)
                                    ]
                               )

    def action_show_customer_ledger(self):
        return {
            'name': _('Customer Ledger'),
            'view_mode': 'tree',
            'domain': [('user_id', '=', self.user_id.id),('customer_rank','>',0)],
            'res_model': 'res.partner',
            'search_view_id':self.env.ref('smart_customer_ledger_report.view_res_customer_ledger').id,
            'view_id': self.env.ref('smart_customer_ledger_report.customer_ladger_list_view_custom').id,
            'type': 'ir.actions.act_window',
            'context': {'create': False, 'active_test': False,'search_default_customer':1,'res_partner_search_mode': 'customer', 'default_is_company': True},
        }