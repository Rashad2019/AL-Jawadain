# -*- coding: utf-8 -*-

from odoo import models, fields, api

class employee_fields(models.Model):
    _inherit = 'hr.employee'
    elhadaf = fields.Char(string="Target", required=False, )
    perc_hadaf = fields.Char(string="Target Rate (%)", required=False, )
    sales_total = fields.Char(string="Sales Total", required=False, )
    perc_sales_total = fields.Char(string="Sales Rate (%)", required=False, )
    estehsal = fields.Float(string="Collectd Money", required=False, )
    perc_estehsal =fields.Selection(string="Collectd Money Rate(%)", selection=[('25', 0.025), ('5', 0.05),('75', 0.075),('1', .01),('2', .02) ], required=False, )
    total_estehsal = fields.Char(string="Total Collected Money", required=False, compute="_compute_total_estehsal")
    job_name = fields.Text(string="Job Name", required=False, )
    elahad = fields.Char(string="Custody", required=False, )
    instrument_no = fields.Char(string="Instrument No", required=False, )
    amount = fields.Char(string="amount", required=False, )
    notes = fields.Text(string="Notes", required=False, )
    wosolat_ids = fields.One2many(comodel_name="wosolat.wosolat", inverse_name="emp_ids", string="Receipts Entries", required=False, )
    solaf_ids = fields.One2many(comodel_name="solaf.solaf", inverse_name="emp_ids", string="Loans", required=False, )
    substitute_employee_id = fields.Many2one('hr.employee', 'Substitute employee')
    manager_user_id = fields.Many2one(related='parent_id.user_id', string="Manager User")

    @api.depends('estehsal','perc_estehsal')
    def _compute_total_estehsal(self):
        for rec in self:
            if rec.estehsal and rec.perc_estehsal:
                print(rec.perc_estehsal)

                if rec.perc_estehsal=='25':
                    rec.total_estehsal = .025 * rec.estehsal
                if rec.perc_estehsal=='5':
                    rec.total_estehsal = .05 * rec.estehsal
                if rec.perc_estehsal=='75':
                    rec.total_estehsal = .075 * rec.estehsal
                if rec.perc_estehsal=='1':
                    rec.total_estehsal = .01 * rec.estehsal
                if rec.perc_estehsal=='2':
                    rec.total_estehsal = .02 * rec.estehsal
            else:
                rec.total_estehsal = 0



class wosolat(models.Model):
    _name = 'wosolat.wosolat'
    from1 = fields.Float(string="From",  required=False, )
    to1 = fields.Float(string="To",  required=False, )
    date1 = fields.Date(string="Receipt Date", required=False, )
    emp_ids = fields.Many2one(comodel_name="hr.employee", string="", required=False, )

class solaf(models.Model):
    _name = 'solaf.solaf'
    solaf = fields.Char(string="Loan Amount", required=False, )
    kest = fields.Char(string="Monthly Installment", required=False, )

    date1 = fields.Date(string="Loan Receipt Date", required=False, )
    date2 = fields.Date(string="Loan End Date", required=False, )
    emp_ids = fields.Many2one(comodel_name="hr.employee", string="", required=False, )


class HRLeave(models.Model):
    _inherit = 'hr.leave'

    substitute_employee_id = fields.Many2one('hr.employee', 'Substitute employee')
    manager_user_id = fields.Many2one(related='employee_id.manager_user_id', string="Manager User")
