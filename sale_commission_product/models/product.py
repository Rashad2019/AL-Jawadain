

from odoo import api, fields, models
from datetime import date, timedelta


class ProductProduct(models.Model):
    _inherit = 'product.product'

    agents = fields.One2many(
        string="Agents & commissions",
        comodel_name='product.product.agent', inverse_name='product_id',
        copy=True, readonly=True)


class ProductProductAgent(models.Model):
    _name = 'product.product.agent'

    def _get_period_start(self, agent, date_to):
        if agent.settlement == "monthly":
            return date(month=date_to.month, year=date_to.year, day=1)
        elif agent.settlement == "biweekly":
            if date_to.day >= 16:
                return date(month=date_to.month, year=date_to.year, day=16)
            else:
                return date(month=date_to.month, year=date_to.year, day=1)
        elif agent.settlement == "quaterly":
            # Get first month of the date quarter
            month = (date_to.month - 1) // 3 * 3 + 1
            return date(month=month, year=date_to.year, day=1)
        elif agent.settlement == "semi":
            if date_to.month > 6:
                return date(month=7, year=date_to.year, day=1)
            else:
                return date(month=1, year=date_to.year, day=1)
        elif agent.settlement == "annual":
            return date(month=1, year=date_to.year, day=1)


    def get_commission_id_product(self, product, agent):
        commission_id = False
        # commission_id for all agent
        # for commission_all_agent in self.search([('product_id', '=', product), ('agent', '=', False)]):
        #     commission_id = commission_all_agent.commission.id
        # commission_id for agent
        for product_agent_id in self.search(
                [('product_id', '=', product), ('agent', '=', agent.id)]):
                    commission_id = product_agent_id.commission.id
        return commission_id

    product_id = fields.Many2one(
        comodel_name="product.product",
        required=True,
        ondelete="cascade",
        string="")
    agent = fields.Many2one(
        comodel_name="res.partner", required=False,
        domain="[('agent', '=', True)]")
    commission = fields.Many2one(
        comodel_name="sale.commission",related='agent.commission_id', required=True)
    target = fields.Float(string="Target Quantity")

    @api.depends("agent", "target","product_id")
    def _compute_target_achivement(self):
        for record in self:
            if record.agent.salesman_as_agent and record.agent.commission_id:
                action_date_only = fields.date.today()
                invoice_date = self._get_period_start(record.agent,action_date_only)
                target = record.target
                if target <= 0:
                    target = 0
                # domain = [('settled','=',False),('agent_id','=',record.agent.id),('invoice_date','<',invoice_date)]
                domain = [('settled','=',False),('agent_id','=',record.agent.id)]
                invoice_lines = self.env['account.invoice.line.agent'].search(domain)
                sum_target_achivement = sum(invoice_lines.filtered(lambda m: m.object_id.product_id == record.product_id).mapped("object_id.quantity"))
                if sum_target_achivement > 0:
                    record.target_achivement = sum_target_achivement / target
                else:
                    record.target_achivement = 0
            else:
                record.target_achivement
    target_achivement = fields.Float(string="Target Achievement",help='Target Achievement based on Agent settlement',compute=_compute_target_achivement)

    target_achivement_compute = fields.Float(string="Compute Commission Based Achievement Rate",help='Commission Compute When Target Rate')


    def name_get(self):
        res = []
        for record in self:
            name = "%s: %s" % (record.agent.name, record.commission.name)
            res.append((record.id, name))
        return res

    _sql_constraints = [
        ('unique_agent', 'UNIQUE(product_id, agent)',
         'You can only add one time each agent.')
    ]
