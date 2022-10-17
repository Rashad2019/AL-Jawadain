
from odoo.addons.smart_api.tool.help import app_display_address , _displayWithCurrency, _lang_get, _default_unique_key, _get_image_url, _get_customers_domain, _getCustomersData , _getProductData, _get_product_domain,_get_journaldata,_prepare_default_reversal,convert_to_float, _get_product_fields, _easy_date
from odoo import api, fields, models, _
from odoo.fields import Datetime, Date
from odoo.tests import Form
from odoo.exceptions import UserError
import random
import json
import re
from .fcmAPI import FCMAPI
from odoo.addons.base.models.ir_mail_server import MailDeliveryException
import logging
import datetime

_logger = logging.getLogger(__name__)


class SmartAPI(models.Model):
    _name = "smart_api"
    _description = "Smart API Model"

    @api.model
    def _validate(self, api_key, context=None):
        context = context or {}
        response = {'success': False, 'responseCode': 0, 'message': _('Unknown Error !!!')}
        if not api_key:
            response['message'] = _('Invalid/Missing Api Key !!!')
            return response
        try:
            smart_api = context.get("smart_api_obj") or self.env['smart_api'].sudo().search([], limit=1)
            if not smart_api:
                response['responseCode'] = 1
                response['message'] = _("SmartAPI Configuration not found !!!")
            elif smart_api.api_key != api_key:
                response['responseCode'] = 1
                response['message'] = _("API Key is invalid !!!")
            else:
                app_lang = context.get(
                    'lang') or smart_api.default_lang and smart_api.default_lang.code or "en_US"
                pricelist_id = context.get('pricelist', False) or smart_api.pricelist_id.id
                app_pricelist = self.env['product.pricelist'].sudo().browse(int(pricelist_id))
                # response["itemsPerPage"] = smart_api.product_limit
                response['success'] = True
                response['responseCode'] = 2
                response['message'] = _('Login successfully.')
                response["context"] = {
                    "pricelist": app_pricelist,
                    "currency_id": app_pricelist.currency_id.id,
                    'currencySymbol': app_pricelist.currency_id.symbol or "",
                    'currencyPosition': app_pricelist.currency_id.position or "",
                    'allowed_company_ids': [smart_api.company_id.id],
                    'tz': 'ASIA/Baghdad',
                    'bin_size': False,
                    'edit_translations': False,
                    'uid': self.env.ref('base.public_user', False) and self.env.ref('base.public_user').id,
                    "user": self.env.ref('base.public_user', False),
                    'lang': app_lang,
                    'lang_obj' :self.env['res.lang']._lang_get(app_lang),
                    "base_url": self._get_base_url() or context.get("host_url")
                }
                response['context']["smart_api_obj"] = smart_api.with_context(response['context'])
        except Exception as e:
            response['responseCode'] = 3
            response['message'] = _("Login Failed:")+"%r" % e
        return response

    @api.model
    def _get_image_url(self, model_name, record_id, field_name, write_date=0, width=0, height=0, context=None):
        """ Returns a local url that points to the image field of a given browse record. """
        context = context.get('context') or {}
        if context.get('base_url', "") and not context['base_url'].endswith("/"):
            context['base_url'] = context['base_url'] + "/"
        if not 'base_url' in context:
            context['base_url'] = self._get_base_url()
        if width or height:
            return '%sweb/image/%s/%s/%s/%sx%s?unique=%s' % (context.get('base_url'), model_name, record_id, field_name, width, height, re.sub('[^\d]', '', fields.Datetime.to_string(write_date)))
        else:
            return '%sweb/image/%s/%s/%s?unique=%s' % (context.get('base_url'), model_name, record_id, field_name, re.sub('[^\d]', '', fields.Datetime.to_string(write_date)))

    @api.model
    def _get_cat_info(self, categ_obj, context=None):
        context = context or {}
        cat_data = {
            "category_id": categ_obj.id,
            "name": categ_obj.name or "",
            "image": self._get_image_url('product.category',categ_obj.id,'image',categ_obj.write_date,context=context),
            "children": [],
        }
        return cat_data

    @api.model
    def _recursive_cats(self, categ_obj, context=None):
        context = context or {}
        data = self._get_cat_info(categ_obj, context)
        if categ_obj.child_id:
            for cat_child in categ_obj.child_id:
                data['children'].append(self._recursive_cats(cat_child, context))
        return data

    @api.model
    def fetch_categories(self, **kwargs):
        context = kwargs or {}
        domain = []
        all_cats = []
        result = {}
        categories_list = {'categories': []}
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
            domain += [('name', 'ilike', kwargs['search'])]

        # if not domain:
        #     domain = [('parent_id','=',False)]
        cat_obj = self.env['product.category'].sudo()
        result['count'] = cat_obj.search_count(domain)
        top_cats = cat_obj.search(domain)
        # for top_cat in top_cats:
        #     all_cats.append(self._recursive_cats(top_cat, context))

        for top_cat in top_cats:
            all_cats.append(self._get_cat_info(top_cat, context))
        categories_list['categories'] = all_cats
        result['data'] = categories_list
        return result

    @api.model
    def fetch_user_info(self, user_obj, context=None):
        context = context or {}
        discount_access = True
        lang_obj = context.get('lang_obj')
        saleperson_type = 'cashvan'
        default_currency = {'currency_id': user_obj.company_id.currency_id.id,
                            'currency_name' :user_obj.company_id.currency_id.name,
                            'currency_symbol': user_obj.company_id.currency_id.symbol}
        default_pricelist = {
            'name': context.get('pricelist') and context.get('pricelist').name or '',
            'pricelist_id': context.get('pricelist') and context.get('pricelist').id or 0 ,
        }
        company ={
            'company_id': user_obj.company_id.id,
            'name':  user_obj.company_id.name or '',
            'logo': self._get_image_url('res.partner',user_obj.company_id.partner_id.id,'image_1920',user_obj.company_id.partner_id.write_date,context=context),
            'address': app_display_address(user_obj.company_id.partner_id._display_address(), user_obj.company_id.name),
            'phone': user_obj.company_id.phone or '',
            'email':user_obj.company_id.email or '',
            'website':user_obj.company_id.website or '',
            'default_currency': default_currency,
            'default_pricelist': default_pricelist,
        }
        collections = self.env['account.payment'].sudo()
        invoices = self.env['account.move'].sudo()
        customers = self.env['res.partner'].sudo()

        domain_collections = [('partner_type','=','customer'),('user_id','=',user_obj.id),('state','=','posted'),('payment_type','=','inbound')]
        domain_invoices = [('invoice_user_id','=',user_obj.id),('state','=','posted'),('move_type','in',('out_invoice','out_refund'))]
        domain_customers = _get_customers_domain()

        thismonth = fields.Date.today()
        start_date = datetime.datetime(thismonth.year,thismonth.month,1)
        this_day = fields.Date.today()

        domain_collections += [('date','>=',start_date),('date','<=',this_day)]
        domain_invoices += [('invoice_date','>=',start_date),('invoice_date','<=',this_day)]
        salespersons_customers_only = self.env['ir.config_parameter']\
            .sudo().get_param('smart_api.salespersons_customers_only')
        if salespersons_customers_only and 'salesperson_ids' in customers._fields:
            domain_customers += [('salesperson_ids','in',user_obj.id)]
        elif salespersons_customers_only:
            domain_customers += [('user_id','=',user_obj.id)]

        done_payments = collections.search(domain_collections)
        done_invoices = invoices.search(domain_invoices)
        total_customers = customers.search_count(domain_customers)

        payment_month_total = sum(done_payments.mapped('amount')) or 0
        payment_month_total_st =_displayWithCurrency(lang_obj,payment_month_total,user_obj.company_id.currency_id.symbol,user_obj.company_id.currency_id.position)

        invoice_month_total = sum(done_invoices.mapped('amount_total')) or 0
        invoice_month_total_st =_displayWithCurrency(lang_obj,invoice_month_total,user_obj.company_id.currency_id.symbol,user_obj.company_id.currency_id.position)

        if user_obj.has_group('iq_extend_sales_alanwan_customs.f_salediscaccess_group_id'):
            discount_access = False
        if user_obj.has_group('cashvan_presale.presale_group_id'):
            saleperson_type = 'presale'
        temp_i = {
            'userId': user_obj.id,
            'userName': user_obj.name or "",
            'userEmail': user_obj.login or "",
            'userPhone': user_obj.phone or "",
            # 'userLang': user_obj.lang.split('_')[0],
            'userLang': user_obj.lang,
            'company': company,
            'discount_access': discount_access,
            'saleperson_type': saleperson_type,
            'max_discount': int(user_obj.max_discount) or 0,
            'userProfileImage': self._get_image_url('res.user', user_obj.id, 'image_1920', user_obj.write_date, context=context),
            'themeCode': '?',
            'total_collect_this_month': payment_month_total_st or '',
            'total_customers': total_customers or 0,
            'total_commission_this_month': '',
            'total_invoiced_this_month': invoice_month_total_st or '',

        }
        return temp_i

    @api.model
    def authenticate(self, credentials, detailed=False, isSocialLogin=False, context=None):
        context = context or {}
        response = {'success': False, 'responseCode': 0, 'message': _('Unknown Error !!!')}
        user = False
        if not isinstance(credentials, dict):
            response['message'] = _('Data is not in Dictionary format !!!')
            return response

        if isSocialLogin:
            if not all(k in credentials for k in ('authProvider', 'authUserId')):
                response['message'] = _('Insufficient data to authenticate !!!')
                return response
            provider = self._getAuthProvider(credentials['authProvider'])
            try:
                user = self.env['res.users'].sudo().search(
                    [('oauth_uid', '=', credentials['authUserId']), ('oauth_provider_id', '=', provider)])
                if not user:
                    response['responseCode'] = 1
                    response['message'] = _("Social-Login: No such record found.")
            except Exception as e:
                response['responseCode'] = 3
                response['message'] = _("Social-Login Failed.")
                response['details'] = "%r" % e
        else:
            if not all(k in credentials for k in ('email', 'password')):
                response['message'] = _('Insufficient data to authenticate !!!')
                return response
            try:
                user = self.env['res.users'].sudo().search([('login', '=', credentials['email'])])
                if user:
                    user.with_user(user)._check_credentials(credentials['password'],{'interactive':True})
                else:
                    response['responseCode'] = 1
                    response['message'] = _("Invalid email address.")
                    response['accessDenied'] = True
            except Exception as e:
                user = False
                response['responseCode'] = 3
                response['message'] = _("Login Failed.")
                response['details'] = "%r" % e
                response['accessDenied'] = True
        if user:
            try:

                response['success'] = True
                response['responseCode'] = 2
                # response['userId'] = user.id
                response['message'] = _('Login successfully.')
                context.update({"uid": user.id,"user": user, 'tz': user.tz,"warehouse": user.assigned_warehouse_id.id})
                response["context"] = context
                # response["uid"] = user.id
                if detailed:
                    response["data"] = self.fetch_user_info(user, context=context)
                    # response.update(self.fetch_user_info(user, context=context))
                # Update request context
                from odoo.http import request
                self.env = context.get('user')

                request.context = dict(context)

            except Exception as e:
                response['responseCode'] = 3
                response['message'] = _("Login Failed.")
                response['details'] = "%r" % e
        return response

    @api.model
    def resetPassword(self, login):
        response = {'success': False}
        try:
            if login:
                self.env['res.users'].sudo().reset_password(login)
                response['success'] = True
                response['message'] = _(
                    "An email has been sent with credentials to reset your password")
            else:
                response['message'] = _("No login provided.")
        except MailDeliveryException as me:
            response['message'] = _("Exception : %r" % me)
        except Exception as e:
            response['message'] = _("Invalid Username/Email.")
        return response

    def attendance(self,context, user_id, **kwargs):
        result = {"success": True}
        user = self.env.context.get('user')
        company_id = user.company_id
        context = dict(self.env.context)
        try:
            kwargs['user_id'] = user_id
            domain = [('id','=',user_id)]
            UserObj = self.env['res.users'].sudo().search(domain,limit=1)
            if UserObj:
                current_state = 3
                employee = UserObj.employee_id
                if employee:
                    kwargs['base_url'] = self._get_base_url()
                    kwargs['context'] = context
                    action_date = fields.Datetime.now()
                    action_date_only = fields.date.today()
                    employee_attendance = self.env['hr.attendance'].sudo().search_count([('employee_id','=',employee.id)])


                    last_attendance_before_check_in = self.env['hr.attendance'].sudo().search([
                        ('employee_id','=',employee.id),
                    ],order='check_in desc',limit=1)
                    last_attendance_before_check_out = self.env['hr.attendance'].sudo().search([
                        ('employee_id','=',employee.id),
                        ('check_in','<=',action_date_only.strftime('%Y-%m-%d 23:59:59')),
                    ],order='check_in desc',limit=1)
                    if 'type' in kwargs:
                        latitude = 0
                        longitude = 0
                        if 'latitude' in kwargs:
                            latitude = kwargs['latitude']
                        if 'latitude' in kwargs:
                            longitude = kwargs['longitude']
                        if kwargs['type'] == 'check_in':
                            att_data = {
                                "check_in_latitude": latitude or 0,
                                "check_in_longitude": longitude or 0,
                                "employee_id": employee.id,
                                "check_in": action_date,
                                "current_state": 0,

                            }

                            if employee_attendance == 0:
                                self.env['hr.attendance'].sudo().with_user(user).create(att_data)
                                message = _('Attendance Created Successfully.')
                                result = {'success': True,'data': {},'message': message}
                                return result

                            if last_attendance_before_check_in.check_in.strftime(
                                '%Y-%m-%d') == action_date_only.strftime(
                                '%Y-%m-%d') and last_attendance_before_check_in.check_out.strftime(
                                '%Y-%m-%d') == action_date_only.strftime('%Y-%m-%d') and last_attendance_before_check_in.current_state == 1:
                                time_out =  abs(convert_to_float(str(action_date.time()))) - abs(convert_to_float(str(last_attendance_before_check_in.check_out.time())))
                                att_data_update = {
                                    "current_state": 0,
                                    "time_out": time_out + last_attendance_before_check_in.time_out
                                }

                                last_attendance_before_check_in.sudo().with_user(user).write(att_data_update)
                                # print('{0:02.0f}:{1:02.0f}'.format(*divmod(float(last_attendance_before_check_in.time_out) * 60,60)))

                                message = _('Attendance Created Successfully.')
                                result = {'success': True,'data': {},'message': message}
                                return result


                            if (last_attendance_before_check_in and last_attendance_before_check_in.check_out and last_attendance_before_check_in.check_out.strftime('%Y-%m-%d') != action_date_only.strftime('%Y-%m-%d')) or (employee_attendance == 0):
                                self.env['hr.attendance'].sudo().with_user(user).create(att_data)
                                message = _('Attendance Created Successfully.')
                                result = {'success': True,'data': {},'message': message}
                                return result
                            else:
                                message = _('Attendance Created Successfully.')
                                result = {'success': True,'data': {},'message': message}
                        else:
                            att_data_update = {
                                "check_out_latitude": latitude or 0,
                                "check_out_longitude": longitude or 0,
                                "check_out": action_date,
                                "current_state":1,
                            }

                            attendance = int(last_attendance_before_check_in.current_state)

                            if last_attendance_before_check_out.check_in.strftime('%Y-%m-%d') == action_date_only.strftime('%Y-%m-%d'):
                                last_attendance_before_check_out.sudo().with_user(user).write(att_data_update)
                                message = _('Attendance Created Successfully.')
                                result = {'success': True,'data': {},'message': message}
                                return result

                        message = _('Attendance Created Successfully.')
                        result = {'success': True,'data':{},'message': message}
                    else:
                        message = _('Error On Post Data!!')
                        result = {'success': False,'message': message}
                else:
                    message = _('Error Employee Not Found!!')
                    result = {'success': False,'message': message}
            else:
                message = "Error Employee Not Found!!"
                result = {'success': False,'message': message}
        except Exception as e:
            print(e)
            message = _(("Error On Create Attendance  %s !!"),str(e))
            result = {'success': False,'message': message}

        return result

    def createvisit(self,context,customer_id, **kwargs):
        result = {"success": True}
        user = context.get('user').id
        context = dict(self.env.context)
        try:
            kwargs['customer_id'] = customer_id
            domain = [('id','=', customer_id)]
            customerObj = self.env['res.partner'].sudo().search(domain,limit=1)
            visit_options = self.get_visitPurposes()
            visit_type = "5"
            if visit_options.get('data'):
                if 'options' in visit_options.get('data'):
                    options_list = visit_options.get('data')['options']
                    if 'reason_visit' in kwargs:
                        for d in options_list:
                            if d['name'] == kwargs['reason_visit']:
                                visit_type = d['id']
            if customerObj:
                kwargs['base_url'] = self._get_base_url()
                kwargs['context'] = context
                visit_date = fields.Date.today()
                next_visit_date = False
                have_next_visit = False
                if kwargs['next_visit_date']:
                    next_visit_date =datetime.datetime.strptime(kwargs['next_visit_date'],'%Y-%m-%d').date()
                    have_next_visit = True
                att_data = {
                    # "visit_ids": customerObj.id,
                    "user_id": user or False,
                    "assigned_by": user or False,
                    "meeting_person_name": kwargs['person_name'] or '',
                    "meeting_person_phone": kwargs['person_phone'] or '',
                    "reason_visit": kwargs['reason_visit'] or '',
                    "result_visit": kwargs['result_visit'] or '',
                    "visit_date": visit_date,
                    "show_date": visit_date,
                    "next_visit": next_visit_date,
                    "latitude": kwargs['lat'] or 0,
                    "longitude": kwargs['lng'] or 0,
                    "street": kwargs['street'] or '',
                    "visit_type": visit_type or '1',
                    "state": 'done',
                    "is_assigned_next_visit": have_next_visit,

                }
                visit_ids = self.env['customer.visit'].with_user(user).create(att_data)
                customerObj.with_user(user).write({'visits_ids': [(4, visit_ids.id)]})
                if visit_ids :
                    res_data = {
                        "visit_id": visit_ids.id,
                        "customer_id": customerObj.id,
                        "person_name": kwargs['person_name'] or '',
                        "person_phone": kwargs['person_phone'] or '',
                        "street": kwargs['street'] or '',
                        "reason_visit": kwargs['reason_visit'] or '',
                        "result_visit": kwargs['result_visit'] or '',
                        "visit_date": Date.to_string(visit_date) or "",
                        "next_visit_date": Date.to_string(next_visit_date) or '',
                        "have_next_visit": have_next_visit,
                        "state": 'done',
                    }
                    message = _('Visit Created Successfully.')
                    result = {'success': True,'data': res_data,'message': message}
                else:
                    message = "Error On Create New Visit !!"
                    result = {'success': False,'message': message}

            else:
                message = "Error Customer Not Found!!"
                result = {'success': False,'message': message}
        except Exception as e:
            print(e)
            message = _(("Error On Create Visit  %s !!"),str(e))
            result = {'success': False,'message': message}

        return result

    def fetch_customer_visit(self,context,**kwargs):
        result = {"success": True}
        user = context.get('user').id
        context = dict(self.env.context)
        limit =int(kwargs.get('limit',1))
        customer_id = 0
        visits = []
        try:
            if 'customer_id' in kwargs:
                customer_id = int(kwargs['customer_id'])
            else:
                result = {'success': False,'message': _('Parameter customer_id  must be send !!!')}
                return result
            domain = [('id','=', customer_id)]
            customerObj = self.env['res.partner'].sudo().search(domain,limit=1)
            if customerObj:
                domainvisit = [('visit_ids','=',customer_id),('user_id','=',user),('assigned_by','=',user)]

                visit_ids = self.env['customer.visit'].sudo().search(domainvisit,order='id desc',limit=limit)
                visit_type_value = dict(
                    self.env['customer.visit'].sudo().fields_get(["visit_type"],['selection'])['visit_type'][
                        "selection"])

                if visit_ids :
                    for visit_id in visit_ids:
                        res_data = {
                            "visit_id": visit_id.id,
                            "customer_id": customerObj.id,
                            "person_name": visit_id.meeting_person_name or '',
                            "person_phone": visit_id.meeting_person_phone or '',
                            "street": visit_id.street or '',
                            "visit_type" : visit_type_value[visit_id.visit_type] or '',
                            "reason_visit": visit_id.reason_visit or '',
                            "result_visit": visit_id.result_visit or '',
                            "visit_date": Date.to_string(visit_id.visit_date) or "",
                            "next_visit_date": Date.to_string(visit_id.next_visit) or '',
                            "have_next_visit": visit_id.is_assigned_next_visit or False,
                            "state": 'done',
                        }
                        visits.append(res_data)
                    message = _('Visits Fetched Successfully')
                    result = {'success': True,'message': message}
                    result['data'] = {'visits': visits}
                else:
                    message = _("Success but Nothing to Show !!")
                    result = {'success': True,'data': {},'message': message}

            else:
                message = "Error Customer Not Found!!"
                result = {'success': False,'message': message}
        except Exception as e:
            message = _(("Error On Fetch Visits  %s !!"),str(e))
            result = {'success': False,'message': message}

        return result

    def updatevisit(self,context,visit_id, **kwargs):
        result = {"success": True}
        user = context.get('user').id
        context = dict(self.env.context)
        try:
            domain = [('id','=', visit_id),('user_id','=',user),('state','not in',['draft','done'])]
            visit_obj = self.env['customer.visit'].sudo().search(domain,limit=1)
            if visit_obj:
                kwargs['base_url'] = self._get_base_url()
                kwargs['context'] = context
                visit_date = fields.Date.today()
                next_visit_date = False
                have_next_visit = False
                if kwargs['next_visit_date']:
                    next_visit_date =datetime.datetime.strptime(kwargs['next_visit_date'],'%Y-%m-%d').date()
                    have_next_visit = True
                att_data = {
                    "meeting_person_name": kwargs['person_name'] or '',
                    "meeting_person_phone": kwargs['person_phone'] or '',
                    "result_visit": kwargs['result_visit'] or '',
                    "next_visit": next_visit_date,
                    "state": kwargs['state'] or 'done',
                    "is_assigned_next_visit": have_next_visit,

                }
                visit_obj.with_user(user).write(att_data)
                if visit_obj:
                    res_data = {
                        "visit_id": visit_obj.id,
                        "customer": _getCustomersData(visit_obj.visit_ids,context)[0],
                        "person_name": visit_obj.meeting_person_name or '',
                        "person_phone": visit_obj.meeting_person_phone or '',
                        "street": visit_obj.street or '',
                        "reason_visit": int(visit_obj.visit_type) or 1,
                        "result_visit": visit_obj.result_visit or '',
                        "visit_date": Date.to_string(visit_obj.visit_date) or "",
                        "next_visit_date": Date.to_string(visit_obj.next_visit) or "",
                        "lat": visit_obj.latitude or visit_obj.visit_ids.partner_latitude or 0,
                        "lng": visit_obj.longitude or visit_obj.visit_ids.partner_longitude or 0,
                        "have_next_visit": True if visit_obj.is_assigned_next_visit else False,
                        "assigned_by": visit_obj.assigned_by.name if visit_obj.assigned_by else ''
                    }
                    message = _('Visit Update Successfully.')
                    result = {'success': True,'data': res_data,'message': message}
                else:
                    message = "Error On Update Visit !!"
                    result = {'success': False,'message': message}
            else:
                message = "Error Visit Not Found!!"
                result = {'success': False,'message': message}
        except Exception as e:
            print(e)
            message = _(("Error On Update Visit  %s !!"),str(e))
            result = {'success': False,'message': message}

        return result

    def setvisitpurpose(self,context,visit_id, **kwargs):
        result = {"success": True}
        user = context.get('user').id
        context = dict(self.env.context)
        try:
            domain = [('id','=', visit_id),('user_id','=',user),('state','not in',['draft','done'])]
            visit_obj = self.env['customer.visit'].sudo().search(domain,limit=1)
            if visit_obj:
                kwargs['base_url'] = self._get_base_url()
                kwargs['context'] = context

                if kwargs['next_visit_date']:
                    next_visit_date =datetime.datetime.strptime(kwargs['next_visit_date'],'%Y-%m-%d').date()
                    have_next_visit = True
                att_data = {
                    "meeting_person_name": kwargs['person_name'] or '',
                    "meeting_person_phone": kwargs['person_phone'] or '',
                    "result_visit": kwargs['result_visit'] or '',
                    "next_visit": next_visit_date,
                    "state": kwargs['state'] or 'done',
                    "is_assigned_next_visit": have_next_visit,

                }
                visit_obj.with_user(user).write(att_data)
                if visit_obj:
                    res_data = {
                        "visit_id": visit_obj.id,
                        "customer": _getCustomersData(visit_obj.visit_ids,context)[0],
                        "person_name": visit_obj.meeting_person_name or '',
                        "person_phone": visit_obj.meeting_person_phone or '',
                        "street": visit_obj.street or '',
                        "reason_visit": int(visit_obj.visit_type) or 1,
                        "result_visit": visit_obj.result_visit or '',
                        "visit_date": Date.to_string(visit_obj.visit_date) or "",
                        "next_visit_date": Date.to_string(visit_obj.next_visit) or "",
                        "lat": visit_obj.latitude or visit_obj.visit_ids.partner_latitude or 0,
                        "lng": visit_obj.longitude or visit_obj.visit_ids.partner_longitude or 0,
                        "have_next_visit": True if visit_obj.is_assigned_next_visit else False,
                        "assigned_by": visit_obj.assigned_by.name if visit_obj.assigned_by else ''
                    }
                    message = _('Visit Update Successfully.')
                    result = {'success': True,'data': res_data,'message': message}
                else:
                    message = "Error On Update Visit !!"
                    result = {'success': False,'message': message}
            else:
                message = "Error Visit Not Found!!"
                result = {'success': False,'message': message}
        except Exception as e:
            print(e)
            message = _(("Error On Update Visit  %s !!"),str(e))
            result = {'success': False,'message': message}

        return result

    def donevisit(self,context,visit_id, **kwargs):
        result = {"success": True}
        user = context.get('user').id
        context = dict(self.env.context)
        try:
            domain = [('id','=', visit_id),('user_id','=',user),('state','not in',['draft','done'])]
            visit_obj = self.env['customer.visit'].sudo().search(domain,limit=1)
            visit_type_value = dict(self.env['customer.visit'].sudo().fields_get(["visit_type"],['selection'])['visit_type']["selection"])

            if visit_obj:
                kwargs['base_url'] = self._get_base_url()
                kwargs['context'] = context
                visit_type = "5"
                visit_type_name = ""
                if 'visit_type' in kwargs:
                    if visit_type_value[str(kwargs['visit_type'])]:
                        visit_type = str(kwargs['visit_type'])
                        visit_type_name = visit_type_value[str(kwargs['visit_type'])]
                att_data = {
                    "state": 'done',
                    "visit_type": visit_type,
                }
                visit_obj.with_user(user).write(att_data)
                if visit_obj:
                    res_data = {
                        "visit_id": visit_obj.id,
                        "customer": _getCustomersData(visit_obj.visit_ids,context)[0],
                        "person_name": visit_obj.meeting_person_name or '',
                        "person_phone": visit_obj.meeting_person_phone or '',
                        "street": visit_obj.street or '',
                        "visit_type": visit_type_name or '',
                        "reason_visit": int(visit_obj.visit_type) or 1,
                        "result_visit": visit_obj.result_visit or '',
                        "visit_date": Date.to_string(visit_obj.visit_date) or "",
                        "next_visit_date": Date.to_string(visit_obj.next_visit) or "",
                        "lat": visit_obj.latitude or visit_obj.visit_ids.partner_latitude or 0,
                        "lng": visit_obj.longitude or visit_obj.visit_ids.partner_longitude or 0,
                        "have_next_visit": True if visit_obj.is_assigned_next_visit else False,
                        "assigned_by": visit_obj.assigned_by.name if visit_obj.assigned_by else ''
                    }
                    message = _('Visit Finished Successfully.')
                    result = {'success': True,'data': res_data,'message': message}
                else:
                    message = "Error On Finish Visit !!"
                    result = {'success': False,'message': message}

            else:
                message = "Error Visit Not Found!!"
                result = {'success': False,'message': message}
        except Exception as e:
            print(e)
            message = _(("Error On Finish Visit  %s !!"),str(e))
            result = {'success': False,'message': message}

        return result

    def fetch_visits(self, context, **kwargs):
        result = {"success": True}
        user = context.get('user').id
        context = dict(self.env.context)
        visits =[]
        visits_list = {'visits': []}
        domain = [('user_id', '=',user),('assigned_by', '!=',user),('state', '=','assigned')]
        # domain += [('visit_date', '=', datetime.datetime.today() + datetime.timedelta(days=1))]
        domain += [('show_date', '<=', fields.date.today())]
        visit_type_value = dict(
            self.env['customer.visit'].sudo().fields_get(["visit_type"],['selection'])['visit_type'][
                "selection"])
        try:
            for key, val in kwargs.items():
                if key.startswith('filter.'):
                    key_name = key.split(".")[1]
                    if key_name == 'visit_date':
                        real_value = datetime.datetime.strptime(val,'%Y-%m-%d').date()
                        domain += [('visit_date', '=', real_value)]
                        pass
                    # elif key_name == 'to_date':
                    #     real_value = datetime.datetime.strptime(val,'%Y-%m-%d').date()
                    #     domain += [('show_date', '<=', real_value)]
                    #     pass
                    elif key_name == 'partner_id':
                        domain += [('visit_ids', '=', int(val))]
                        pass
                    elif val.isnumeric():
                        real_value = int(val)
                        domain += [(key_name,'=',real_value)]
                    else:
                        real_value = val
                        domain += [(key_name,'=',real_value)]
        except:
            pass

        try:
            visitsObj = self.env['customer.visit'].sudo().search(domain)
            if visitsObj:
                for visit in visitsObj:
                    res_data = {
                        "visit_id": visit.id,
                        "customer": _getCustomersData(visit.visit_ids,context)[0],
                        "person_name": visit.meeting_person_name or '',
                        "person_phone": visit.meeting_person_phone or '',
                        "street": visit.street or '',
                        "visit_type": visit_type_value[visit.visit_type] or '',
                        "reason_visit": int(visit.visit_type) or 1,
                        "result_visit": visit.result_visit or '',
                        "visit_date": Date.to_string(visit.visit_date) or "",
                        "show_date": Date.to_string(visit.show_date) or "",
                        "next_visit_date": Date.to_string(visit.next_visit) or "",
                        "lat": visit.latitude or visit.visit_ids.partner_latitude or 0,
                        "lng": visit.longitude or visit.visit_ids.partner_longitude or 0,
                        "have_next_visit": True if visit.is_assigned_next_visit else False,
                        "assigned_by": visit.assigned_by.name if visit.assigned_by else ''
                    }
                    visits.append(res_data)


                if visits:
                    visits_list['visits'] = visits
                    message = _('Visits Fetched Successfully.')
                    result = {'success': True,'data': visits_list,'message': message}
                else:
                    message = _("Success but Nothing to Show !!")
                    result = {'success': True,'data': {},'message': message}

            else:
                message = _("Success but Nothing to Show !!")
                result = {'success': True,'data': {},'message': message}
        except Exception as e:
            print(e)
            message = _(("Error On Fetch Visits  %s !!"),str(e))
            result = {'success': False,'message': message}

        return result

    def fetch_orders(self, context, **kwargs):
        """
        Extra Parameters: domain, limit, fields, offset, order

        """
        orders =[]
        orders_list = {'orders': []}
        domain = []
        domain = [('user_id', '=', context.get('user').id)]

        result = {'offset': int(kwargs.get('offset', 0))}
        try:
            for key, val in kwargs.items():
                if key.startswith('filter.'):
                    key_name = key.split(".")[1]
                    if key_name == 'from_date':
                        real_value = datetime.datetime.strptime(val,'%Y-%m-%d').date()
                        domain += [('date_order', '>=', real_value)]
                        pass
                    elif key_name == 'to_date':
                        real_value = datetime.datetime.strptime(val,'%Y-%m-%d').date()
                        domain += [('date_order', '<=', real_value)]
                        pass
                    elif val.isnumeric():
                        real_value = int(val)
                        domain += [(key_name,'=',real_value)]
                    else:
                        real_value = val
                        domain += [(key_name,'=',real_value)]
        except:
            pass
        if 'search' in kwargs:
            domain += ['|',('name', 'ilike', kwargs['search']),('id', 'like', kwargs['search'])]

        OrdersObj = self.env['sale.order'].sudo()
        result['count'] = OrdersObj.search_count(domain)
        orders_date = OrdersObj.search(domain, limit=int(kwargs.get(
            'limit', 1000)), offset=result["offset"], order=kwargs.get('order', 0))
        for order_data in orders_date:

            orders.append(self.get_order(order_data.id))
        orders_list['orders'] = orders
        result['data'] = orders_list
        return result

    def fetch_journalentries(self, **kwargs):
        """
        Extra Parameters: domain, limit, fields, offset, order

        """
        context = dict(self.env.context)
        lang_obj = context.get('lang_obj')
        currency_symbol = context.get('currencySymbol')
        currency_position = context.get('currencyPosition')
        invoices =[]
        domain = []
        result = {}
        invoices_list = {'journalentries': [],'total_unreconciled': '0','total_reconciled': '0'}
        assigned_journal_id = self.env.context.get('user').assigned_journal_id or self._get_default_journal_id()
        if assigned_journal_id:
            domain += [('journal_id', '=', assigned_journal_id.id)]
        else:
            message = _("Please Specify Journal to user!!")
            result = {'success': False,'message': message}
            return result

        domain +=[('state', '=', 'posted')]
        rows_unreconciled = self.env['account.move.line'].sudo().search([('account_id', '=', assigned_journal_id.payment_debit_account_id.id)])
        total_unreconciled = 0
        for row_unreconciled in rows_unreconciled:
            total_unreconciled += row_unreconciled.debit - row_unreconciled.credit
        # total_reconciled = self.env.context.get('user').assigned_journal_id.payment_debit_account_id.balance or 0
        invoices_list['total_unreconciled'] =_displayWithCurrency(lang_obj,total_unreconciled,currency_symbol,currency_position)
        invoices_list['total_reconciled'] =_displayWithCurrency(lang_obj,total_unreconciled,currency_symbol,currency_position)

        result = {'offset': int(kwargs.get('offset', 0))}
        try:
            for key, val in kwargs.items():
                if key.startswith('filter.'):
                    key_name = key.split(".")[1]
                    if key_name not in ['from_date','to_date']:
                        domain += [('date','<=',datetime.datetime.today())]

                    if key_name == 'from_date':
                        real_value = datetime.datetime.strptime(val,'%Y-%m-%d').date()
                        domain += [('date', '>=', real_value)]
                        pass
                    elif key_name == 'to_date':
                        real_value = datetime.datetime.strptime(val,'%Y-%m-%d').date()
                        domain += [('date', '<=', real_value)]
                        pass
                    elif val.isnumeric():
                        real_value = int(val)
                        domain += [(key_name,'=',real_value)]
                    else:
                        real_value = val
                        domain += [(key_name,'=',real_value)]
        except:
            pass
        if 'search' in kwargs:
            domain += ['|',('name', 'ilike', kwargs['search']),('id', 'like', kwargs['search'])]
        kwargs['base_url'] = self._get_base_url()
        invoicesObj = self.env['account.move'].sudo()
        result['count'] = invoicesObj.search_count(domain)
        invoices_date = invoicesObj.with_context().search(domain, limit=int(kwargs.get(
            'limit', 1000)), offset=result["offset"], order=kwargs.get('order', 0))
        for invoice_date in invoices_date:
            invoices.append(_get_journaldata(invoice_date,kwargs)[0])
        invoices_list['journalentries'] = invoices
        result['data'] = invoices_list
        return result


    def fetch_dueinvoices(self, context, **kwargs):
        """
        Extra Parameters: domain, limit, fields, offset, order

        """
        invoices =[]
        invoices_list = {'dueinvoices': []}
        domain = [('user_id', '=', context.get('user').id)]
        domain += [('payment_state','in',['partial', 'not_paid']),('amount_residual','>',0),('move_type','=','out_invoice'),('state','=','posted')]

        result = {'offset': int(kwargs.get('offset', 0))}
        try:
            for key, val in kwargs.items():
                if key.startswith('filter.'):
                    key_name = key.split(".")[1]
                    if key_name not in ['from_date','to_date']:
                        domain += [('invoice_date_due','<=',datetime.datetime.today())]

                    if key_name == 'from_date':
                        real_value = datetime.datetime.strptime(val,'%Y-%m-%d').date()
                        domain += [('invoice_date_due', '>=', real_value)]
                        pass
                    elif key_name == 'to_date':
                        real_value = datetime.datetime.strptime(val,'%Y-%m-%d').date()
                        domain += [('invoice_date_due', '<=', real_value)]
                        pass
                    elif val.isnumeric():
                        real_value = int(val)
                        domain += [(key_name,'=',real_value)]
                    else:
                        real_value = val
                        domain += [(key_name,'=',real_value)]
        except:
            pass
        if 'search' in kwargs:
            domain += ['|',('name', 'ilike', kwargs['search']),('id', 'like', kwargs['search'])]

        invoicesObj = self.env['account.move'].sudo()
        result['count'] = invoicesObj.search_count(domain)
        invoices_date = invoicesObj.search(domain, limit=int(kwargs.get(
            'limit', 1000)), offset=result["offset"], order=kwargs.get('order', 0))
        for invoice_date in invoices_date:
            Orderdomain = [('user_id', '=', context.get('user').id),('invoice_ids', 'in', [invoice_date.id])]
            OrderObj = self.env['sale.order'].sudo().search(Orderdomain, limit=1)
            if OrderObj:
                invoices.append(self.get_invoice(invoice_date.id))
        invoices_list['dueinvoices'] = invoices
        result['data'] = invoices_list
        return result

    def fetch_products(self, **kwargs):
        """
        Extra Parameters: domain, limit, fields, offset, order

        """
        domain = _get_product_domain()
        product_list = {'products': []}
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
            domain += ['|',('name', 'ilike', kwargs['search']),('barcode', 'ilike', kwargs['search'])]

        ProductObj = self.env['product.template'].sudo()
        result['count'] = ProductObj.search_count(domain)
        product_data = ProductObj.with_context().search(domain, limit=int(kwargs.get(
            'limit', 1000)), offset=result["offset"], order=kwargs.get('order', 0))
        product_list['products'] = _getProductData(self,product_data,kwargs)
        result['data'] = product_list
        return result

    def create_customer(self, context, **kwargs):
        result = {"success": True}
        user = self.env.context.get('user')
        company_id = user.company_id
        context = dict(self.env.context)

        try:
            kwargs['customer_rank'] = 1
            kwargs['user_id'] = user.id
            kwargs['company_id'] = company_id.id
            customer = self.env['res.partner'].with_user(user).create(kwargs)

            kwargs['base_url'] = self._get_base_url()
            kwargs['context'] = context
            result['data'] = _getCustomersData(customer,kwargs)[0]
            result['message'] = _('Customer Created.')
        except Exception as e:
            message = "Error On Create Customer !!"
            result = {'success': False,'message': e}

        return result

    def update_customer(self, context,customer_id, **kwargs):
        result = {"success": True}
        user = self.env.context.get('user')
        company_id = user.company_id
        context = dict(self.env.context)
        try:
            kwargs['user_id'] = user.id
            domain = [('id','=',customer_id)]
            PartnerObj = self.env['res.partner'].sudo().search(domain,limit=1)
            if PartnerObj:
                customer = PartnerObj.with_user(user).write(kwargs)
                if customer:
                    kwargs['base_url'] = self._get_base_url()
                    kwargs['context'] = context
                    customerObj = self.env['res.partner'].sudo().search(domain,limit=1)
                    result['data'] = _getCustomersData(customerObj,kwargs)[0]
                    result['message'] = _('Customer Updated Successfully.')
                else:
                    message = "Error On Post Data!!"
                    result = {'success': False,'message': message}
            else:
                message = "Error Customer Not Found!!"
                result = {'success': False,'message': message}
        except Exception as e:
            message = "Error On Update Customer !!"
            result = {'success': False,'message': e}

        return result

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
        result = {'offset': int(kwargs.get('offset', 0))}
        salespersons_customers_only = self.env['ir.config_parameter']\
            .sudo().get_param('smart_api.salespersons_customers_only')
        if user_id and salespersons_customers_only:
            domain += [('user_id', '=', user_id.id)]
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
        if 'risk_exception' in PartnerObj._fields:
            domain += [('risk_exception','=',False)]
        result['count'] = PartnerObj.search_count(domain)
        partner_data = PartnerObj.with_context().search(domain, limit=int(kwargs.get(
            'limit', 1000)), offset=result["offset"], order=kwargs.get('order', 0))
        customers_list['customers'] = _getCustomersData(partner_data, kwargs)
        result['data'] = customers_list
        return result

    def create_so(self,context, **kwargs):
        result = {"success": True}
        user = context.get('user')
        payment_method_id = 0
        payment_term_id = 0
        amount_paid = 0
        note = 0
        warehouse_id = context.get('user').assigned_warehouse_id.id or self._get_default_warehouse_id().id
        pricelist_id = context.get('pricelist').id
        order_discount_rate = 0
        order_discount_type = ''
        discount_access = True

        if user.has_group('iq_extend_sales_alanwan_customs.f_salediscaccess_group_id'):
            discount_access = False
        if 'discount_rate' in kwargs and discount_access:
            if user.max_discount >= float(kwargs['discount_rate']):
                order_discount_rate = float(kwargs['discount_rate'])
            elif float(kwargs['discount_rate']) > user.max_discount:
                result = {'success': False,'message': _('Error Max discount rate you can use is %s !!!',str(user.max_discount))}
                return result
            else:
                order_discount_rate = 0
            order_discount_type = 'percent'

        if 'payment_method_id' in kwargs:
            payment_method_id = int(kwargs['payment_method_id'])
        if 'amount_paid' in kwargs:
            amount_paid = float(kwargs['amount_paid'])

        if 'currency_id' in kwargs:
            currency_id = int(kwargs['currency_id'])

        else:
            currency_id = context.get('currency_id')

        if 'pricelist_id' in kwargs:
            pricelist_id = int(kwargs['pricelist_id'])

        if 'customer_id' in kwargs:
            partner = self.env['res.partner'].sudo().search([('id', '=',int(kwargs['customer_id']))])
            if not partner:
                result = {'success': False,'message': _('Customer 2 not found !!!')}
                return result
        else:
            result = {'success': False,'message': _('Customer 1 not found !!!')}
            return result
        if 'payment_term_id' in kwargs:
            payment_term_id = int(kwargs['payment_term_id'])
        if 'note' in kwargs:
            note = kwargs['note']
        else:
            payment_term_id = partner.property_payment_term_id.id


        addr = partner.address_get(['delivery'])
        so_data = {
            "partner_id": partner.id,
            "pricelist_id": pricelist_id,
            "payment_term_id":  payment_term_id,
            "team_id": user.sale_team_id.id,
            "partner_invoice_id": partner.id,
            "partner_shipping_id": addr['delivery'],
            "user_id": user.id,
            "currency_id":currency_id,
            "warehouse_id":warehouse_id,
        }
        company = context.get("pricelist").company_id
        if company:
            so_data['company_id'] = company.id
        try:
            order = self.env['sale.order'].with_user(user).create(so_data)
            order.write({'user_id':user.id, 'create_uid': user.id})
            order.write({'team_id': user.sale_team_id.id})
            if (('visit_id' not in kwargs or ('visit_id' in kwargs and kwargs['visit_id'] == None)) and 'sale_method' in order._fields):
                order.write({'sale_method': 'by_phone'})
            if 'visit_id' in kwargs and (kwargs['visit_id'] != "" and kwargs['visit_id'] != None) and 'sale_method' in order._fields:
                order.write({'sale_method': 'by_route'})
                print(kwargs['visit_id'])
            result['data'] = order.id
            if 'order_lines' in kwargs:
                discount_type = False
                discount_amount = 0
                uom_id = None

                for order_line in kwargs['order_lines']:
                    if 'product_id' in order_line:
                        product = self.env['product.product'].sudo().search([('product_tmpl_id', '=', int(order_line['product_id']))], limit=1)
                        if not product:
                            result = {'success': False,'message': _('Product not found !!!')}
                            return result
                        else:
                            order_line['product_id'] = product.id
                    else:
                        result = {'success': False,'message': _('Product not found !!!')}
                        return result
                    if 'unit_id' in order_line:
                        uom_id = order_line['unit_id']

                    if 'discount_amount' in order_line and 'discount_type' in order_line and discount_access:
                        if order_line['discount_type'] in ['amount','percent']:
                            discount_type = order_line['discount_type']
                            if order_line['discount_amount'] > 0:
                                discount_amount = order_line['discount_amount']
                    order.add_order_line(order_line['product_id'], None, None ,order_line['qty'],uom_id,discount_type,discount_amount)

            if discount_access:
                order.write({"iq_discount_type": order_discount_type,"iq_discount_amount": order_discount_rate,})
                order.compute_disc_order()
            self.env.user = context.get('user')
            if not user.has_group('cashvan_presale.presale_group_id'):
                order.with_user(user).action_confirm()
                if order.invoice_ids and note:
                    order.invoice_ids.write({'narration': note})

                if order.invoice_ids and amount_paid > 0:
                    payment_obj = self._create_payment_vals(order, context.get('user'), amount_paid)
                    if payment_obj:
                        credit_aml = payment_obj.line_ids.filtered('credit')
                        order.invoice_ids.js_assign_outstanding_line(credit_aml.id)


            result['message'] = _('Order Created.')
        except Exception as e:
            print(e)
            result = {'success': False,'message': _('Error On Create Order (%s) !!!',str(e))}

        return result

    def create_reverse(self, context, invoice_id, **kwargs):
        result = {"success": True}
        user = context.get('user')
        reason = ''
        warehouse_id = context.get('user').assigned_warehouse_id.id or self._get_default_warehouse_id().id
        is_return_stock = False
        is_cancel_needed = False
        new_moves = False
        invoice = 0
        default_values_list = []
        move_line_ids = []
        if 'is_return_stock' in kwargs:
            if kwargs['is_return_stock'] == 1:
                is_return_stock = True
        if 'reason' in kwargs:
            reason = kwargs['reason']

        try:
            if invoice_id:
                invoice = self.env['account.move'].sudo().browse(int(invoice_id))
                Order = self.env['sale.order'].sudo().search([("invoice_ids","in",[invoice.id])],limit=1)

                if invoice and invoice.state not in ('draft','cancel'):
                    default_values_list = _prepare_default_reversal(invoice, reason)
                    new_moves = invoice.with_user(user).with_context(check_move_validity=False)._reverse_moves([default_values_list],cancel=is_cancel_needed)

                    result['data'] = new_moves.id
                    if 'lines' in kwargs:
                        if is_return_stock:
                            if Order and Order.picking_ids:
                                for pick in Order.picking_ids:
                                    if pick.state == 'done' and pick.picking_type_code == 'outgoing':
                                        self.with_user(user)._create_reverse_transfer(pick, kwargs['lines'])

                        for order_line in kwargs['lines']:

                            if 'product_id' in order_line:

                                Order_line = self.env['sale.order.line'].sudo().search(
                                    [("product_id","=",int(order_line['product_id'])),('order_id','=',Order.id)],
                                    limit=1)
                                old_move_line = self.env['account.move.line'].sudo().search([('product_id', '=', int(order_line['product_id'])),('move_id','=',invoice.id)], limit=1)
                                move_line = self.env['account.move.line'].sudo().search([('product_id', '=', int(order_line['product_id'])),('move_id','=',new_moves.id)], limit=1)
                                if not move_line or not Order_line:
                                    result = {'success': False,'message': _('Product not found !!!')}
                                    return result
                                else:
                                    if 'unit_id' in order_line:
                                        uom_id = order_line['unit_id']
                                    else:
                                        uom_id = old_move_line.product_uom_id.id

                                    if 'return_qty' in order_line:
                                        return_qty = order_line['return_qty']
                                    else:
                                        return_qty = 0
                                    if Order_line.qty_invoiced < 0 and (abs(Order_line.qty_invoiced) - move_line.quantity > return_qty):
                                        result = {'success': False,'message': _('Error Returned QTY more than QTY in invoice !!!')}
                                        new_moves.unlink()
                                        return result
                                    if return_qty == 0:
                                        move_line.unlink()
                                        pass

                                    move_line.with_context(check_move_validity=False).write({'quantity': return_qty,'product_uom_id': uom_id,'create_uid': user.id})
                                    move_line_ids.append(move_line.id)
                            else:
                                result = {'success': False,'message': _('Product not found !!!')}
                                return result
                        self.env['account.move.line'].sudo().search(
                            [('id','not in',move_line_ids),('move_id','=',new_moves.id)]).with_context(check_move_validity=False).unlink()

                        new_moves.sudo().with_context(check_move_validity=False)._recompute_dynamic_lines()
                        if move_line_ids:
                            new_moves.with_user(user).with_context(check_move_validity=False).action_post()
                        result['message'] = _('Invoice Reversed Successfully.')
                    else:
                        if new_moves:
                            new_moves.unlink()
                        result = {'success': False,'message': _('Error On Create reverse invoice  !!!')}

                else:
                    result = {'success': False,'message': _('Error On Create reverse invoice  !!!')}
            else:
                result = {'success': False,'message': _('Error On Create reverse invoice  !!!')}

        except Exception as e:
            print(e)
            if new_moves:
                new_moves.unlink()
            result = {'success': False,'message': _('Error On Create reverse invoice (%s) !!!',str(e))}
            return result

        return result
    def create_multi_reverse(self, context,customer_id, **kwargs):
        result = {"success": True}
        user = context.get('user')
        reason = ''
        list_ret_invoices = []
        warehouse_id = context.get('user').assigned_warehouse_id.id or self._get_default_warehouse_id().id
        is_return_stock = False
        is_cancel_needed = False
        action_date = fields.date.today()
        invoice = 0
        invoices = []
        customer_obj = self.env['res.partner'].sudo().search([('id','=',customer_id)],limit=1)
        if not customer_obj:
            result = {'success': False,'message': _('Customer not found !!!')}
            return result

        if customer_obj:
            invoices = self.env['account.move'].sudo().with_user(user).search([('payment_state','!=','reversed'),('move_type','=','out_invoice'),('state','=','posted'),('partner_id','=',customer_obj.id)]).\
                filtered(lambda move:  move.invoice_date + datetime.timedelta(days=move.no_of_days_to_return) > action_date)
            if not invoices:
                result = {'success': False,'message': _('A Customer has not a Posted Invoices !!!')}
                return result
        # else:
        #     result = {'success': False,'message': _('invoice_ids must by sent !!!')}
        #     return result
        default_values_list = []
        if 'is_return_stock' in kwargs:
            if kwargs['is_return_stock'] == 1:
                is_return_stock = True
        if 'reason' in kwargs:
            reason = kwargs['reason']

        try:
            for invoice in invoices:
                if invoice:
                    Order = self.env['sale.order'].sudo().search([("invoice_ids","in",[invoice.id])],limit=1)

                    if invoice and invoice.state not in ('draft','cancel'):
                        default_values_list = _prepare_default_reversal(invoice, reason)
                        new_moves = invoice.sudo().with_user(user).with_context(check_move_validity=False)._reverse_moves([default_values_list],cancel=is_cancel_needed)
                        new_moves.invoice_line_ids
                        result['data'] = new_moves.id
                        # if 'lines' in kwargs:
                        if is_return_stock:
                            if Order and Order.picking_ids:
                                for pick in Order.picking_ids:
                                    if pick.state == 'done' and pick.picking_type_code == 'outgoing':
                                        self.with_user(user)._create_reverse_all_transfer(pick)

                        new_moves.sudo()._recompute_payment_terms_lines()
                        new_moves.sudo().with_user(user).with_context(check_move_validity=False).action_post()

                        list_ret_invoices.append(new_moves.id)
                        #
                        # else:
                        #     result = {'success': False,'message': _('Error On Create reverse invoices  !!!')}

                    # else:
                        # result = {'success': False,'message': _('Error On Create reverse invoices  !!!')}
            # else:
            #     result = {'success': False,'message': _('Error On Create reverse invoice  !!!')}
            if list_ret_invoices:
                result['message'] = _('Invoices Reversed Successfully.')
                result['data'] = list_ret_invoices
                result['success'] = True

        except Exception as e:
            print(e)
            result = {'success': False,'message': _('Error On Create reverse invoices (%s) !!!',str(e))}
            return result


        return result

    def fetch_toreturninvoices(self, context, **kwargs):
        result = {"success": True}
        user = context.get('user')
        list_ret_invoices = []
        invoices = []
        customer_id = 0
        action_date = fields.date.today()
        if 'customer_id' in kwargs:
            customer_id = int(kwargs['customer_id'])
        else:
            result = {'success': False,'message': _('Parameter customer_id  must be send !!!')}
            return result
        customer_obj = self.env['res.partner'].sudo().search([('id','=',customer_id)],limit=1)
        if not customer_obj:
            result = {'success': False,'message': _('Customer not found !!!')}
            return result

        if customer_obj:
            invoices = self.env['account.move'].sudo().with_user(user).search([('payment_state','!=','reversed'),('move_type','=','out_invoice'),('state','=','posted'),('partner_id','=',customer_obj.id)]).\
                filtered(lambda move:  (move.invoice_date + datetime.timedelta(days=move.no_of_days_to_return)) > action_date)
            if not invoices:
                result = {'success': True,'message': _('A Customer has not Invoices to Refund!!!')}
                result['data'] = {'invoices':[]}
                return result
        try:
            for invoice in invoices:
                if invoice:
                    if invoice and invoice.state not in ('draft','cancel'):
                        invoicedata = self.get_invoice(invoice.id)
                        if invoicedata:
                            list_ret_invoices.append(invoicedata)
            if list_ret_invoices:
                result['message'] = _('Invoices Fetched Successfully.')
                result['data'] = {'invoices':list_ret_invoices}
                result['success'] = True
            elif not list_ret_invoices:
                result = {'success': True,'message': _('A Customer has not Invoices to Refund!!!')}
                result['data'] = {'invoices':[]}
            return result

        except Exception as e:
            print(e)
            result = {'success': False,'message': _('Error On Fetch invoices (%s) !!!',str(e))}
            return result

        return result

    def _create_reverse_transfer(self, pick ,lines):
        user = self._context.get('user')
        stock_return_picking_form = Form(self.env['stock.return.picking'].sudo()
                                         .with_context(active_ids=[pick.id],active_id=pick.id,
                                                       active_model='stock.picking'))
        stock_return_picking = stock_return_picking_form.save()
        product_ids = []
        if lines:
            for line in lines:
                if 'product_id' in line and 'return_qty' in line:
                    Order_line = self.env['sale.order.line'].sudo().search(
                        [("product_id","=",int(line['product_id'])),('order_id','=',pick.sale_id.id)],
                        limit=1)

                    if line['return_qty'] > 0 and Order_line and Order_line.qty_delivered >= line['return_qty']:
                        return_move = stock_return_picking.product_return_moves.filtered(
                            lambda move: move.product_id.id == line['product_id']).quantity = line['return_qty']
                        stock_return_picking.product_return_moves.filtered(
                            lambda move: move.product_id.id == line['product_id']).to_refund= True
                        if return_move:
                            product_ids.append(line['product_id'])


        stock_return_picking.product_return_moves.filtered(
            lambda move: move.product_id.id not in product_ids).unlink()
        stock_return_picking_action = stock_return_picking.create_returns()

        return_pick = self.env['stock.picking'].sudo().browse(stock_return_picking_action['res_id'])
        for move in return_pick.move_line_ids_without_package:
            move.write({
                'qty_done': move.qty_done,
            })
        return_pick.action_confirm()
        for move in return_pick.move_lines:
            # move.quantity_done = move.product_uom_qty
            move.sudo().write({
                'quantity_done': move.product_uom_qty,
            })

        return_pick.sudo().with_context(skip_attachment=True).button_validate()

        return

    def _create_reverse_all_transfer(self, pick):
        user = self._context.get('user')
        stock_return_picking_form = Form(self.env['stock.return.picking']
                                         .with_context(active_ids=[pick.id],active_id=pick.id,
                                                       active_model='stock.picking'))
        stock_return_picking = stock_return_picking_form.save()

        stock_return_picking_action = stock_return_picking.create_returns()

        return_pick = self.env['stock.picking'].browse(stock_return_picking_action['res_id'])
        for move in return_pick.move_line_ids_without_package:
            move.write({
                'qty_done': move.qty_done,
            })
        return_pick.action_confirm()
        for move in return_pick.move_lines:
            # move.quantity_done = move.product_uom_qty
            move.sudo().write({
                'quantity_done': move.product_uom_qty,
            })

        return_pick.sudo().with_context(skip_attachment=True).button_validate()

        return

    def create_payment(self,context, **kwargs):
        result = {"success": True}
        user = context.get('user')
        order = {}
        amount_paid =0.0
        statement = ''

        if 'statement' in kwargs:
            statement = kwargs['statement']

        if 'amount_paid' in kwargs and float(kwargs['amount_paid']) > 0:
            amount_paid = float(kwargs['amount_paid'])
        else:
            result = {'success': False,'message': _('Parameter (amount_paid)  must by sent !!!')}

        if 'invoice_id' in kwargs:
            order = self.env['sale.order'].sudo().with_user(user).search([('user_id','=',user.id),('invoice_ids', 'in',[kwargs['invoice_id']])],limit=1)
            if not order:
                result = {'success': False,'message': _('Invoice not found !!!')}
                return result
        # elif 'order_id' in kwargs:
        #     order = self.env['sale.order'].sudo().with_user(user).search([('user_id','=',user.id),('id', '=',int(kwargs['order_id']))],limit=1)
        #     if not order:
        #         result = {'success': False,'message': _('Order not found !!!')}
        #         return result

        else:
            result = {'success': False,'message': _('One of Post Parameters(order_id,invoice_id) must by sent !!!')}
            return result
        try:
            if order:
                if order.invoice_ids and amount_paid > 0:
                    if order.invoice_ids.amount_residual <= 0:
                        result = {'success': False,'message': _('This invoice has already been full paid !!!')}
                        return result

                    payment_obj = self._create_payment_vals(order,user,amount_paid)
                    if payment_obj:
                        credit_aml = payment_obj.line_ids.filtered('credit')
                        order.invoice_ids.js_assign_outstanding_line(credit_aml.id)
                        if statement:
                            statement_date = Datetime.to_string(datetime.datetime.now())
                            note ="%s \n %s (%s) " % (order.invoice_ids.narration or "" , statement,statement_date)
                            order.invoice_ids.write({'narration': note})
                result['data'] = int(kwargs['invoice_id'])
                result['message'] = _('Payment Created.')
                return result
        except Exception as e:
            print(e)
            result = {'success': False,'message':'Error On Create Payment  !!!'}
        return result

    def create_multi_payment(self,context, **kwargs):
        result = {"success": True}
        user = context.get('user')
        order = {}
        amount_paid =0.0
        statement = ''
        listinvoices = []
        if 'statement' in kwargs:
            statement = kwargs['statement']

        if 'amount_paid' in kwargs and float(kwargs['amount_paid']) > 0:
            amount_paid = float(kwargs['amount_paid'])
        else:
            result = {'success': False,'message': _('Parameter (amount_paid)  must by sent !!!')}

        if 'invoice_ids' in kwargs:
            orders = self.env['sale.order'].sudo().with_user(user).search([('user_id','=',user.id),('invoice_ids', 'in',kwargs['invoice_ids'])])
            if not orders:
                result = {'success': False,'message': _('Invoice not found !!!')}
                return result
        else:
            result = {'success': False,'message': _('One of Post Parameters(order_id,invoice_ids) must by sent !!!')}
            return result
        try:
            if orders:
                for order in orders:
                    if order.invoice_ids and amount_paid > 0:
                        if order.invoice_ids[0].amount_residual <= 0:
                            result = {'success': False,'message': _('This invoice has already been full paid !!!')}
                            return result


                        payment_obj = self._create_payment_vals(order,user,amount_paid)
                        if payment_obj:
                            amount_paid = amount_paid - order.invoice_ids[0].amount_residual
                            credit_aml = payment_obj.line_ids.filtered('credit')
                            order.invoice_ids[0].js_assign_outstanding_line(credit_aml.id)
                            listinvoices.append(order.invoice_ids[0].id)
                            if statement:
                                statement_date = Datetime.to_string(datetime.datetime.now())
                                note ="%s \n %s (%s) " % (order.invoice_ids[0].narration or "" , statement,statement_date)
                                order.invoice_ids[0].write({'narration': note})

                result['data'] = listinvoices
                result['message'] = _('Payment Created.')
                return result
        except Exception as e:
            print(e)
            result = {'success': False,'message':'Error On Create Payment  !!!'}

        return result

    def create_transfer_money(self,context, **kwargs):
        context = dict(self.env.context)
        result = {"success": True}
        user = context.get('user')
        order = {}
        amount_paid =0.0
        statement = ''
        collection_by_balance = self.env['ir.config_parameter']\
            .sudo().get_param('smart_api.collection_by_balance')

        transfer_type = 'inbound'
        currency_id = user.company_id.currency_id.id
        if 'statement' in kwargs:
            statement = kwargs['statement']
        if 'currency_id' in kwargs:
            currency_id = kwargs['currency_id']

        if 'amount_paid' in kwargs and float(kwargs['amount_paid']) > 0:
            amount_paid = float(kwargs['amount_paid'])
        else:
            result = {'success': False,'message': _('Parameter (amount_paid)  must by sent !!!')}
            return result
        if 'transfer_type' in kwargs:
            transfer_type = kwargs['transfer_type']
        else:
            result = {'success': False,'message': _('Parameter (transfer_type)  must by sent !!!')}
            return result

        if 'customer_id' in kwargs:
            customer_id = self.env['res.partner'].sudo().search([('id','=',kwargs['customer_id'])],limit=1)
            if not customer_id:
                result = {'success': False,'message': _('Customer not found !!!')}
                return result

        else:
            result = {'success': False,'message': _('One of Post Parameters(customer_id) must by sent !!!')}
            return result
        try:
            payment_obj = self._create_payment_without_invoice_vals(user,customer_id,currency_id,transfer_type,amount_paid)

            if transfer_type == 'inbound':
                invoicesObj = self.env['account.move'].sudo()
                domain_invoice =[('partner_id','=',int(kwargs['customer_id'])),('payment_state','in',['partial', 'not_paid']),('amount_residual','>',0),('move_type','=','out_invoice'),('state','=','posted')]
                count_invoices = invoicesObj.search_count(domain_invoice)
                order = 'invoice_date desc'
                if collection_by_balance == 'older_all_overdue':
                    order = 'invoice_date asc'
                else:
                    order = 'invoice_date desc'
                if count_invoices > 0:
                    customer_invoices = invoicesObj.search(domain_invoice,order=order)
                    credit_aml = payment_obj.line_ids.filtered('credit')
                    if credit_aml:
                        credit_amount = credit_aml.credit
                        for customer_invoice in customer_invoices:
                            credit_amount = credit_amount - customer_invoice.amount_residual
                            customer_invoice.js_assign_outstanding_line(credit_aml.id)
                            if statement:
                                statement_date = Datetime.to_string(datetime.datetime.now())
                                note = "%s \n %s (%s) " % (customer_invoice.narration or "",statement,statement_date)
                                customer_invoice.write({'narration': note})

            if payment_obj:
                result['data'] = _getCustomersData(customer_id,context)[0]
                result['message'] = _('Transfer Created Successfully.')
            else:
                result = {'success': False,'message': _('Error On Create Transfer !!!')}

            return result
        except Exception as e:
            print(e)
            result = {'success': False,'message':_('Error On Create Transfer %s !!!',str(e))}
            return result

    def _create_payment_vals(self, order, user, amount_paid):
        payment_vals = {
            'date': datetime.date.today(),
            'amount': abs(amount_paid),
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'ref': order.invoice_ids.name,
            'journal_id': user.assigned_journal_id.id or self._get_default_journal_id().id,
            'currency_id': order.currency_id.id,
            'partner_id': order.partner_id.id,
            # 'company_id': user.company_id.id,
            'partner_bank_id': False,
            'payment_method_id': 1,
            # 'destination_account_id': order.invoice_ids.line_ids[1].account_id.id,

        }

        payment = self.env['account.payment'].with_user(user).create(payment_vals)
        payment.with_user(user).action_post()
        # payment.reconcile()
        return payment

    def _create_payment_without_invoice_vals(self,user,customer,currency_id,payment_type,amount_paid):
        payment_vals = {
            'date': datetime.date.today(),
            'amount': abs(amount_paid),
            'payment_type': payment_type if payment_type else 'inbound',
            'partner_type': 'customer',
            'ref': customer.name,
            'journal_id': user.assigned_journal_id.id or self._get_default_journal_id().id,
            'currency_id': currency_id if currency_id else user.company_id.currency_id.id,
            'partner_id': customer.id,
            # 'company_id': user.company_id.id,
            'partner_bank_id': False,
            'payment_method_id': 1,
            # 'destination_account_id': order.invoice_ids.line_ids[1].account_id.id,

        }

        payment = self.env['account.payment'].with_user(user).create(payment_vals)
        payment.with_user(user).action_post()
        # payment.reconcile()
        return payment


    def _create_payment_multi_invoice_vals(self,user,customer,currency_id,payment_type,amount_paid,to_reconcile):
        payment_vals = {
            'date': datetime.date.today(),
            'amount': abs(amount_paid),
            'payment_type': payment_type if payment_type else 'inbound',
            'partner_type': 'customer',
            'ref': customer.name,
            'journal_id': user.assigned_journal_id.id or self._get_default_journal_id().id,
            'currency_id': currency_id if currency_id else user.company_id.currency_id.id,
            'partner_id': customer.id,
            # 'company_id': user.company_id.id,
            'partner_bank_id': False,
            'payment_method_id': 1,
            # 'destination_account_id': order.invoice_ids.line_ids[1].account_id.id,

        }
        to_write = {}
        payment = self.env['account.payment'].with_user(user).create(payment_vals)
        # to_write = {'payment_id': payment.id}
        # line_ids = []
        # for write_off_line_val in write_off_line_vals:
        #     line_vals_list = payment._prepare_move_line_default_vals(write_off_line_vals=write_off_line_val)
        #     if line_vals_list:
        #         line_ids.append((0,0,line_vals_list[1]))
        # if line_ids:
        #     to_write = {'line_ids': line_ids}
        # payment.move_id.write(to_write)

        for lines in to_reconcile:
            # Batches are made using the same currency so making 'lines.currency_id' is ok.
            if payment.currency_id != lines.currency_id:
                liquidity_lines,counterpart_lines,writeoff_lines = payment._seek_for_lines()
                source_balance = abs(sum(lines.mapped('amount_residual')))
                payment_rate = liquidity_lines[0].amount_currency / liquidity_lines[0].balance
                source_balance_converted = abs(source_balance) * payment_rate

                # Translate the balance into the payment currency is order to be able to compare them.
                # In case in both have the same value (12.15 * 0.01 ~= 0.12 in our example), it means the user
                # attempt to fully paid the source lines and then, we need to manually fix them to get a perfect
                # match.
                payment_balance = abs(sum(counterpart_lines.mapped('balance')))
                payment_amount_currency = abs(sum(counterpart_lines.mapped('amount_currency')))
                if not payment.currency_id.is_zero(source_balance_converted - payment_amount_currency):
                    continue

                delta_balance = source_balance - payment_balance

                # Balance are already the same.
                if self.company_currency_id.is_zero(delta_balance):
                    continue

                # Fix the balance but make sure to peek the liquidity and counterpart lines first.
                debit_lines = (liquidity_lines + counterpart_lines).filtered('debit')
                credit_lines = (liquidity_lines + counterpart_lines).filtered('credit')

                payment.move_id.write({'line_ids': [
                    (1,debit_lines[0].id,{'debit': debit_lines[0].debit + delta_balance}),
                    (1,credit_lines[0].id,{'credit': credit_lines[0].credit + delta_balance}),
                ]})


        payment.with_user(user).action_post()

        domain = [('account_internal_type', 'in', ['receivable', 'payable']), ('reconciled', '=', False)]
        for lines in  to_reconcile:

            # When using the payment tokens, the payment could not be posted at this point (e.g. the transaction failed)
            # and then, we can't perform the reconciliation.
            if payment.state != 'posted':
                continue

            payment_lines = payment.line_ids.filtered_domain(domain)
            for account in payment_lines.account_id:
                (payment_lines + lines)\
                    .filtered_domain([('account_id', '=', account.id), ('reconciled', '=', False)])\
                    .reconcile()
        # payment.reconcile()
        return payment


    def get_order(self,order_id):
        context = dict(self.env.context)
        orderObj = self.env['sale.order'].sudo()
        Order = orderObj.search([("id","=",order_id)],limit=1)

        state_value = dict(orderObj.fields_get(["state"],['selection'])['state']["selection"])
        if Order:

            amount_paid = 0.0
            amount_paid_details = []
            order_invoice = False
            if Order.invoice_ids :
                for invoice in Order.invoice_ids:
                    if invoice.move_type == 'out_invoice' and invoice.state == 'posted' and not order_invoice:
                        order_invoice = invoice
            if order_invoice:
                reconciled_payments_widget_vals = json.loads(order_invoice.invoice_payments_widget)
                if reconciled_payments_widget_vals and 'content' in reconciled_payments_widget_vals:
                    for vals in reconciled_payments_widget_vals['content']:
                        amount_paid += vals['amount']
                        temppayments = {
                            'payment_id': vals['payment_id'],
                            'name': vals['ref'].replace(' (%s)' % order_invoice.name,''),
                            'amount': round(vals['amount'],1),
                            'currency': vals['currency'],
                            'date': vals['date'],
                        }
                        amount_paid_details.append(temppayments)

            order_currency= {'currency_id': Order.currency_id.id, 'currency_symbol': Order.currency_id.symbol}
            result = {'order_id': Order.id,
                      'invoice_id': order_invoice.id if order_invoice else 0,
                      'invoice_name': order_invoice.name  if order_invoice else "",
                      'name': Order.name or "",
                      'customer': _getCustomersData(Order.partner_id, context)[0],
                      'create_date': Datetime.to_string(Order.create_date) or "",
                      'invoice_date_due': Date.to_string(order_invoice.invoice_date_due) if order_invoice else  "",
                      'payment_term_id': Order.payment_term_id.id,
                      'currency': order_currency,
                      'amount_total': Order.amount_total,
                      'amount_paid': amount_paid,
                      'amount_paid_details': amount_paid_details or [],
                      'amount_residual': order_invoice.amount_residual if order_invoice else  0.0,
                      'discount_total': Order.iq_total_disc or 0.0,
                      'status': state_value[Order.state],
                      'user': Order.user_id.name,
                      'note': order_invoice.narration if order_invoice else "",
                      'shipping_address': app_display_address(Order.partner_shipping_id._display_address(),
                                                                       Order.partner_shipping_id.name),
                      'billing_address': app_display_address(Order.partner_invoice_id._display_address(),
                                                                      Order.partner_invoice_id.name),
                      'items': [],
                      'invoices': []}
            if Order.order_line:
                for line in Order.order_line:
                    if line.product_id:
                        temp = {

                            "product_id": line.product_id and line.product_id.id or "",
                            'name': line.name or "",
                            'product_name': line.product_id and line.product_id.display_name or "",
                            'image': _get_image_url(self._get_base_url(),'product.product',
                                                    line.product_id and line.product_id.id or "",'image_1920',
                                                    line.product_id and line.product_id.write_date or 0),
                            # 'qty': "%s %s" % (line.sudo().product_uom_qty,line.sudo().product_uom.name),
                            'qty':line.sudo().product_uom_qty,
                            'qty_invoiced': line.sudo().qty_invoiced,
                            'qty_delivered': line.sudo().qty_delivered,
                            'unit_id':line.sudo().product_uom.id,
                            'price_unit': line.price_unit,
                            'price_subtotal': line.price_subtotal,
                            'price_total': line.price_total,
                            'discount': "%s" % (line.discount and "%s %%" % line.discount or ""),
                            'state': state_value[line.state],

                        }
                        result['items'].append(temp)
            for invoice in Order.invoice_ids:
                result['invoices'].append(self.get_invoice(invoice.id))
        else:
            result = []
        return result

    def get_invoice(self,invoice_id):
        context = dict(self.env.context)
        invoiceObj = self.env['account.move'].sudo()
        invoice = invoiceObj.search([("id","=",invoice_id)],limit=1)
        orderObj = self.env['sale.order'].sudo()
        Order = orderObj.search([("invoice_ids","in",[invoice.id])],limit=1)

        state_value = dict(orderObj.fields_get(["state"],['selection'])['state']["selection"])
        move_type = dict(invoiceObj.fields_get(["move_type"],['selection'])['move_type']["selection"])
        if Order:
            amount_paid = 0.0
            amount_paid_details = []
            if Order.invoice_ids and invoice.state == 'posted':
                reconciled_payments_widget_vals = json.loads(invoice.invoice_payments_widget)
                if reconciled_payments_widget_vals and 'content' in reconciled_payments_widget_vals:
                    for vals in reconciled_payments_widget_vals['content']:
                        amount_paid += vals['amount']
                        temppayments = {
                            'payment_id': vals['payment_id'],
                            'name': vals['ref'].replace(' (%s)' % invoice.name,''),
                            'amount': round(vals['amount'],1),
                            'currency': vals['currency'],
                            'date': vals['date'],
                        }
                        amount_paid_details.append(temppayments)

            order_currency= {'currency_id': Order.currency_id.id, 'currency_symbol': Order.currency_id.symbol}
            result = {'order_id': Order.id,
                      'invoice_id': invoice.id or 0,
                      'invoice_name': invoice.name or "",
                      'name': Order.name or "",
                      'customer': _getCustomersData(Order.partner_id, context)[0],
                      'create_date': Datetime.to_string(Order.create_date) or "",
                      'invoice_date_due': Date.to_string(invoice.invoice_date_due) or "",
                      'payment_term_id': Order.payment_term_id.id,
                      'currency': order_currency,
                      'amount_total': Order.amount_total,
                      'amount_paid': amount_paid,
                      'amount_paid_details': amount_paid_details or [],
                      'amount_residual':invoice.amount_residual or 0.0,
                      'discount_total': Order.iq_total_disc or 0.0,
                      'status': state_value[Order.state],
                      'note': invoice.narration or "",
                      'user': Order.user_id.name,
                      'is_refund_invoice': True if invoice.move_type == 'out_refund' else False,
                      'shipping_address': app_display_address(Order.partner_shipping_id._display_address(),
                                                                       Order.partner_shipping_id.name),
                      'billing_address': app_display_address(Order.partner_invoice_id._display_address(),
                                                                      Order.partner_invoice_id.name),
                      'items': []}
            if Order.order_line:
                for line in Order.order_line:
                    if line.product_id:
                        temp = {

                            "product_id": line.product_id and line.product_id.id or "",
                            'name': line.name or "",
                            'product_name': line.product_id and line.product_id.display_name or "",
                            'image': _get_image_url(self._get_base_url(),'product.product',
                                                    line.product_id and line.product_id.id or "",'image_1920',
                                                    line.product_id and line.product_id.write_date),
                            # 'qty': "%s %s" % (line.sudo().product_uom_qty,line.sudo().product_uom.name),
                            'qty': line.sudo().product_uom_qty,
                            'qty_invoiced': line.sudo().qty_invoiced,
                            'qty_delivered': line.sudo().qty_delivered,
                            'unit_id': line.sudo().product_uom.id,
                            'price_unit': line.price_unit,
                            'price_subtotal': line.price_subtotal,
                            'price_total': line.price_total,
                            'discount': "%s" % (line.discount and "%s %%" % line.discount or ""),
                            'state': state_value[line.state],

                        }
                        result['items'].append(temp)
        else:
            result = {}
        return result

    def fetch_paymentTerms(self, context, **kwargs):
        paymentTermsObj = self.env['account.payment.term'].sudo().search([("active","=",True)])
        result = {'data': {}}
        result['count'] = paymentTermsObj.search_count([("active","=",True)])

        paymentTermsObjdata = {'terms': []}
        paymentTermsObjlist =[]
        for paymentTermObj in paymentTermsObj:
            temp = {
                'name': paymentTermObj.name,
                'term_id': paymentTermObj.id,
                # 'lines': paymentTermObj.line_ids,
            }
            paymentTermsObjlist.append(temp)

        paymentTermsObjdata['terms'] = paymentTermsObjlist
        result['data'] = paymentTermsObjdata

        return result

    def get_paymentTerms(self):
        paymentTermsObj = self.env['account.payment.term'].sudo().search([("active","=",True)])

        paymentTermsObjlist =[]
        for paymentTermObj in paymentTermsObj:
            temp = {
                'name': paymentTermObj.name,
                'term_id': paymentTermObj.id,
                # 'lines': paymentTermObj.line_ids,
            }
            paymentTermsObjlist.append(temp)

        return paymentTermsObjlist

    def get_visitPurposes(self):
        visit_obj = self.env['customer.visit'].sudo()
        selection_list = []
        selection = visit_obj.fields_get(["visit_type"],['selection'])['visit_type']["selection"]
        for value, label in selection:
            option = {
                'id': value,
                'name': label,
            }
            selection_list.append(option)
        result = {'data': {'options': selection_list}}

        return result


    def fetch_paymentMethods(self, context, **kwargs):
        paymentmethods = []
        paymentmethods.append({'name': _('cash'), 'id': 1, 'terms': []})

        paymentmethods.append({'name': _('in term'), 'id': 2, 'terms': self.get_paymentTerms()})

        result = {'count': 2, 'data': {'methods': paymentmethods }}
        return result


    def fetch_priceLists(self, context, **kwargs):

        company_id = context.get('company_id') or self._getdefaultCompany_id()
        domain = ['|', '&',('company_id', '=', company_id),('active', '=',True),'&',('company_id', '=',False),('active', '=', True)]
        priceListsObj = self.env['product.pricelist'].search(domain)
        result = {'data': {}}
        result['count'] = priceListsObj.search_count(domain)
        priceListsObjdata = {'pricelists': []}
        priceListslist =[]
        for priceListObj in priceListsObj:
            priceList_currency= {'currency_id': priceListObj.currency_id.id, 'currency_name': priceListObj.currency_id.name, 'currency_symbol': priceListObj.currency_id.symbol}

            temp = {
                'name': priceListObj.name,
                'pricelist_id': priceListObj.id,
                'currency': priceList_currency,
            }
            priceListslist.append(temp)

        priceListsObjdata['pricelists'] = priceListslist
        result['data'] = priceListsObjdata

        return result

    def fetch_countries(self, context, **kwargs):
        company_id = context.get('company_id') or self._getdefaultCompany_id()
        result = {'offset': int(kwargs.get('offset', 0))}
        default_country_id = self.env.context.get('user').company_id.country_id
        domain = []
        if 'search' in kwargs:
            s = kwargs['search']
            domain += [('name', 'ilike', s)]

        countriesObj = self.env['res.country'].search(domain, limit=1000, offset=result["offset"] or 0, order=kwargs.get('order', 0))
        result = {'data': {}}
        result['count'] = countriesObj.search_count(domain)
        countriesObjdata = {'countries': []}
        countriesObjlist =[]
        for countryObj in countriesObj:
            statelist = []
            for state in countryObj.state_ids:
                tempstate = {
                    'name': state.name,
                    'state_id': state.id,
                }
                statelist.append(tempstate)

            temp = {
                'name': countryObj.name,
                'country_id': countryObj.id,
                'phone_code': countryObj.phone_code,
                'states': statelist,
            }
            countriesObjlist.append(temp)

        if default_country_id and not 'search' in kwargs and not 'filter' in kwargs:
            statedefaultcountrylist = []
            for state in default_country_id.state_ids:
                tempstate = {
                    'name': state.name,
                    'state_id': state.id,
                }
                statelist.append(tempstate)

            defaultcountry = {
                'name': default_country_id.name,
                'country_id': default_country_id.id,
                'phone_code': default_country_id.phone_code,
                'states': statedefaultcountrylist,
            }
            countriesObjlist.insert(0, defaultcountry)

        countriesObjdata['countries'] = countriesObjlist
        result['data'] = countriesObjdata

        return result

    def fetch_currencies(self, context, **kwargs):
        default_currency_id = context.get('currency_id')

        company_id = context.get('company_id') or self._getdefaultCompany_id()
        domain = [('active', '=', True)]
        currenciesObj = self.env['res.currency'].search(domain)
        result = {'data': {}}
        result['count'] = currenciesObj.search_count(domain)
        currenciesObjdata = {'currencies': []}
        currenciesObjlist =[]
        for currencyObj in currenciesObj:
            is_default = False
            if default_currency_id == currencyObj.id:
                is_default = True
            temp = {
                'name': currencyObj.name,
                'currency_id': currencyObj.id,
                'symbol': currencyObj.symbol,
                'default': is_default,
                'rate': currencyObj.rate,
            }
            currenciesObjlist.append(temp)

        currenciesObjdata['currencies'] = currenciesObjlist
        result['data'] = currenciesObjdata

        return result

    def _get_base_url(self):
        return self.env['ir.config_parameter'].get_param('web.base.url') + '/'

    def _default_language(self):
        lc = self.env['ir.default'].get('res.partner', 'lang')
        dl = self.env['res.lang'].search([('code', '=', lc)], limit=1)
        return dl.id if dl else self.env['res.lang'].search([]).ids[0]

    def _active_languages(self):
        return self.env['res.lang'].search([]).ids

    def dashboard_data_chart(self, smartapi_Obj, user_Obj):

        location_distance_buffer = self.env['ir.config_parameter']\
            .sudo().get_param('customer_visits.location_distance_buffer') or 0
        collections = self.env['account.payment'].sudo()
        invoices = self.env['account.move'].sudo()
        customers = self.env['res.partner'].sudo()

        domain_collections = [('partner_type','=','customer'),('user_id','=',user_Obj.id),('state','=','posted'),('payment_type','=','inbound')]
        domain_invoices = [('invoice_user_id','=',user_Obj.id),('state','=','posted'),('move_type','in',('out_invoice','out_refund'))]
        domain_customers = _get_customers_domain()

        thismonth = fields.Date.today()
        start_date = datetime.datetime(thismonth.year,thismonth.month,1)
        this_day = fields.Date.today()

        domain_collections += [('date','>=',start_date),('date','<=',this_day)]
        domain_invoices += [('invoice_date','>=',start_date),('invoice_date','<=',this_day)]
        salespersons_customers_only = self.env['ir.config_parameter']\
            .sudo().get_param('smart_api.salespersons_customers_only')
        if salespersons_customers_only and 'salesperson_ids' in customers._fields:
            domain_customers += [('salesperson_ids','in',user_Obj.id)]
        elif salespersons_customers_only:
            domain_customers += [('user_id','=',user_Obj.id)]

        done_payments = collections.search(domain_collections)
        done_invoices = invoices.search(domain_invoices)
        total_customers = customers.search_count(domain_customers)

        payment_month_total = sum(done_payments.mapped('amount')) or 0
        payment_month_total_st =_displayWithCurrency(smartapi_Obj.default_lang,payment_month_total,user_Obj.company_id.currency_id.symbol,user_Obj.company_id.currency_id.position)

        invoice_month_total = sum(done_invoices.mapped('amount_total')) or 0
        invoice_month_total_st =_displayWithCurrency(smartapi_Obj.default_lang,invoice_month_total,user_Obj.company_id.currency_id.symbol,user_Obj.company_id.currency_id.position)

        account_payment = self.env['account.payment'].sudo()
        domain =[('user_id', '=', user_Obj.id), ('state', '=', 'posted')]
        done_payments = account_payment.search(domain)
        today = fields.Date.today()
        this_month = fields.Date.today().strftime('%Y-%m')
        this_week = datetime.datetime.strptime(fields.Date.to_string(fields.Date.from_string(today) + datetime.timedelta(days=7)),'%Y-%m-%d').date()
        all_total = sum(done_payment.amount for done_payment in done_payments)
        month_total = sum(done_payment.amount for done_payment in done_payments if done_payment.date.strftime('%Y-%m') == this_month)
        week_total = sum(done_payment.amount for done_payment in done_payments if done_payment.date >= today and  done_payment.date <= this_week )
        employee = user_Obj.employee_id
        action_date_only = fields.date.today()
        attendance = 0
        if employee:
            last_attendance_before_check_in = self.env['hr.attendance'].sudo().search([
                ('employee_id','=',employee.id),
            ],order='check_in desc',limit=1)
            if not last_attendance_before_check_in:
                attendance = 1
            elif last_attendance_before_check_in.check_in.strftime('%Y-%m-%d') != action_date_only.strftime('%Y-%m-%d'):
                attendance = 1
            elif last_attendance_before_check_in.check_in.strftime('%Y-%m-%d') == action_date_only.strftime('%Y-%m-%d') and not last_attendance_before_check_in.check_out :
                attendance = 0
            elif last_attendance_before_check_in.check_in.strftime('%Y-%m-%d') == action_date_only.strftime('%Y-%m-%d') and last_attendance_before_check_in.check_out.strftime('%Y-%m-%d') == action_date_only.strftime('%Y-%m-%d'):
                attendance = int(last_attendance_before_check_in.current_state)

        else:
            attendance = 3
        discount_access = True
        max_discount = int(user_Obj.max_discount) or 0
        saleperson_type = 'cashvan'

        if user_Obj.has_group('cashvan_presale.presale_group_id'):
            saleperson_type = 'presale'
        if user_Obj.has_group('iq_extend_sales_alanwan_customs.f_salediscaccess_group_id'):
            discount_access = False
            max_discount = 0


        temp = {
            "data": {
                "total": {
                    "all": _displayWithCurrency(smartapi_Obj.default_lang, all_total, smartapi_Obj.currency_id.symbol, smartapi_Obj.currency_id.position),
                    "month": _displayWithCurrency(smartapi_Obj.default_lang, month_total, smartapi_Obj.currency_id.symbol, smartapi_Obj.currency_id.position),
                    "week":  _displayWithCurrency(smartapi_Obj.default_lang, week_total, smartapi_Obj.currency_id.symbol, smartapi_Obj.currency_id.position)
                },
                "saleperson_type": saleperson_type,
                "discount_access": discount_access,
                "max_discount": max_discount,
                "attendance": attendance,
                'total_collect_this_month': payment_month_total_st or '',
                'total_customers': total_customers or 0,
                'total_commission_this_month': '',
                'total_invoiced_this_month': invoice_month_total_st or '',
                'location_distance_buffer': int(location_distance_buffer) or 0,

            }
        }
        return temp

    def dashboard_data(self, seller_Obj):
        SaleOrder = self.env['sale.order'].sudo()
        new_sol_count = SaleOrder.search_count(
            [('user_id', '=', seller_Obj.id), ('state', '=', 'new')])
        approved_sol_count = SaleOrder.search_count(
            [('user_id', '=', seller_Obj.id), ('state', '=', 'approved')])
        shipped_sol_count = SaleOrder.search_count(
            [('user_id', '=', seller_Obj.id), ('state', '=', 'shipped')])
        temp = {
            "new_solCount": new_sol_count,
            "approved_solCount": approved_sol_count,
            "shipped_solCount": shipped_sol_count,
            "total": {
                "label": "Total Amount",
                "value": seller_Obj.total_mp_payment
            },
            "balance": {
                "label": "Balance Amount",
                "value": seller_Obj.balance_mp_payment
            },

        }
        return temp

    def _get_default_journal_id(self):
        if self.env.user.assigned_journal_id:
            return self.env.user.assigned_journal_id.id
        else:
            company_id = self.env.context.get('company_id') or self._getdefaultCompany_id()
            domain = ['|','&',('company_id','=',company_id),('active','=',True),'&',('type','in',('cash','bank')),
                      ('type','in',('cash','bank'))]

            # domain = ['|','&',('company_id', '=', self.env.user.company_id.id),('type', 'in', ('cash','bank')) ]
            journal = self.env['account.journal'].sudo().search(domain, limit=1,order='id desc')
            if journal:
                return journal[0]
            else:
                return False

    def _get_default_warehouse_id(self):
        if self.env.user.assigned_warehouse_id:
            return self.env.user.assigned_warehouse_id
        else:
            return self.env.user._get_default_warehouse_id()

    def _getdefaultCompany_id(self):
        comp_id = self.env['res.company'].search([], limit=1)
        return comp_id.id

    name = fields.Char('App Title', default="Smart Van APP", required=1)
    # salesperson_id = fields.Many2one('res.users', string='Default Salesperson')
    # salesteam_id = fields.Many2one('crm.team', string='Default Sales Team')
    api_key = fields.Char(string='API Secret key', default="dummySecretKey", required=1)
    fcm_api_key = fields.Char(string='FCM Api key')
    color_scheme = fields.Selection([
        ('default', 'Default'),
        ('red-green', 'Red-Green'),
        ('light-green', 'Light Green'),
        ('deep-purple-pink', 'Deep Purple-Pink'),
        ('blue-orange', 'Blue Orange'),
        ('light-blue-red', 'Light Blue-Red')],
        string='Color Scheme', required=True,
        default='default',
        help="Color Options for your App.")

    default_lang = fields.Many2one('res.lang', string='Default Language', default=_default_language)

    pricelist_id = fields.Many2one('product.pricelist', string='Default Pricelist')
    currency_id = fields.Many2one(
        'res.currency', related='pricelist_id.currency_id', string='Default Currency', readonly=True)

    product_limit = fields.Integer(
        default=10, string='Limit Products per page', help='Used in Pagination', required=1)

    company_id = fields.Many2one('res.company', default=_getdefaultCompany_id,
                                 help="select company id for the app")

    def unlink(self):
        raise UserError(_('You cannot remove/deactivate this Configuration.'))


