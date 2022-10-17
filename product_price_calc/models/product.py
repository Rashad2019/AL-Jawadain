
from odoo import api, models, fields


class ProductPrice(models.Model):
    _inherit = 'product.template'

    profit = fields.Float(string="Profit")


    @api.onchange('standard_price','profit')
    def onchange_profit(self):
        profit_amount = float(self.profit if self.profit else 1 / 100) * float(self.standard_price if self.standard_price else 1)
        list_price = float(self.standard_price) + float(profit_amount)
        self.list_price = list_price