
from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)


class ProductPublicCategory(models.Model):
	_inherit = 'product.category'

	image = fields.Binary('Icon', attachment=True)

