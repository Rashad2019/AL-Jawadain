# # -*- coding: utf-8 -*-
# from odoo import http
# from odoo.http import Controller, route, request, Response


# class IqConfirmPoAlanwanCustoms(http.Controller):
#     @http.route('/iq_confirm_po_alanwan_customs/iq_confirm_po_alanwan_customs/', auth='public')
#     def index(self, **kw):
#         return request.env['ir.module.module'].update_list()

#     @http.route('/iq_confirm_po_alanwan_customs/iq_confirm_po_alanwan_customs/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('iq_confirm_po_alanwan_customs.listing', {
#             'root': '/iq_confirm_po_alanwan_customs/iq_confirm_po_alanwan_customs',
#             'objects': http.request.env['iq_confirm_po_alanwan_customs.iq_confirm_po_alanwan_customs'].search([]),
#         })

#     @http.route('/iq_confirm_po_alanwan_customs/iq_confirm_po_alanwan_customs/objects/<model("iq_confirm_po_alanwan_customs.iq_confirm_po_alanwan_customs"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('iq_confirm_po_alanwan_customs.object', {
#             'object': obj
#         })
