
# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError


class iq_AccountMovepaymenregistertInherit(models.TransientModel):
    _inherit = 'account.payment.register'
    
    
    def action_create_payments(self):
        if self._context.get('active_model') == 'account.move':
                move_id = self.env['account.move'].browse(self._context.get('active_ids', []))
                if move_id.move_type == 'in_invoice':
                    attachment_data = self.env['ir.attachment'].read_group([('res_model', '=', 'account.move'), ('res_id', '=', move_id.id)], ['res_id'], ['res_id'])
                    print("attachment_data",len(attachment_data))
                    attachment = dict((data['res_id'], data['res_id_count']) for data in attachment_data)
                    print("attachment",attachment)
                    attach_no = attachment.get(self.id, 0)
                    print("diffff",self.payment_difference,"attach_no",attach_no)
                    if self.payment_difference == 0 :
                        if len(attachment_data) > 0 :
                            print("passsss")
                            return super(iq_AccountMovepaymenregistertInherit, self).action_create_payments()
                        else:
                            print("ERRORORORORO")
                            raise UserError(_('Please Load Attachment before Fully Paid !!'))
                    else:
                        return super(iq_AccountMovepaymenregistertInherit, self).action_create_payments()
            
                else:
                    return super(iq_AccountMovepaymenregistertInherit, self).action_create_payments()
        else:
                    return super(iq_AccountMovepaymenregistertInherit, self).action_create_payments() 
