from odoo.addons.smart_api.tool.help import _get_customers_domain , _getCustomersData

from odoo import api, fields, models


class SmartAPI(models.Model):
    _inherit = "smart_api"


    def fetch_customers(self, **kwargs):
        """
        Extra Parameters: domain, limit, fields, offset, order
        """
        context = dict(self.env.context)
        user_id = context.get('user')
        customers_list = {'customers': []}
        domain = _get_customers_domain()
        kwargs['base_url'] = self._get_base_url()
        kwargs['context'] = context
        salespersons_customers_only = self.env['ir.config_parameter']\
            .sudo().get_param('smart_api.salespersons_customers_only')
        if user_id and salespersons_customers_only:
            domain += [('salesperson_ids','in',user_id.id)]
        result = {'offset': int(kwargs.get('offset', 0))}
        try:
            for key, val in kwargs.items():
                if key.startswith('filter.'):
                    key_name = key.split(".")[1]
                    if val.isnumeric():
                        real_value = int(val)
                    else:
                        real_value = val
                    domain += [(key_name, '=', real_value)]
        except:
            pass

        if 'search' in kwargs:
            s = kwargs['search']
            domain += ['|','|','|',('name', 'ilike', s),('phone', 'ilike', s),('email', 'ilike', s),('mobile', 'ilike', s)]

        PartnerObj = self.env['res.partner'].sudo()
        result['count'] = PartnerObj.search_count(domain)
        partner_data = PartnerObj.with_context().search(domain, limit=int(kwargs.get(
            'limit', 100000)), offset=result["offset"], order=kwargs.get('order', 0))
        customers_list['customers'] = _getCustomersData(partner_data, kwargs)
        result['data'] = customers_list
        return result

