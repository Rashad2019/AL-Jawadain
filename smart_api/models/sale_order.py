
import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

from odoo.http import request
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def add_order_line(self, product_id=None, line_id=None, add_qty=0, set_qty=0,uom_id=None,discount_type=False,discount_amount=0, **kwargs):
        self.ensure_one()
        product_context = dict(self.env.context)
        product_context.setdefault('lang', self.sudo().partner_id.lang)
        SaleOrderLineSudo = self.env['sale.order.line'].sudo().with_context(product_context)
        # change lang to get correct name of attributes/values
        product_with_context = self.env['product.product'].with_context(product_context)
        product = product_with_context.browse(int(product_id))
        try:
            if add_qty:
                add_qty = float(add_qty)
        except ValueError:
            add_qty = 1
        try:
            if set_qty:
                set_qty = float(set_qty)
        except ValueError:
            set_qty = 0
        quantity = 0
        order_line = False
        # if self.state != 'draft':
        #     request.session['sale_order_id'] = None
        #     raise UserError(_('It is forbidden to modify a sales order which is not in draft status.'))
        # if line_id is not False:
        #     order_line = self._cart_find_product_line(product_id, line_id, **kwargs)[:1]

        # Create line if no line with product_id can be located
        if not order_line:
            if not product:
                raise UserError(_("The given product does not exist therefore it cannot be added to cart."))

            no_variant_attribute_values = kwargs.get('no_variant_attribute_values') or []
            received_no_variant_values = product.env['product.template.attribute.value'].browse([int(ptav['value']) for ptav in no_variant_attribute_values])
            received_combination = product.product_template_attribute_value_ids | received_no_variant_values
            product_template = product.product_tmpl_id

            # handle all cases where incorrect or incomplete data are received
            combination = product_template._get_closest_possible_combination(received_combination)


            # get or create (if dynamic) the correct variant
            product = product_template._create_product_variant(combination)

            if not product:
                raise UserError(_("The given combination does not exist therefore it cannot be added to order."))

            product_id = product.id

            values = self.product_id_change(self.id, product_id, qty=1, uom_id=uom_id, discount_type=discount_type,discount_amount=discount_amount)

            # add no_variant attributes that were not received
            for ptav in combination.filtered(lambda ptav: ptav.attribute_id.create_variant == 'no_variant' and ptav not in received_no_variant_values):
                no_variant_attribute_values.append({
                    'value': ptav.id,
                })

            # save no_variant attributes values
            if no_variant_attribute_values:
                values['product_no_variant_attribute_value_ids'] = [
                    (6, 0, [int(attribute['value']) for attribute in no_variant_attribute_values])
                ]

            # add is_custom attribute values that were not received
            custom_values = kwargs.get('product_custom_attribute_values') or []
            received_custom_values = product.env['product.template.attribute.value'].browse([int(ptav['custom_product_template_attribute_value_id']) for ptav in custom_values])

            for ptav in combination.filtered(lambda ptav: ptav.is_custom and ptav not in received_custom_values):
                custom_values.append({
                    'custom_product_template_attribute_value_id': ptav.id,
                    'custom_value': '',
                })
            # save is_custom attributes values
            if custom_values:
                values['product_custom_attribute_value_ids'] = [(0, 0, {
                    'custom_product_template_attribute_value_id': custom_value['custom_product_template_attribute_value_id'],
                    'custom_value': custom_value['custom_value']
                }) for custom_value in custom_values]

            # create the line
            order_line = SaleOrderLineSudo.create(values)
            try:
                order_line._compute_tax_id()
            except ValidationError as e:
                # The validation may occur in backend (eg: taxcloud) but should fail silently in frontend
                _logger.debug("ValidationError occurs during tax compute. %s" % (e))
            if add_qty:
                add_qty -= 1

        # compute new quantity
        if set_qty:
            quantity = set_qty
        elif add_qty is not None:
            quantity = order_line.product_uom_qty + (add_qty or 0)

        # Remove zero of negative lines
        if quantity <= 0:
            order_line.unlink()
        else:
            # update line
            no_variant_attributes_price_extra = [ptav.price_extra for ptav in order_line.product_no_variant_attribute_value_ids]
            values = self.with_context(no_variant_attributes_price_extra=tuple(no_variant_attributes_price_extra)).product_id_change(self.id, product_id, qty=quantity, uom_id=uom_id, discount_type=discount_type,discount_amount=discount_amount)
            if self.pricelist_id.discount_policy == 'with_discount' and not self.env.context.get('fixed_price'):
                order = self.sudo().browse(self.id)
                product_context.update({
                    'partner': order.partner_id,
                    'quantity': quantity,
                    'date': order.date_order,
                    'uom': uom_id,
                    'pricelist': order.pricelist_id.id
                })
                product_with_context = self.env['product.product'].with_company(order.company_id).with_context(product_context)
                product = product_with_context.browse(product_id)
                values['price_unit'] = self.env['account.tax']._fix_tax_included_price_company(
                    order_line._get_display_price(product),
                    order_line.product_id.taxes_id,
                    order_line.tax_id,
                    self.company_id
                )
            order_line.write(values)

            order_line.name = order_line.get_sale_order_line_multiline_description_sale(product)

        option_lines = self.order_line.filtered(lambda l: l.id == order_line.id)

        return {'line_id': order_line.id, 'quantity': quantity, 'option_ids': list(set(option_lines.ids))}

    def product_id_change(self, order_id, product_id, qty=0,uom_id=None,discount_type=False,discount_amount=0):
        order = self.sudo().browse(order_id)
        product_context = dict(self.env.context)
        product_context.setdefault('lang', order.partner_id.lang)

        product_context.update({
            'partner': order.partner_id,
            'quantity': qty,
            'uom': uom_id,
            'date': order.date_order,
            'pricelist': order.pricelist_id.id,
        })

        product = self.env['product.product'].with_context(product_context).with_company(order.company_id.id).browse(product_id)
        discount = 0

        if order.pricelist_id.discount_policy == 'without_discount':
            # This part is pretty much a copy-paste of the method '_onchange_discount' of
            # 'sale.order.line'.
            price, rule_id = order.pricelist_id.with_context(product_context).get_product_price_rule(product, qty or 1.0, order.partner_id)
            pu, currency = request.env['sale.order.line'].with_context(product_context)._get_real_price_currency(product, rule_id, qty, product.uom_id, order.pricelist_id.id)
            if pu != 0:
                if order.pricelist_id.currency_id != currency:
                    # we need new_list_price in the same currency as price, which is in the SO's pricelist's currency
                    date = order.date_order or fields.Date.today()
                    pu = currency._convert(pu, order.pricelist_id.currency_id, order.company_id, date)
                discount = (pu - price) / pu * 100
                if discount < 0:
                    # In case the discount is negative, we don't want to show it to the customer,
                    # but we still want to use the price defined on the pricelist
                    discount = 0
                    pu = price
        else:
            pu = product.price
            if order.pricelist_id and order.partner_id:
                order_line = self.env['sale.order.line'].sudo().search([('order_id', '=', order.id), ('product_id', '=', product_id)])
                if order_line:
                    pu = self.env['account.tax']._fix_tax_included_price_company(pu, product.taxes_id, order_line[0].tax_id, self.company_id)

        return {
            'product_id': product_id,
            'product_uom_qty': qty,
            'order_id': order_id,
            'product_uom': uom_id or product.uom_id.id,
            'price_unit': pu,
            'discount': discount,
            'iq_disc': discount_amount or 0,
            'iq_discount_type': discount_type or '',
        }

    def compute_disc(self, vals):
        discount = 0
        if 'iq_disc' in vals and vals['iq_disc'] != 0:
            if 'iq_discount_type' in vals and vals['iq_discount_type'] == 'percent':
                if 'price_unit' in vals and vals['price_unit'] != 0:
                    disc = (vals['iq_disc'] / vals['price_unit']) * 100
                    discount = disc

            else:
                discount = vals['iq_disc']
        return discount

    def compute_disc_order(self):
        if self.iq_discount_amount != 0:
            iq_count = 0
            line_disc = 0
            disc = 0
            for x in self.order_line:
                iq_count = iq_count + 1
            if self.iq_discount_type == 'percent':
                line_disc = self.iq_discount_amount
            else:
                line_disc = self.iq_discount_amount / iq_count

            for x in self.order_line:
                x.write({
                    'iq_disc': line_disc,
                    'iq_discount_type': self.iq_discount_type,
                })

    @api.onchange('user_id')
    def onchange_user_id(self):
        super().onchange_user_id()
        if not self.env.user and self.env.uid:
            self.env.user = self.env['res.users'].sudo().search([('id', '=', self.env.uid)])
        if self.env.user.assigned_warehouse_id:
            self.warehouse_id = self.env.user.assigned_warehouse_id
        else:
            self.warehouse_id = self.user_id.with_company(self.company_id.id)._get_default_warehouse_id().id