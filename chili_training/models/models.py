# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Training(models.Model):
    _name = "hr.training"
    _description = "Training"

    name = fields.Char(string="Name")
    from_date = fields.Date(string="From Date")
    course_subject = fields.Char(string="Course Subject")
    to_date = fields.Date(string="To Date")
    status = fields.Selection([('start', 'To Start'),
                               ('running', 'Running'),
                               ('hold', 'Hold'),
                               ('cancel', 'Cancel'),
                               ('Done', 'Done')], default='start',
                              string="Status")
    employee_ids = fields.One2many('employee.training','hr_training_id', string="Employee")
    description = fields.Text(string="Description")
    company_id = fields.Many2one('res.company',
                                 default=lambda self: self.env.user.company_id)



class EmployeeTraining(models.Model):
    _name = "employee.training"
    _description = "Employee Training"

    name = fields.Char(string=" Course Name")
    employee_id = fields.Many2one("hr.employee", string="Employee")
    hr_training_id = fields.Many2one("hr.training", string="Training Program")
    result = fields.Char(string='Result')
    training_cost = fields.Char(string='Training Cost')
    from_date = fields.Date(string="From Date")
    course_subject = fields.Char(string="Course Subject", related='hr_training_id.course_subject')
    to_date = fields.Date(string="To Date")
    status = fields.Selection([('start', 'To Start'),
                               ('running', 'Running'),
                               ('hold', 'Hold'),
                               ('cancel', 'Cancel'),
                               ('Done', 'Done')], default='start',
                              string="Status")
    description = fields.Text(string="Description")
    company_id = fields.Many2one('res.company',
                                 default=lambda self: self.env.user.company_id)
    doc_attachment_id = fields.Many2many('ir.attachment', 'doc_attach_rel', 'doc_id', 'attach_id3', string="Attachment",
                                         help='You can attach the copy of your document', copy=False)

class HREmployee(models.Model):
    _inherit = 'hr.employee'


    punish_ids = fields.One2many("employee.punish", "employee_id", string="العقويات")
    training_ids = fields.One2many("employee.training", "employee_id", string="Training")



class EmployeeTrainingAttachment(models.Model):
    _inherit = 'ir.attachment'

    doc_attach_rel = fields.Many2many('employee.training', 'doc_attachment_id', 'attach_id3', 'doc_id',
                                      string="Attachment", invisible=1)