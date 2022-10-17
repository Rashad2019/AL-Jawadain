from odoo import api, fields, models, _
from odoo.exceptions import UserError



class FStockScrapConfirm(models.Model):
    _inherit = 'stock.scrap'
    
    
    iq_note = fields.Char('Reason')
    iq_user = fields.Char('Scrap User')
    
    def action_validate(self):
        if self.user_has_groups('iq_alanwan_customs.f_scrapadminprodqty_group_id'):
            return super(FStockScrapConfirm, self).action_validate()
        else:
            raise UserError(_('Only Users Have Access "Scrap/Admin" can validate !!'))
        