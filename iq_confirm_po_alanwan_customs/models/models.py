from odoo import api, fields, models, _
from odoo.exceptions import UserError



class FconfirmPurchaseOrderConfirm(models.Model):
    _inherit = 'purchase.order'
    
    
    
    def button_confirm(self):
        attachment_data = self.env['ir.attachment'].read_group([('res_model', '=', 'purchase.order'), ('res_id', 'in', self.ids)], ['res_id'], ['res_id'])
        attachment = dict((data['res_id'], data['res_id_count']) for data in attachment_data)
      
        attach_no = attachment.get(self.id, 0)
        if self.user_has_groups('purchase.group_purchase_manager'):
            return super(FconfirmPurchaseOrderConfirm, self).button_confirm()
        else:
            raise UserError(_('Only Purchase/Admin Can Confirm  !!'))
            
#         if self.user_has_groups('purchase.group_purchase_manager'):
#             if self.partner_id :
#                     if attach_no > 0  :
#                         return super(FPurchaseOrderConfirm, self).button_confirm()
#                     else:
#                         raise UserError(_('Please Load Attachment before Confirm Purchase Order !!'))
#             else:
#                     return super(FPurchaseOrderConfirm, self).button_confirm()
#         else:
#             raise UserError(_('Only Purchase/Admin Can Confirm  !!'))
            