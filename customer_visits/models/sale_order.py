
import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

from odoo.http import request
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    sell_by_phone = fields.Boolean('Sale by Phone',default=False)
    sale_method = fields.Selection(string='Sale Method',
        selection = [
            ('by_web',''),
            ('by_phone','Sell By Phone'),
            ('by_route','Sell By Route'),
                    ],default='by_web')
