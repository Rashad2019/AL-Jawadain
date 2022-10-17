import random
import string
import re
from odoo import fields , _

from datetime import datetime
import logging
from odoo.addons.smart_api.tool.service import WebServices

_logger = logging.getLogger(__name__)


def _changePricelist(pricelist_id):
    return {
        'currencySymbol': pricelist_id.currency_id.symbol or "",
        'currencyPosition': pricelist_id.currency_id.position or "",
    }


def _displayWithCurrency(lang_obj,amount,symbol,position):
    fmt = "%.{0}f".format(2)  # currency.decimal_places
    formatted_amount = lang_obj.format(
        fmt,amount,grouping=True,monetary=True)  # currency.round(amount)
    return "%s%s" % (symbol,formatted_amount) if position == "before" else "%s%s" % (formatted_amount,symbol)


def _lang_get(cls):
    return cls.env['res.lang'].get_installed()


def _default_unique_key(size,chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))

def _get_image_url(base_url,model_name,record_id,field_name,write_date=0,width=0,height=0):
    """ Returns a local url that points to the image field of a given browse record. """
    if base_url and not base_url.endswith("/"):
        base_url = base_url + "/"
    if width or height:
        return '%sweb/image/%s/%s/%s/%sx%s?unique=%s' % (
            base_url,model_name,record_id,field_name,width,height,
            re.sub('[^\d]','',fields.Datetime.to_string(write_date)))
    else:
        return '%sweb/image/%s/%s/%s?unique=%s' % (
            base_url,model_name,record_id,field_name,re.sub('[^\d]','',fields.Datetime.to_string(write_date)))


def _getCustomersData(p_data,context={}):
    result = []

    if 'context' in context:
        context_default = context.get('context')
    else:
        context_default = context
    base_url = context_default.get('base_url')
    lang_obj = context_default.get('lang_obj')
    currency_symbol = context_default.get('currencySymbol')
    currency_position = context_default.get('currencyPosition')
    for partner in p_data:
        total_due = ""
        credit = partner.credit
        if partner.credit < 0:
            credit = 0
        if partner.total_due > 0:
            total_due = _displayWithCurrency(lang_obj,abs(partner.total_due) or 0,currency_symbol,currency_position)
        result.append({
            'customer_id': partner.id or '',
            'name': partner.name or '',
            'phone': partner.phone or '',
            'mobile': partner.mobile or '',
            'email': partner.email or '',
            'lang': partner.lang or '',
            'image': _get_image_url(base_url,'res.partner',partner.id, 'image_1920', partner.write_date),
            'latitude': str(partner.partner_latitude) or '',
            'longitude': str(partner.partner_longitude) or '',
            'total_due': total_due,
            'credit': credit,
            'debit': partner.debit,
            'addresses': _getCustomerAddresses(partner)
        })
    return result


def _getCustomerAddresses(Partner):
    result = {}
    domain = [
        ('id','child_of',Partner.commercial_partner_id.ids),
        ('id','not in',[Partner.id]),
    ]
    addresses = Partner.search(domain,limit=5,offset=0,order="id desc")
    result['addresses'] = [
        {
            'name': Partner.name or '',
            'addressId': Partner.id,
        }
    ]
    if _checkFullAddress(Partner):
        result['addresses'][0]['display_name'] = app_display_address(
            Partner._display_address(),Partner.name)
    else:
        result['addresses'][0]['display_name'] = EMPTY_ADDRESS
    for address in addresses:
        temp = {
            'name': address.name or '',
            'display_name': address._display_address() != EMPTY_ADDRESS and app_display_address(
                address._display_address(),address.name) or address._display_address(),
            'addressId': address.id,
        }
        result['addresses'].append(temp)
    return result['addresses']


