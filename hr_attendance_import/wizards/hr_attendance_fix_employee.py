# -*- coding: utf-8 -*-
# Copyright 2017 Artex Trading <informatica@artextrading.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, exceptions, models


class HrAttendanceFixEmployee(models.TransientModel):
    _name = 'hr.attendance.fix.employee'
    _description = 'Auto fix employee ID from Barcode'


    def button_wizard_hr_attendance_fix_employee(self):
        context = self.env.context
        if 'active_ids' not in context:
            raise exceptions.UserError('active_ids not defined')

        employee_obj = self.env['hr.employee']
        incidence_obj = self.env['hr.attendance.incidence']
        records = incidence_obj.browse(context['active_ids'])
        for item in records:
            employee = employee_obj.search([('barcode', '=', item.barcode)],
                                           limit=1)
            if employee and (employee.id != item.employee_id):
                item.write({'employee_id': employee.id})
