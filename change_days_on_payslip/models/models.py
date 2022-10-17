# -*- coding: utf-8 -*-

from odoo import models, fields, api


class change_days_on_payslip(models.Model):
    _inherit = 'hr.payslip.worked_days'
    _description = 'change_days_on_payslip.change_days_on_payslip'
    number_of_days = fields.Float(string='Number of Days' , readonly='0')

    @api.onchange('number_of_days')
    def onchange_method(self):
        print(self.payslip_id.employee_id.resource_calendar_id.hours_per_day)
        s = self.payslip_id.employee_id.resource_calendar_id.hours_per_day
        self.number_of_hours =self.number_of_days*s
        wage= self.payslip_id.employee_id.contract_id.wage
        print(self.amount)
        self.amount = self.number_of_hours*(wage/(s*26))
        print( self.amount )
        y = self.number_of_hours*(wage/(s*26))
        print(y)

    @api.depends('is_paid', 'number_of_hours', 'payslip_id', 'payslip_id.normal_wage', 'payslip_id.sum_worked_hours')
    def _compute_amount(self):
        for worked_days in self:
            print('ahmed')
            # worked_days.amount = worked_days.payslip_id.normal_wage * worked_days.number_of_hours / (
            #             worked_days.payslip_id.sum_worked_hours or 1) if worked_days.is_paid else 0
            s = worked_days.payslip_id.employee_id.resource_calendar_id.hours_per_day

            wage = worked_days.payslip_id.employee_id.contract_id.wage
            worked_days.amount = worked_days.number_of_hours*(wage/(s*26))