
from odoo import models, fields, api
from itertools import chain

concat = chain.from_iterable


class UsersControl(models.Model):
    _inherit = 'res.users'

    def default_is_sales_person_control(self):
        if self.has_group('iq_sales_alanwan_customs.f_salepersonaccess_group_id'):
            return True
        else:
            return False

    def default_have_discount_access_control(self):
        if self.has_group('iq_extend_sales_alanwan_customs.f_salediscaccess_group_id'):
            return True
        else:
            return False

    is_sales_person_control = fields.Boolean(string='Is SalesPerson ?', default=default_is_sales_person_control)
    have_discount_access_control = fields.Boolean(string='Disable Discount Access On Sales ?', default=default_have_discount_access_control)

    def write(self, values):
        res = super(UsersControl, self).write(values)

        if self.env.user.has_group('sales_team.group_sale_manager'):
            for user in self:
                salepersonaccess_group = self.env.ref('iq_sales_alanwan_customs.f_salepersonaccess_group_id')
                if values.get('is_sales_person_control'):
                    super(UsersControl, user).write({'groups_id': [(4,salepersonaccess_group.id)]})
                elif values.get('is_sales_person_control') == False:
                    super(UsersControl,user).write({'groups_id': [(3,salepersonaccess_group.id)]})

                salediscaccess_group = self.env.ref('iq_extend_sales_alanwan_customs.f_salediscaccess_group_id')
                if values.get('have_discount_access_control'):

                    super(UsersControl, user).write({'groups_id': [(4,salediscaccess_group.id)]})
                elif  values.get('have_discount_access_control') == False:
                    super(UsersControl,user).write({'groups_id': [(3,salediscaccess_group.id)]})

                if not 'is_sales_person_control' in values:
                    if user.has_group('iq_sales_alanwan_customs.f_salepersonaccess_group_id'):
                        super(UsersControl, user).write({'is_sales_person_control': True})
                    else:
                        super(UsersControl, user).write({'is_sales_person_control': False})
                if not 'have_discount_access_control' in values:
                    if user.has_group('iq_extend_sales_alanwan_customs.f_salediscaccess_group_id'):
                        super(UsersControl, user).write({'have_discount_access_control': True})
                    else:
                        super(UsersControl, user).write({'have_discount_access_control': False})
        return res

