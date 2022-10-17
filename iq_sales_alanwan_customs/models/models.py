# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class iq_sales_alanwan_customs(models.Model):
#     _name = 'iq_sales_alanwan_customs.iq_sales_alanwan_customs'
#     _description = 'iq_sales_alanwan_customs.iq_sales_alanwan_customs'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
