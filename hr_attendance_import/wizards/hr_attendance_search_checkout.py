# -*- coding: utf-8 -*-
# Copyright 2017 Artex Trading <informatica@artextrading.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HrAttendanceSearchCheckOutLine(models.TransientModel):
    _name = 'hr.attendance.search.checkout.line'

    wizard_id = fields.Many2one(comodel_name='hr.attendance.search.checkout',
                                string='Wizard Id')

    employee_id = fields.Many2one('hr.employee',
                                  string='Employee',
                                  ondelete='cascade',
                                  index=True)

    check_in = fields.Datetime(string='Check In')

    check_out = fields.Datetime(string='Check Out')

    checkin_id = fields.Many2one('hr.attendance.incidence',
                                 string='Check IN ')

    checkout_id = fields.Many2one('hr.attendance.incidence',
                                  string='Check OUT')


class HrAttendanceSearchCheckOut(models.TransientModel):
    _name = 'hr.attendance.search.checkout'
    _description = 'Auto search check out of employee check in'

    line_ids = fields.One2many(
        comodel_name='hr.attendance.search.checkout.line',
        inverse_name='wizard_id',
        string='Attendance Lines')

    @api.model
    def default_get(self, _fields):
        result = super(HrAttendanceSearchCheckOut, self).default_get(_fields)
        active_ids = self.env.context.get('active_ids')
        active_model = self.env.context.get('active_model')

        if active_model == 'hr.attendance.incidence' and active_ids:
            incidence_obj = self.env['hr.attendance.incidence']
            records = incidence_obj.browse(active_ids)
            values = []

            # Search check_out for all checks_in selected
            for item in records:
                if not item.employee_id or not item.check_in or item.check_out:
                    continue

                incidence_out = incidence_obj.search([
                    ('employee_id', '=', item.employee_id.id),
                    ('check_in', '=', False),
                    ('check_out', '>', item.check_in)
                ], order='check_out asc', limit=1)

                if incidence_out:
                    values.append((0, 0, {
                        'wizard_id': self.id,
                        'employee_id': item.employee_id.id,
                        'check_in': item.check_in,
                        'check_out': incidence_out.check_out,
                        'checkin_id': item.id,
                        'checkout_id': incidence_out.id
                    }))

            # Load result into wizard lines
            if values:
                result.update({'line_ids': values})

        return result


    def button_wizard_hr_attendance_search_checkout(self):
        # Join check_in & check_out for selected incidence
        incidence_obj = self.env['hr.attendance.incidence']
        if self.line_ids:
            for item in self.line_ids:
                record = incidence_obj.browse(item.checkin_id.id)
                record.write({'check_out': item.check_out})

            # Delete old check_out incidence
            self.line_ids.mapped('checkout_id').unlink()

            # Confirm incidence with check_in & check_out
            incidence_obj.confirm_incidence2attendance(
                self.line_ids.mapped('checkin_id'))
