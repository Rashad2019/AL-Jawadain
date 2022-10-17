
from datetime import datetime, date, timedelta

from odoo import models, fields, api, _


class HrDocumentTemplate(models.Model):
    _name = 'hr.document.template'
    _description = 'HR Documents Templates'

    code = fields.Char(string='Document Code', size=5, required=True,copy=False)
    name = fields.Char(string='Document Name', required=True, copy=False)
    description = fields.Text(string='Description', copy=False)
    document_attachment_id = fields.Many2many('ir.attachment', 'document_attachment_rel', 'doc_id', 'attach_id4', string="Attachment",
                                         help='You can attach the copy of your document', copy=False)

class HrDocumentTemplateAttachment(models.Model):
    _inherit = 'ir.attachment'

    document_attachment_rel = fields.Many2many('hr.document.template', 'document_attachment_id', 'attach_id4', 'doc_id',
                                      string="Attachment", invisible=1)
