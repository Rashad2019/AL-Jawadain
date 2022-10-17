# -*- coding: utf-8 -*-
# from odoo import http


# class IqAutoConfirmSalesAlanwanCustoms(http.Controller):
#     @http.route('/iq_auto_confirm_sales_alanwan_customs/iq_auto_confirm_sales_alanwan_customs/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/iq_auto_confirm_sales_alanwan_customs/iq_auto_confirm_sales_alanwan_customs/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('iq_auto_confirm_sales_alanwan_customs.listing', {
#             'root': '/iq_auto_confirm_sales_alanwan_customs/iq_auto_confirm_sales_alanwan_customs',
#             'objects': http.request.env['iq_auto_confirm_sales_alanwan_customs.iq_auto_confirm_sales_alanwan_customs'].search([]),
#         })

#     @http.route('/iq_auto_confirm_sales_alanwan_customs/iq_auto_confirm_sales_alanwan_customs/objects/<model("iq_auto_confirm_sales_alanwan_customs.iq_auto_confirm_sales_alanwan_customs"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('iq_auto_confirm_sales_alanwan_customs.object', {
#             'object': obj
#         })
