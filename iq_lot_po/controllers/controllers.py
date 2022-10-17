# -*- coding: utf-8 -*-
# from odoo import http


# class IqLotPo(http.Controller):
#     @http.route('/iq_lot_po/iq_lot_po/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/iq_lot_po/iq_lot_po/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('iq_lot_po.listing', {
#             'root': '/iq_lot_po/iq_lot_po',
#             'objects': http.request.env['iq_lot_po.iq_lot_po'].search([]),
#         })

#     @http.route('/iq_lot_po/iq_lot_po/objects/<model("iq_lot_po.iq_lot_po"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('iq_lot_po.object', {
#             'object': obj
#         })
