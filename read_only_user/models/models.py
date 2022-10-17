from odoo import api, models, _
from odoo.exceptions import AccessError


class BaseModelExtend(models.AbstractModel):
    _inherit = 'base'

    @api.model_create_multi
    @api.returns('self', lambda value: value.id)
    def create(self, vals_list):
        if self.env.user.read_only_user:
            model = self._name
            mode = 'create'
            self._cr.execute("""SELECT MAX(CASE WHEN perm_{mode} THEN 1 ELSE 0 END)
                                      FROM ir_model_access a
                                      JOIN ir_model m ON (m.id = a.model_id)
                                     WHERE a.group_id IS NULL
                                       AND m.model = %s
                                       AND a.active IS TRUE""".format(mode=mode),
                             (model,))
            public_rule = self._cr.fetchone()[0]
            if not public_rule and model not in ['mail.message', 'mail.channel.partner', 'mail.channel', 'resource.resource', 'mail.alias', 'res.users.log', 'ir.attachment', 'bus.bus', 'bus.presence']:
                # print(self._name)
                # print('Access Denied Contact your administrator to allows this operation')
                raise AccessError(_('Access Denied Contact your administrator to allows this operation'))

        return super(BaseModelExtend, self).create(vals_list)

    @api.model
    def _create(self, data_list):
        if self.env.user.read_only_user:
            model = self._name
            mode = 'create'
            self._cr.execute("""SELECT MAX(CASE WHEN perm_{mode} THEN 1 ELSE 0 END)
                                      FROM ir_model_access a
                                      JOIN ir_model m ON (m.id = a.model_id)
                                     WHERE a.group_id IS NULL
                                       AND m.model = %s
                                       AND a.active IS TRUE""".format(mode=mode),
                             (model,))
            public_rule = self._cr.fetchone()[0]
            if not public_rule and model not in ['mail.message', 'mail.channel.partner', 'mail.channel', 'resource.resource', 'mail.alias', 'res.users.log', 'ir.attachment', 'bus.bus', 'bus.presence']:
                # print(self._name)
                # print('Access Denied Contact your administrator to allows this operation')
                raise AccessError(_('Access Denied Contact your administrator to allows this operation'))

        return super(BaseModelExtend, self)._create(data_list)

    def _write(self, vals):
        if self.env.user.read_only_user:

            model = self._name
            mode = 'write'
            self._cr.execute("""SELECT MAX(CASE WHEN perm_{mode} THEN 1 ELSE 0 END)
                                      FROM ir_model_access a
                                      JOIN ir_model m ON (m.id = a.model_id)
                                     WHERE a.group_id IS NULL
                                       AND m.model = %s
                                       AND a.active IS TRUE""".format(mode=mode),
                             (model,))
            public_rule = self._cr.fetchone()[0]
            if not public_rule and model not in ['mail.message', 'mail.channel.partner', 'mail.channel', 'resource.resource', 'mail.alias', 'res.users.log', 'ir.attachment', 'bus.bus', 'bus.presence']:
                # print(self._name)
                # print('Access Denied Contact your administrator to allows this operation')
                raise AccessError(_('Access Denied Contact your administrator to allows this operation'))

        return super(BaseModelExtend, self)._write(vals)

    def write(self, vals):
        if self.env.user.read_only_user:
            model = self._name
            mode = 'write'
            self._cr.execute("""SELECT MAX(CASE WHEN perm_{mode} THEN 1 ELSE 0 END)
                                      FROM ir_model_access a
                                      JOIN ir_model m ON (m.id = a.model_id)
                                     WHERE a.group_id IS NULL
                                       AND m.model = %s
                                       AND a.active IS TRUE""".format(mode=mode),
                             (model,))
            public_rule = self._cr.fetchone()[0]
            if not public_rule and model not in ['mail.message', 'mail.channel.partner', 'mail.channel', 'resource.resource', 'mail.alias', 'res.users.log', 'ir.attachment', 'bus.bus', 'bus.presence']:
                # print(self._name)
                # print('Access Denied Contact your administrator to allows this operation')
                raise AccessError(_('Access Denied Contact your administrator to allows this operation'))

        return super(BaseModelExtend, self).write(vals)

    def unlink(self):
        if self.env.user.read_only_user:
            model = self._name
            mode = 'unlink'
            self._cr.execute("""SELECT MAX(CASE WHEN perm_{mode} THEN 1 ELSE 0 END)
                                      FROM ir_model_access a
                                      JOIN ir_model m ON (m.id = a.model_id)
                                     WHERE a.group_id IS NULL
                                       AND m.model = %s
                                       AND a.active IS TRUE""".format(mode=mode),
                             (model,))
            public_rule = self._cr.fetchone()[0]
            if not public_rule and model not in ['mail.message', 'mail.channel.partner', 'mail.channel', 'resource.resource', 'mail.alias', 'res.users.log', 'ir.attachment', 'bus.bus', 'bus.presence']:
                # print(self._name)
                # print('Access Denied Contact your administrator to allows this operation')
                raise AccessError(_('Access Denied Contact your administrator to allows this operation'))

        return super(BaseModelExtend, self).unlink()