def _getProductData(self , p_data, context={}):
    context_default = context.get('context')
    base_url = context_default.get("base_url")
    currency_symbol = context_default.get("currencySymbol")
    currency_position = context_default.get("currencyPosition")
    lang_obj = context_default.get("lang_obj",)
    pricelist = context_default.get("pricelist",False)
    result = []
    for prod in p_data:
        attributes = []
        variants = []

        units = []
        sub_units = self.env["uom.uom"].sudo().search([("id","!=",prod.uom_id.id),("active","=",True),("category_id","=", prod.uom_id.category_id.id)])
        for sub_unit in sub_units:

            units.append({
                "name": sub_unit.name,
                "uom_id": sub_unit.id,
                "default": False,
                "rate": sub_unit.factor_inv,
            })
        units.append({
            "name": prod.uom_id.name,
            "uom_id": prod.uom_id.id,
            "default": True,
            "rate": prod.uom_id.factor_inv,
        })
        for ali in prod.attribute_line_ids:
            temp = {
                "name": ali.attribute_id.name or "",
                "attribute_id": ali.attribute_id.id,
                "type": ali.attribute_id.display_type,
                "newVariant": ali.attribute_id.create_variant,
                "values": [],
            }
            for v in ali.value_ids:
                temp["values"].append({
                        "name": v.name or "",
                        "value_id": v.id,
                        "htmlCode": v.html_color or "",
                        "newVariant": ali.attribute_id.create_variant
                })
            attributes.append(temp)
        if prod.product_variant_count > 1:
            for var in prod.product_variant_ids:
                comb_info = prod.with_context(**context)._get_combination_info(combination=False,product_id=var.id,add_qty=1,
                                                                               pricelist=pricelist,parent_combination=False,
                                                                               only_template=False)
                temp = {
                    'product_id': var.id,
                    'name': var.name or '',
                    'barcode': var.barcode or '',
                    'price_with_discount': comb_info['price'] or 0,
                    'price_unit': comb_info['has_discounted_price'] and comb_info['list_price'] or comb_info['price'] or 0,
                    'price_with_discount_with_currency': comb_info['has_discounted_price'] and _displayWithCurrency(lang_obj,comb_info[
                        'price'] or 0,currency_symbol,currency_position) or "",
                    'price_unit_with_currency': _displayWithCurrency(lang_obj,
                                                       comb_info['has_discounted_price'] and comb_info['list_price'] or
                                                       comb_info['price'] or 0,currency_symbol,currency_position),
                    'image': _get_image_url(base_url,'product.product',var.id,'image_1920',prod.write_date),
                    'available_qty': int(var.qty_available) or 0,
                    'combinations': [],
                }
                for ptavi in var.product_template_attribute_value_ids:
                    temp["combinations"].append({
                        "value_id": ptavi.product_attribute_value_id and ptavi.product_attribute_value_id.id,
                        "attribute_id": ptavi.attribute_id and ptavi.attribute_id.id,
                    })
                variants.append(temp)

        comb_info = prod.with_context(**context)._get_combination_info(combination=False,product_id=False,add_qty=1,
                                                                       pricelist=pricelist,parent_combination=False,
                                                                       only_template=False)
        result.append({
            'product_id': prod.id or '',
            'name': prod.name or '',
            'barcode': prod.barcode or '',
            'price_unit': comb_info['has_discounted_price'] and comb_info['list_price'] or comb_info['price'] or 0,
            'price_with_discount': comb_info['has_discounted_price'] and comb_info['price'] or 0,

            'price_unit_with_currency': _displayWithCurrency(lang_obj,comb_info['has_discounted_price'] and comb_info['list_price'] or
                                               comb_info['price'] or 0,currency_symbol,currency_position),
            'price_with_discount_with_currency': comb_info['has_discounted_price'] and _displayWithCurrency(lang_obj,
                                                                                              comb_info['price'] or 0,
                                                                                              currency_symbol,
                                                                                              currency_position) or "",
            'description': prod.description_sale or '',
            'available_qty': int(prod.qty_available) or 0,
            'image': _get_image_url(base_url,'product.template',prod.id,'image_1920',prod.write_date),
            'product_uom': units or [],
            'attributes' : attributes or [],
            'variants': variants or []
        })

    return result

def _get_journaldata(data,context={}):
    context_default = context.get('context')
    reconciled_vals = []
    partner = {}
    if data.partner_id:
        partner = _getCustomersData(data.partner_id,context_default)
    currency = {'currency_id': data.currency_id.id,'currency_symbol': data.currency_id.symbol}
    move_type_value = dict(data.fields_get(["move_type"],['selection'])['move_type']["selection"])

    lines = []
    for line in data.line_ids:
        account = {'account_id': line.account_id.id,'account_name': line.account_id.name}

        lines.append({
            'label': line.name,
            'account': account,
            'debit': line.debit,
            'credit': line.credit,
        })

    reconciled_vals.append({
        'name': data.name,
        'move_id': data.id,
        'ref': data.ref or '',
        'move_type': move_type_value[data.move_type],
        'customer': partner,
        'amount': data.amount_total,
        'currency': currency,
        'lines': lines or [],
        'date': fields.Datetime.to_string(data.date) or "",
        })
    return reconciled_vals

def _prepare_default_reversal(move, reason=''):
    reverse_date = datetime.today()
    return {
        'ref': _('Reversal of: %(move_name)s, %(reason)s', move_name=move.name, reason=reason)
               if reason
               else _('Reversal of: %s', move.name),
        'date': reverse_date,
        # 'reason': reason,
        # 'refund_method': 'modify',
        'invoice_date': move.is_invoice(include_receipts=True) and (reverse_date or move.date)  or False,
        'journal_id': move.journal_id.id,
        'invoice_payment_term_id': None,
        'invoice_user_id': move.invoice_user_id.id,
        'auto_post': False,
    }


def _get_product_fields():
    return ['name','product_variant_id','product_variant_count','price','description_sale','lst_price','write_date']


def _get_product_domain():
    return [("sale_ok","=",True)]


def _get_customers_domain():
    return [("active","=",True),('customer_rank','>',0),('state','=','approved')]


def app_display_address(address,name=""):
    return (name or "") + (name and "\n" or "") + address


def _checkFullAddress(Partner):
    # mandatory_fields = ["street","city","zip","country_id"]
    mandatory_fields = ["street","city","state_id","zip","country_id"]

    val = mandatory_fields
    # val = [True if mf == "state_id" and not Partner.country_id.state_ids else getattr(
    #     Partner,mf) for mf in mandatory_fields]
    return all(val)

def convert_to_float(time_att):
    h_m_s = time_att.split(":")
    hours = int(h_m_s[0])
    minutes_1 = float(h_m_s[1]) / 60.0
    minutes = ("%.2f" % minutes_1)
    return hours + float(minutes)


def _easy_date(time=False):
    now = datetime.now()
    if type(time) is str:
        time = fields.Datetime.from_string(time)
    if type(time) is int:
        diff = now - datetime.fromtimestamp(time)
    elif isinstance(time,datetime):
        diff = now - time
    elif not time:
        diff = now - now
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(second_diff) + " seconds ago"
        if second_diff < 120:
            return "a minute ago"
        if second_diff < 3600:
            return str(int(second_diff / 60)) + " minutes ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str(int(second_diff / 3600)) + " hours ago"
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(day_diff) + " days ago"
    if day_diff < 31:
        return str(int(day_diff / 7)) + " weeks ago"
    if day_diff < 365:
        return str(int(day_diff / 30)) + " months ago"
    return str(int(day_diff / 365)) + " years ago"


TAG_RE = re.compile(r'<[^>]+>')


def remove_htmltags(text):
    return TAG_RE.sub('',text)


EMPTY_ADDRESS = "\n\n  \n"