class FcmRegisteredDevices(models.Model):
    _name = 'fcm.registered.devices'
    _description = 'All Registered Devices on FCM for Push Notifications.'
    _order = 'write_date desc'

    def name_get(self):
        res = []
        for record in self:
            name = record.user_id and record.user_id.name or ''
            res.append((record.id, "%s(DeviceId:%s)" % (name, record.device_id)))
        return res

    name = fields.Char('Name')
    token = fields.Text('FCM Registration ID', readonly=True)
    device_id = fields.Char('Device Id', readonly=True)
    user_id = fields.Many2one('res.users', string="User", readonly=True, index=True)
    active = fields.Boolean(default=True, readonly=True)
    write_date = fields.Datetime(string='Last Update', readonly=True)
    description = fields.Text('Description', readonly=True)


class FcmRegisteredTopics(models.Model):
    _name = 'fcm.registered.topics'
    _description = 'All Registered Topics for Push Notifications.'

    name = fields.Char('Topic Name', required=True)


class PushNotificationTemplate(models.Model):
    _name = 'smart.push.notification.template'
    _description = 'Smart Push Notification Templates'
    _order = "name"

    def _addMe(self, data):
        self.env["smart.notification.messages"].sudo().create(data)
        return True

    def _get_key(self):
        smart_api = self.env['smart_api'].sudo().search([], limit=1)
        return smart_api and smart_api.fcm_api_key or ""

    @api.model
    def _pushMe(self, key, payload_data, data=False):
        status = True
        summary = ""
        try:
            push_service = FCMAPI(api_key=key)
            summary = push_service.send([payload_data])
            if data:
                self._addMe(data)
        except Exception as e:
            status = False
            summary = "Error: %r" % e
        return [status, summary]

    @api.model
    def _send(self, to_data, user_id=False, max_limit=20):

        if type(to_data) != dict:
            return False
        if not to_data.get("to", False) and not to_data.get("registration_ids", False):
            if not user_id:
                return False
            reg_data = self.env['fcm.registered.devices'].sudo().search_read(
                [('user_id', '=', user_id)], limit=max_limit, fields=['token'])
            if not reg_data:
                return False
            to_data = {
                "registration_ids": [r['token'] for r in reg_data]
            }
        notification = dict(title=self.notification_title,
                            body=self.notification_body, sound="default")
        if self.notification_color:
            notification['color'] = self.notification_color
        if self.notification_tag:
            notification['tag'] = self.notification_tag

        fcm_payload = dict(notification=notification)
        fcm_payload.update(to_data)
        data_message = dict(type="", id="", domain="", image="", name="")

        if self.banner_action == 'product':
            data_message['type'] = 'product'
            data_message['id'] = self.product_id.id
            data_message['name'] = self.product_id.name
        elif self.banner_action == 'category':
            data_message['type'] = 'category'
            data_message['id'] = self.category_id.id
            data_message['name'] = self.category_id.name
        elif self.banner_action == 'custom':
            data_message['type'] = 'custom'
            data_message['domain'] = "[('id','in',%s)]" % self.product_ids.ids
            data_message['name'] = self.notification_title
        else:
            data_message['type'] = 'none'
        data_message['image'] = _get_image_url(self._context.get(
            'base_url'), 'smart.push.notification.template', self.id, 'image', self.write_date)
        data_message['notificationId'] = random.randint(1, 99999)
        fcm_payload['data'] = data_message
        domain = [('res_model', '=', self._name),
            ('res_field', '=', 'image'),
            ('res_id', 'in', [self.id])]
        attachment = self.env['ir.attachment'].sudo().search(domain)
        if user_id:
            data = dict(
                title=self.notification_title, body=self.notification_body, user_id=user_id,
                banner=attachment.datas, datatype='default'
            )
        return self._pushMe(self._get_key(), json.dumps(fcm_payload).encode('utf8'), user_id and data or False)

    name = fields.Char('Name', required=True, translate=True)
    notification_color = fields.Char('Color', default='PURPLE')
    notification_tag = fields.Char('Tag')
    notification_title = fields.Char('Title', required=True, translate=True)
    active = fields.Boolean(default=True, copy=False)
    notification_body = fields.Text('Body', translate=True)
    image = fields.Binary('Image', attachment=True)
    banner_action = fields.Selection([
        ('product', 'Open Product Page'),
        ('category', 'Open Category Page'),
        ('custom', 'Open Custom Collection Page'),
        ('none', 'Do nothing')],
        string='Action', required=True,
        default='none',
        help="Define what action will be triggerred when click/touch on the banner.")
    product_id = fields.Many2one('product.template', string='Choose Product')
    product_ids = fields.Many2many('product.template', string='Choose Products')
    device_id = fields.Many2one('fcm.registered.devices', string='Select Device')
    total_views = fields.Integer('Total # Views', default=0, readonly=1, copy=False)
    condition = fields.Selection([
        ('signup', 'User`s SignUp'),
        ('orderplaced', "Order Placed")
    ], string='Condition', required=True, default='signup')

    def dry_run(self):
        self.ensure_one()
        to_data = dict(to=self.device_id and self.device_id.token or "")
        result = self._send(
            to_data, self.device_id and self.device_id.user_id and self.device_id.user_id.id or False)
        # raise UserError('Result: %r'%result)

    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {}, name=_('%s(copy)') % self.name)
        return super(PushNotificationTemplate, self).copy(default)


