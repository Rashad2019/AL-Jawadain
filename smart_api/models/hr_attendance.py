from odoo import api,fields,models,_
import logging

_logger = logging.getLogger(__name__)


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    current_state = fields.Integer('current_state',default=1)
    time_out = fields.Float('Time Out',default=0.0)

    @api.depends('time_out')
    def _compute_time_out(self):
        for atten in self:
            atten.time_out_string ='{0:02.0f}:{1:02.0f}'.format(*divmod(float(atten.time_out) * 60,60))

    time_out_string = fields.Char('Time Out',default='00:00',compute=_compute_time_out)


