
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def cashvan_presale_post_init(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    cashvan_group_id = env.ref("cashvan_presale.cashvan_group_id")
    if cashvan_group_id:
        user_ids = env['res.users'].search([])
        userlistids = user_ids.mapped('id') or []
        if userlistids:
            env.ref("cashvan_presale.cashvan_group_id").write({'users': [(6, 0 ,userlistids)]})


def uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})

    env.ref("cashvan_presale.cashvan_group_id").write({'users': [(5, False, False)]})
    env.ref("cashvan_presale.presale_group_id").write({'users': [(5, False, False)]})

