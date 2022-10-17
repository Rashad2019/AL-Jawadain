# -*- coding: utf-8 -*-
# from odoo import http


# class IqPoDiscountCustom(http.Controller):
#     @http.route('/iq_po_discount_custom/iq_po_discount_custom/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/iq_po_discount_custom/iq_po_discount_custom/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('iq_po_discount_custom.listing', {
#             'root': '/iq_po_discount_custom/iq_po_discount_custom',
#             'objects': http.request.env['iq_po_discount_custom.iq_po_discount_custom'].search([]),
#         })

#     @http.route('/iq_po_discount_custom/iq_po_discount_custom/objects/<model("iq_po_discount_custom.iq_po_discount_custom"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('iq_po_discount_custom.object', {
#             'object': obj
#         })
