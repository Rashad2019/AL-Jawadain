# -*- coding: utf-8 -*-
# from odoo import http


# class ChangeDaysOnPayslip(http.Controller):
#     @http.route('/change_days_on_payslip/change_days_on_payslip/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/change_days_on_payslip/change_days_on_payslip/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('change_days_on_payslip.listing', {
#             'root': '/change_days_on_payslip/change_days_on_payslip',
#             'objects': http.request.env['change_days_on_payslip.change_days_on_payslip'].search([]),
#         })

#     @http.route('/change_days_on_payslip/change_days_on_payslip/objects/<model("change_days_on_payslip.change_days_on_payslip"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('change_days_on_payslip.object', {
#             'object': obj
#         })
