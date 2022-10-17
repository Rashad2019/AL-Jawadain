
from odoo import models
from odoo.addons.stock.models.stock_picking import Picking
import logging
_logger = logging.getLogger(__name__)


class StockPickingReturn(models.Model):
	_inherit = 'stock.picking'

	def button_validate_return(self,picking):
		res = Picking.button_validate(picking)
		return res

