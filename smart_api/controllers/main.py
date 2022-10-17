from odoo import _
from odoo.addons.smart_api.tool.service import WebServices
from odoo.http import request, route
from odoo.addons.smart_api.tool.help import _get_image_url
import logging
import json
_logger = logging.getLogger(__name__)


class SmartApi(WebServices):

    @route('/smart_api/user/login', csrf=False, type='http', auth="none", methods=['POST'])
    def login(self, **kwargs):
        kwargs['detailed'] = True
        response = self._authenticate(True, **kwargs)
        self._tokenUpdate(user_id=response.get('userId'))
        return self._response('login', response)

    @route('/smart_api/user/signOut', csrf=False, type='http', auth="none", methods=['POST'])
    def signOut(self, **kwargs):
        response = self._authenticate(False, **kwargs)
        if response.get('success'):
            response['message'] = "Have a Good Day !!!"
            self._tokenUpdate()
        return self._response('signOut', response)

    @route('/smart_api/user/resetPassword', csrf=False, type='http', auth="none", methods=['POST'])
    def resetPassword(self, **kwargs):
        response = self._authenticate(False, **kwargs)
        if response.get('success'):
            smartapi = request.env['smart_api'].sudo().with_context(response.get("context"))
            result = smartapi.resetPassword(self._mData.get('email', False))
            response.update(result)
        return self._response('resetPassword', response)

    @route('/smart_api/user/updateProfile', csrf=False, type='http', auth="none", methods=['POST'])
    def saveMyDetails(self, **kwargs):
        response = self._authenticate(True, **kwargs)
        if response.get('success'):
            result = {}
            smartapi = request.env['smart_api'].sudo()
            User = response.get('context',{}).get('user').sudo()
            base_url = response.get('context',{}).get('base_url')
            if User:
                result['message'] = _("Updated Successfully.")
                if self._mData.get('image'):
                    try:
                        User.write({'image_1920': self._mData['image']})
                        # result['userProfileImage'] = _get_image_url(
                        #     base_url, 'res.user', User.id, 'image_1920', User.write_date)
                    except Exception as e:
                        result['message'] = _("Please try again later")+" %r" % e
                if self._mData.get('name'):
                    User.write({'name': self._mData['name']})
                if self._mData.get('password'):
                    User.write({'password': self._mData['password']})
            else:
                result = {'success': False, 'message': _('Account not found !!!')}
            result['data'] = smartapi.fetch_user_info(User)
            response.update(result)
        return self._response('saveMyDetails', response)

    @route('/smart_api/attendance/<int:user_id>', csrf=False, type='http', auth="none", methods=['POST'])
    def userAttendance(self, user_id, **kwargs):
        response = self._authenticate(True, **kwargs)
        context = response.get('context')
        if response.get('success'):
            smartapi = request.env['smart_api'].sudo().with_context(response.get("context"))
            Postdata = self._mData or {}
            result = smartapi.attendance(context=response.get("context"),user_id=user_id, **Postdata)
            response.update(result)

        return self._response('userAttendance', response)

    @route('/smart_api/newvisit/<int:customer_id>', csrf=False, type='http', auth="none", methods=['POST'])
    def createVisit(self, customer_id, **kwargs):

        response = self._authenticate(True, **kwargs)
        context = response.get('context')
        if response.get('success'):
            smartapi = request.env['smart_api'].sudo().with_context(response.get("context"))
            Postdata = self._mData or {}
            result = smartapi.createvisit(context=response.get("context"), customer_id=customer_id, **Postdata)
            response.update(result)

        return self._response('createVisit', response)

    @route('/smart_api/customerVisit', csrf=False, type='http', auth="none", methods=['GET'])
    def CustomerVisits(self, **kwargs):

        response = self._authenticate(True, **kwargs)
        context = response.get('context')
        if response.get('success'):
            smartapi = request.env['smart_api'].sudo().with_context(response.get("context"))
            result = smartapi.fetch_customer_visit(context=response.get("context"),**kwargs)
            response.update(result)

        return self._response('CustomerVisits', response)
    @route('/smart_api/updatevisit/<int:visit_id>', csrf=False, type='http', auth="none", methods=['POST'])
    def UpdateVisit(self, visit_id, **kwargs):

        response = self._authenticate(True, **kwargs)
        context = response.get('context')
        if response.get('success'):
            smartapi = request.env['smart_api'].sudo().with_context(response.get("context"))
            Postdata = self._mData or {}
            result = smartapi.updatevisit(context=response.get("context"), visit_id=visit_id, **Postdata)
            response.update(result)

        return self._response('updateVisit', response)

    @route('/smart_api/visitdone/<int:visit_id>', csrf=False, type='http', auth="none", methods=['POST'])
    def DoneVisit(self, visit_id, **kwargs):

        response = self._authenticate(True, **kwargs)
        context = response.get('context')
        if response.get('success'):
            smartapi = request.env['smart_api'].sudo().with_context(response.get("context"))
            Postdata = self._mData or {}
            result = smartapi.donevisit(context=response.get("context"), visit_id=visit_id, **Postdata)
            response.update(result)

        return self._response('doneVisit', response)

    @route('/smart_api/visits', csrf=False, type='http', auth="none", methods=['GET'])
    def getUserVisits(self, **kwargs):
        response = self._authenticate(True, **kwargs)
        if response.get('success'):
            smartapi = request.env['smart_api'].sudo().with_context(response.get("context"))
            result = smartapi.fetch_visits(context=response.get("context"), **kwargs)
            response.update(result)
            # response['message'] = "Visits result."
        return self._response('getUserVisits', response)

    @route('/smart_api/homeData', csrf=False, type='http', auth="none", methods=['GET'])
    def getHomeData(self, **kwargs):
        response = self._authenticate(True, **kwargs)
        if response.get('success'):
            user = response.get('context',{}).get('user').sudo()
            smartapi = request.env['smart_api'].sudo().with_context(response.get("context"))
            smartapi_obj = smartapi.search([], limit=1)
            result = smartapi.dashboard_data_chart(smartapi_obj,user)
            response.update(result)
            response['message'] = "Homepage Data."
        return self._response('homepage', response)

    @route('/smart_api/customers', csrf=False, type='http', auth="none", methods=['GET'])
    def getCustomersData(self, **kwargs):
        response = self._authenticate(True, **kwargs)
        if response.get('success'):
            smartapi = request.env['smart_api'].sudo()
            result = smartapi.fetch_customers(**kwargs)
            response.update(result)
            response['message'] = "Customers result."
        return self._response('search', response)

    @route('/smart_api/createCustomer/', csrf=False, type='http', auth="none", methods=['POST'])
    def createCustomer(self, **kwargs):

        response = self._authenticate(True, **kwargs)
        context = response.get('context')
        if response.get('success'):
            smartapi = request.env['smart_api'].sudo().with_context(response.get("context"))
            Postdata = self._mData or {}
            result = smartapi.create_customer(context=response.get("context"), **Postdata)
            response.update(result)

        return self._response('createCustomer', response)

    @route('/smart_api/updateCustomer/<int:customer_id>', csrf=False, type='http', auth="none", methods=['POST'])
    def updateCustomer(self, customer_id, **kwargs):

        response = self._authenticate(True, **kwargs)
        context = response.get('context')
        if response.get('success'):
            smartapi = request.env['smart_api'].sudo().with_context(response.get("context"))
            Postdata = self._mData or {}
            result = smartapi.update_customer(context=response.get("context"), customer_id=customer_id, **Postdata)
            response.update(result)

        return self._response('updateCustomer', response)

    @route('/smart_api/categories', csrf=False, type='http', auth="none", methods=['GET'])
    def getCategoriesData(self, **kwargs):
        response = self._authenticate(True, **kwargs)
        if response.get('success'):
            smartapi = request.env['smart_api'].sudo()
            result = smartapi.fetch_categories(context=response.get("context"), **kwargs)
            response.update(result)
            response['message'] = "Categories result."
        return self._response('categorie', response)

    @route('/smart_api/products', csrf=False, type='http', auth="none", methods=['GET'])
    def getProductsData(self, **kwargs):
        response = self._authenticate(True, **kwargs)
        if response.get('success'):

            smartapi = request.env['smart_api'].sudo().with_context(response.get("context"))
            result = smartapi.fetch_products(context=response.get("context"), **kwargs)
            response.update(result)
            response['message'] = "Products result."
        return self._response('product', response)

    @route('/smart_api/createOrder', csrf=False, type='http', auth="none", methods=['POST'])
    def placeNewOrder(self, **kwargs):
        response = self._authenticate(True, **kwargs)
        context = response.get('context')
        if response.get('success'):
            smartapi = request.env['smart_api'].sudo().with_context(response.get("context"))
            Postdata = self._mData or {}
            result = smartapi.create_so(context=response.get("context"), **Postdata)
            if 'success' in result and result['success'] == True:
                result['data'] = smartapi.get_order(result['data'])
            response.update(result)
        return self._response('createOrder', response)

    @route('/smart_api/returnInvoice/<int:invoice_id>', csrf=False, type='http', auth="none", methods=['POST'])
    def ReturnOrder(self, invoice_id, **kwargs):
        response = self._authenticate(True, **kwargs)
        context = response.get('context')
        if response.get('success'):
            smartapi = request.env['smart_api'].sudo().with_context(response.get("context"))
            Postdata = self._mData or {}
            result = smartapi.create_reverse(context=response.get("context"),invoice_id=invoice_id, **Postdata)
            if 'success' in result and result['success'] == True:
                result['data'] = smartapi.get_invoice(result['data'])
            response.update(result)
        return self._response('ReturnOrder', response)

    @route('/smart_api/returnCustomerInvoices/<int:customer_id>',csrf=False,type='http',auth="none",methods=['POST'])
    def createMultiReverse(self, customer_id, **kwargs):

        response = self._authenticate(True,**kwargs)
        context = response.get('context')
        listdata = {'invoices': []}
        listinvoices = []
        if response.get('success'):
            smartapi = request.env['smart_api'].sudo().with_context(response.get("context"))
            Postdata = self._mData or {}
            result = smartapi.create_multi_reverse(context=response.get("context"),customer_id=customer_id,**Postdata)
            if 'success' in result and result['success'] == True:
                if 'data' in result:
                    for data in result['data']:
                        listinvoices.append(smartapi.get_invoice(data))
                listdata['invoices'] = listinvoices
                result['data'] = listdata
            response.update(result)

        return self._response('createMultiReverse',response)

    @route('/smart_api/createPayment', csrf=False, type='http', auth="none", methods=['POST'])
    def createPayment(self, **kwargs):

        response = self._authenticate(True, **kwargs)
        context = response.get('context')
        if response.get('success'):
            smartapi = request.env['smart_api'].sudo().with_context(response.get("context"))
            Postdata = self._mData or {}
            result = smartapi.create_payment(context=response.get("context"), **Postdata)
            if 'success' in result and result['success'] == True:
                result['data'] = smartapi.get_invoice(result['data'])
            response.update(result)

        return self._response('createPayment', response)

    @route('/smart_api/createTransferMoney', csrf=False, type='http', auth="none", methods=['POST'])
    def createTransferMoney(self, **kwargs):

        response = self._authenticate(True, **kwargs)
        context = response.get('context')
        if response.get('success'):
            smartapi = request.env['smart_api'].sudo().with_context(response.get("context"))
            Postdata = self._mData or {}
            result = smartapi.create_transfer_money(context=response.get("context"), **Postdata)
            if 'success' not in result or result['success'] != True:
                result['data'] = {}

            response.update(result)

        return self._response('createTransferMoney', response)



    @route('/smart_api/createMultiPayment', csrf=False, type='http', auth="none", methods=['POST'])
    def createMultiPayment(self, **kwargs):

        response = self._authenticate(True, **kwargs)
        context = response.get('context')
        listdata = {'invoices' : []}
        listinvoices = []
        if response.get('success'):
            smartapi = request.env['smart_api'].sudo().with_context(response.get("context"))
            Postdata = self._mData or {}
            result = smartapi.create_multi_payment(context=response.get("context"), **Postdata)
            if 'success' in result and result['success'] == True:
                if 'data' in result:
                    for data in result['data']:
                        listinvoices.append(smartapi.get_invoice(data))
                listdata['invoices'] = listinvoices
                result['data'] = listdata
            response.update(result)

        return self._response('createPayment', response)

    @route('/smart_api/order/<int:order_id>', csrf=False, type='http', auth="none", methods=['GET'])
    def getOrder(self, order_id, **kwargs):
        response = self._authenticate(True, **kwargs)
        if response.get('success'):
            if order_id:
                result = {}
                smartapi = request.env['smart_api'].sudo().with_context(response.get("context"))
                result['data'] = smartapi.get_order(order_id)
                result['message'] = "Order details."
            else:
                result = {'success': False, 'message': 'Order not found !!!'}
            response.update(result)
        return self._response('order', response)

    @route('/smart_api/orders', csrf=False, type='http', auth="none", methods=['GET'])
    def getOrders(self, **kwargs):
        response = self._authenticate(True, **kwargs)
        if response.get('success'):
            smartapi = request.env['smart_api'].sudo().with_context(response.get("context"))
            result = smartapi.fetch_orders(context=response.get("context"), **kwargs)
            response.update(result)
            response['message'] = "Orders result."
        return self._response('orders', response)

    @route('/smart_api/returnableinvoices', csrf=False, type='http', auth="none", methods=['GET'])
    def getToReturnInvoices(self, **kwargs):
        response = self._authenticate(True, **kwargs)
        if response.get('success'):
            smartapi = request.env['smart_api'].sudo().with_context(response.get("context"))
            result = smartapi.fetch_toreturninvoices(context=response.get("context"), **kwargs)
            response.update(result)
        return self._response('invoices', response)


    @route('/smart_api/dueinvoices', csrf=False, type='http', auth="none", methods=['GET'])
    def getDueInvoices(self, **kwargs):
        response = self._authenticate(True, **kwargs)
        if response.get('success'):
            smartapi = request.env['smart_api'].sudo().with_context(response.get("context"))
            result = smartapi.fetch_dueinvoices(context=response.get("context"), **kwargs)
            response.update(result)
            response['message'] = "Due Invoices result."
        return self._response('invoices', response)

    @route('/smart_api/journalitems', csrf=False, type='http', auth="none", methods=['GET'])
    def getJournalItems(self, **kwargs):
        response = self._authenticate(True, **kwargs)
        if response.get('success'):
            smartapi = request.env['smart_api'].sudo().with_context(response.get("context"))
            result = smartapi.fetch_journalentries(context=response.get("context"), **kwargs)
            response.update(result)
            response['message'] = "Journal Items result."
        return self._response('journalitems', response)


    @route('/smart_api/paymentTerm', csrf=False, type='http', auth="none", methods=['GET'])
    def getpaymentTerm(self, **kwargs):
        response = self._authenticate(True, **kwargs)
        if response.get('success'):
            smartapi = request.env['smart_api'].sudo().with_context(response.get("context"))
            result = smartapi.fetch_paymentTerms(context=response.get("context"), **kwargs)
            response.update(result)
            response['message'] = "Payment Terms result."
        return self._response('Payment Term', response)

    @route('/smart_api/visitOptions', csrf=False, type='http', auth="none", methods=['GET'])
    def visitPurposes(self, **kwargs):
        response = self._authenticate(True, **kwargs)
        if response.get('success'):
            smartapi = request.env['smart_api'].sudo().with_context(response.get("context"))
            result = smartapi.get_visitPurposes()
            response.update(result)
            response['message'] = "Visit Purposes result."
        return self._response('visitPurposes', response)

    @route('/smart_api/paymentMethod', csrf=False, type='http', auth="none", methods=['GET'])
    def getpaymentMethod(self, **kwargs):
        response = self._authenticate(True, **kwargs)
        if response.get('success'):
            smartapi = request.env['smart_api'].sudo().with_context(response.get("context"))
            result = smartapi.fetch_paymentMethods(context=response.get("context"), **kwargs)
            response.update(result)
            response['message'] = "Payment Methods result."
        return self._response('Payment Method', response)

    @route('/smart_api/priceList', csrf=False, type='http', auth="none", methods=['GET'])
    def getpriceList(self, **kwargs):
        response = self._authenticate(True, **kwargs)
        if response.get('success'):
            smartapi = request.env['smart_api'].sudo().with_context(response.get("context"))
            result = smartapi.fetch_priceLists(context=response.get("context"), **kwargs)
            response.update(result)
            response['message'] = "Price lists result."
        return self._response('Price lists', response)

    @route('/smart_api/currencyList', csrf=False, type='http', auth="none", methods=['GET'])
    def getcurrencyList(self, **kwargs):
        response = self._authenticate(True, **kwargs)
        if response.get('success'):
            smartapi = request.env['smart_api'].sudo().with_context(response.get("context"))
            result = smartapi.fetch_currencies(context=response.get("context"), **kwargs)
            response.update(result)
            response['message'] = "currency lists result."
        return self._response('Currency lists', response)

    @route('/smart_api/countries', csrf=False, type='http', auth="none", methods=['GET'])
    def getCountriesList(self, **kwargs):
        response = self._authenticate(True, **kwargs)
        if response.get('success'):
            smartapi = request.env['smart_api'].sudo().with_context(response.get("context"))
            result = smartapi.fetch_countries(context=response.get("context"), **kwargs)
            response.update(result)
            response['message'] = "Countries lists result."
        return self._response('Countries lists', response)