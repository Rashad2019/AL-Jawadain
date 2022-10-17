# -*- coding: utf-8 -*-
# Copyright 2017 Artex Trading <informatica@artextrading.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import Warning as UserError
import base64
import csv
import io
from datetime import datetime


class HrAttendanceImport(models.TransientModel):
    _name = 'hr.attendance.import'
    _description = 'Import attendance'

    data = fields.Binary(string='File', required=True)

    name = fields.Char(string='Filename', readonly=True)

    delimeter = fields.Char(string='Delimeter', default=',', required=True)

    fieldname_header = fields.Boolean(
        string='First line contains field names',
        default=True)

    lineterminator = fields.Selection([
        ('\r\n', 'Windows'),
        ('\r', 'Linux/Mac')],
        string='Line Terminator',
        default='\r\n',
        required=True)

    input_format = fields.Selection([
        ('moviment',
         'Alternate movement: Employee, Type(Input/Output), Datetime'),
        ('attendance',
         'Assistance completed: Employee, Datetime Input, Datetime Output')],
        string='Input Format',
        default='moviment',
        required=True)

    employee_id_format = fields.Selection([
        ('id', 'Employee ID'),
        ('barcode', 'Badge ID')],
        string="Employee ID format",
        default='barcode',
        required=True)

    def _attendance_from_csv(self, reader):
        # Get models pointers
        incidence_obj = self.env['hr.attendance.incidence']
        attendance_obj = self.env['hr.attendance']
        employee_obj = self.env['hr.employee']

        # Main process
        for index, row in enumerate(reader):
            if self.fieldname_header and (index == 0):
                continue

            # Init and load CSV row data
            employee_code, check_in, check_out = row
            values = {}

            # Verify Datetime data
            try:
                values['check_in'] = fields.Datetime.from_string(check_in)
                values['check_out'] = fields.Datetime.from_string(check_out)
            except:
                values['incidence'] += _('Datetime format incorrect!\n')

            # Search for Employee ID
            if employee_code:
                employee = employee_obj.search(
                    [(self.employee_id_format, '=', employee_code)], limit=1)

                if employee:
                    values['barcode'] = employee.barcode
                    values['employee_id'] = employee.id
                else:
                    values['incidence'] += _('The Employee code is incorrect!\n')

            else:
                values['incidence'] += _('Employee/Badge ID is missing!\n')

            # Save data into DB
            if values['incidence']:
                values['barcode'] = employee_code
                values['employee_id'] = False
                values['incidence'] += ', '.join(row)
                incidence_obj.create(values)
            else:
                attendance_obj.create(values)

    def _movements_from_csv(self, reader):
        import pdb

        # Get models pointers
        incidence_obj = self.env['hr.attendance.incidence']
        attendance_obj = self.env['hr.attendance']
        employee_obj = self.env['hr.employee']
        attendance_lst = []

        # Read data from CSV process
        for index, row in enumerate(reader):
            if self.fieldname_header and (index == 0):
                continue

            # Init and load CSV row data
            print(row)
            employee_code, date_str, time_str , type_movement = row
            date_movement = date_str + " " + time_str
            values = {}
            values['incidence'] = ''

            # Verify Datetime data
            try:

                # print(date_movement)
                date_movement = datetime.strptime(date_movement,'%m/%d/%Y %H:%M:%S')
                print(date_movement)
            except:
                values['incidence'] += _('Datetime format incorrect!\n')

            # Search for Employee ID
            employee = employee_obj.search(
                [(self.employee_id_format, '=', employee_code)], limit=1)

            if not employee:
                values['incidence'] += _('The Employee code is incorrect!\n')

            # Save data into Array
            if values['incidence']:
                values['barcode'] = employee_code
                values['employee_id'] = False
                values['incidence'] += ', '.join(row)

                if type_movement == 'Check In':
                    values['check_in'] = date_movement.strftime("%Y-%m-%d %H:%M:%S")
                elif type_movement == 'Break Out':
                    values['check_in'] = date_movement.strftime("%Y-%m-%d %H:%M:%S")
                elif type_movement == 'Check Out':
                    values['check_out'] = date_movement.strftime("%Y-%m-%d %H:%M:%S")
                elif type_movement == 'Break Out':
                    values['check_out'] = date_movement.strftime("%Y-%m-%d %H:%M:%S")
                print(values)
                incidence_obj.create(values)
            else:
                attendance_lst.append({'employee_id': employee.id,
                                       'date_movement': date_movement.strftime("%Y-%m-%d %H:%M:%S"),
                                       'type_movement': type_movement})
        # There're new records
        if len(attendance_lst) > 0:
            # First sort list of movements
            def _attendance_sort(_movement):
                return str(_movement['employee_id'])\
                    + _movement['date_movement']\
                    + _movement['type_movement']

            attendance_lst.sort(key=_attendance_sort)

            # Main process
            employee_id = 0
            date_movement = False
            type_movement = ''
            # pdb.set_trace()
            for movement in attendance_lst:
                print(movement)
                if movement['employee_id'] != employee_id:
                    if employee_id > 0:
                        if date_movement:
                            # last record without save always is entry
                            attendance_obj.create(
                                {'employee_id': employee_id,
                                'check_in': date_movement})

                    employee_id = movement['employee_id']
                    date_movement = movement['date_movement']
                    type_movement = movement['type_movement']

                    # Check first movement for new employee
                    # if it's an output there must be an earlier entry
                    if type_movement == 'Check Out':
                        attendance = attendance_obj.search([
                            ('employee_id', '=', employee_id),
                            ('check_in', '<=', date_movement),
                            ('check_out', '=', False),
                        ], order='check_in desc', limit=1)

                        if attendance:
                            # TODO: Check if more 24h diference between entry and exit
                            attendance.write({'check_out': date_movement})
                        else:
                            incidence_obj.create(
                                {'employee_id': movement['employee_id'],
                                 'check_out': date_movement,
                                 'incidence': _('Missing pre-attendance entry!')})

                        date_movement = False
                        type_movement = ''
                    continue

                # Check if new movement is compatible with previous one
                if type_movement == movement['type_movement']:
                    if movement['type_movement'] == 'Check In':
                        incidence_obj.create(
                            {'employee_id': movement['employee_id'],
                             'check_in': date_movement,
                             'incidence': _('Found entry without exit!')})
                    else:
                        incidence_obj.create(
                            {'employee_id': movement['employee_id'],
                             'check_out': date_movement,
                             'incidence': _('Found exit without entry!')})
                    continue

                # If it is a new entry, we save the data until the next move.
                # If it's an output we record the assistance
                if movement['type_movement'] == "Check In":
                    date_movement = movement['date_movement']
                    type_movement = movement['type_movement']
                    continue
                elif not type_movement:              # Exit without Entry
                    incidence_obj.create(
                        {'employee_id': employee_id,
                         'check_out': date_movement,
                         'incidence': _('Found exit without entry!')})
                else:
                    attendance_obj.create(
                        {'employee_id': employee_id,
                         'check_in': date_movement,
                         'check_out': movement['date_movement']})
                date_movement = False
                type_movement = ''


    def button_wizard_hr_attendance_import(self):
        """Load Attendance data from the CSV file."""
        self.ensure_one()

        if not self.data:
            raise UserError(_('You need to select a file!'))

        # Decode and read file data
        data = base64.b64decode(self.data)
        file_input = io.StringIO(data.decode("utf-8","ignore"))
        file_input.seek(0)
        reader = csv.reader(file_input,
                            delimiter='\t',
                            lineterminator=str(self.lineterminator))

        if self.input_format == 'moviment':
            self._movements_from_csv(reader)
        else:
            self._attendance_from_csv(reader)
