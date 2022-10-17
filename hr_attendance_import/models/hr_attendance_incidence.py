# -*- coding: utf-8 -*-
# Copyright 2017 Artex Trading <informatica@artextrading.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields, _
from odoo.exceptions import Warning as UserError


class HrAttendanceIncidence(models.Model):
    _name = 'hr.attendance.incidence'
    _description = 'Attendance Incidence'
    _sort = 'barcode,check_in,check_out'

    barcode = fields.Char(string='Badge ID',
                          help='ID used for employee identification.')

    employee_id = fields.Many2one('hr.employee',
                                  string='Employee',
                                  ondelete='cascade',
                                  index=True)

    check_in = fields.Datetime(string='Check In')

    check_out = fields.Datetime(string='Check Out')

    incidence = fields.Text(string='Incidence')

    def confirm_incidence2attendance(self, incidence_list):
        attendance_obj = self.env['hr.attendance']
        for item in incidence_list:
            if not item.employee_id or not item.check_in:
                continue

            # Check duplicate attendance
            attendance = attendance_obj.search(
                [('employee_id', '=', item.employee_id.id),
                 ('check_in', '=', item.check_in)], limit=1)

            if attendance:
                item.write(
                    {'incidence': _('An entry with the same time for the '
                                    'employee already exists!\n')+item.incidence}
                )
                continue

            # Check only one entry for employee in attendance
            if not item.check_out:
                attendance = attendance_obj.search([
                    ('employee_id', '=', item.employee_id.id),
                    ('check_out', '=', False),
                ], order='check_in desc', limit=1)

                if attendance:
                    item.write(
                        {_('There is already a entry without '
                                      'exit for the employee\n')+item.incidence}
                    )

            # Create new attendance and delete incidence
            attendance_obj.create(
                {'employee_id': item.employee_id.id,
                 'check_in': item.check_in,
                 'check_out': item.check_out})

            item.unlink()

    def button_confirm_incidence(self):
        self.confirm_incidence2attendance(self)