class PushNotification(models.Model):
    _name = 'smart.push.notification'
    _description = 'Smart Push Notification'
    _order = "activation_date, name"
    _inherit = ['smart.push.notification.template']

    @api.model
    def parse_n_push(self, max_limit=20, registration_ids=None):
        to_data = dict()
        if self.notification_type == 'token-auto':
            reg_data = self.env['fcm.registered.devices'].sudo(
            ).search_read(limit=max_limit, fields=['token'])
            registration_ids = [r['token'] for r in reg_data]
        elif self.notification_type == 'token-manual':
            registration_ids = [d.token for d in self.device_ids]
        elif self.notification_type == 'topic':
            to_data['to'] = '/topics/%s' % self.topic_id.name
        else:
            return [False, "Insufficient Data"]

        if registration_ids:
            if len(registration_ids) > 1:
                to_data['registration_ids'] = registration_ids
            else:
                to_data['to'] = registration_ids[0]
        return self._send(to_data)

    summary = fields.Text('Summary', readonly=True)
    activation_date = fields.Datetime('Activation Date', copy=False)
    notification_type = fields.Selection([
        ('token-auto', 'Token-Based(All Reg. Devices)'),
        ('token-manual', 'Token-Based(Selected Devices)'),
        ('topic', 'Topic-Based'),
    ],
        string='Type', required=True,
        default='token-auto')
    topic_id = fields.Many2one('fcm.registered.topics', string='Choose Topic')
    device_ids = fields.Many2many('fcm.registered.devices', string='Choose Devices/Customers')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('hold', 'Hold'),
        ('error', 'Error'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')

    def action_cancel(self):
        for record in self:
            record.state = 'cancel'
        return True

    def action_confirm(self):
        for record in self:
            record.state = 'confirm'
        return True

    def action_draft(self):
        for record in self:
            record.state = 'draft'
        return True

    def action_hold(self):
        for record in self:
            record.state = 'hold'
        return True

    def push_now(self):
        for record in self:
            response = record.parse_n_push()
            record.state = response[0] and 'done' or 'error'
            record.summary = response[1]
        return True

    def duplicate_me(self):
        self.ensure_one()
        action = self.env.ref('smart_api.smart_push_notification_action').read()[0]
        action['views'] = [(self.env.ref('smart_api.smart_push_notification_template_view_form').id, 'form')]
        action['res_id'] = self.copy().id
        return action


class NotificationMessages(models.Model):
    _name = 'smart.notification.messages'
    _description = 'Notification Messages'

    name = fields.Char('Message Name', default='/', index=True, copy=False, readonly=True)
    title = fields.Char('Title')
    subtitle = fields.Char('Subtitle')
    body = fields.Text('Body')
    icon = fields.Binary('Icon')
    banner = fields.Binary('Banner')
    is_read = fields.Boolean('Is Read', default=False, readonly=True)
    user_id = fields.Many2one('res.users', string="User", index=True)
    active = fields.Boolean(default=True, readonly=True)
    period = fields.Char('Period', compute='_compute_period')
    datatype = fields.Selection([
        ('default', 'Default'),
        ('order', 'Order')],
        string='Data Type', required=True,
        default='default',
        help="Notification Messages Data Type for Smart VAN App.")

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('smart.notification.messages')
        return super(NotificationMessages, self).create(vals)

    def _compute_period(self):
        for i in self:
            i.period = _easy_date(i.create_date)
