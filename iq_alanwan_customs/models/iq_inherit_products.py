from odoo import api, fields, models, _




class ProductProduct(models.Model):
    _inherit = "product.template"

    _sql_constraints = [
        ('name_uniq', 'unique(name)', "A Name can only be assigned to one product !"),
    ]