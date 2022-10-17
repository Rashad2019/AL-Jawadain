import base64
import os
from odoo import models, fields,tools, api
from odoo.modules.module import get_module_resource


class ResCompany(models.Model):
    _inherit = 'res.company'

    def _get_bg_image(self):
        image_path = get_module_resource('bg_image_custom', 'static/src/img/', 'home-menu-bg-overlay.svg')
        return base64.b64encode(open(image_path, 'rb') .read())

    bg_image = fields.Binary('Background Image', attachment=True, default=_get_bg_image)

    def write(self, vals):

        if 'bg_image' in vals:
            if vals['bg_image'] == False:
                vals['bg_image'] = self._get_bg_image()
        return super(ResCompany, self).write(vals)
