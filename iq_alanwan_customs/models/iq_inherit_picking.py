from odoo import api, fields, models, _
from odoo.exceptions import UserError



class FPuickingConfirm(models.Model):
    _inherit = 'stock.picking'
    

    def button_validate(self):
        if self.picking_type_id.code == 'incoming':
            attachment_data = self.env['ir.attachment'].read_group([('res_model', '=', 'stock.picking'), ('res_id', 'in', self.ids)], ['res_id'], ['res_id'])
            attachment = dict((data['res_id'], data['res_id_count']) for data in attachment_data)

            attach_no = attachment.get(self.id, 0)

            if self.partner_id :
                    if attach_no > 0  :
                        return super(FPuickingConfirm, self).button_validate()
                    else:
                        if not self.env.context.get('skip_attachment'):
                            raise UserError(_('Please Load Attachment before Confirm Purchase Order !!'))
                        else:
                            return super(FPuickingConfirm,self).button_validate()
            else:
                    return super(FPuickingConfirm, self).button_validate()
        else:
            return super(FPuickingConfirm, self).button_validate()