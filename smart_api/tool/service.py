
from functools import wraps
from ast import literal_eval
from base64 import b64decode
import json
import xml.etree.ElementTree as ET
import werkzeug
from odoo.http import request, Controller, route
import logging
_logger = logging.getLogger(__name__)


class xml(object):

    @staticmethod
    def _encode_content(data):
        # .replace('&', '&amp;')
        return data.replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

    @classmethod
    def dumps(cls, apiName, obj):
        _logger.warning("%r : %r" % (apiName, obj))
        if isinstance(obj, dict):
            return "".join("<%s>%s</%s>" % (key, cls.dumps(apiName, obj[key]), key) for key in obj)
        elif isinstance(obj, list):
            return "".join("<%s>%s</%s>" % ("I%s" % index, cls.dumps(apiName, element), "I%s" % index) for index, element in enumerate(obj))
        else:
            return "%s" % (xml._encode_content(obj.__str__()))

    @staticmethod
    def loads(string):
        def _node_to_dict(node):
            if node.text:
                return node.text
            else:
                return {child.tag: _node_to_dict(child) for child in node}
        root = ET.fromstring(string)
        return {root.tag: _node_to_dict(root)}


class WebServices(Controller):

    def __decorateMe(func):
        @wraps(func)
        def wrapped(inst, *args, **kwargs):
            inst._mData = request.httprequest.data and json.loads(
                request.httprequest.data) or {}
            # inst._mData = {"login" : 'admin'}
            inst._mAuth = request.httprequest.authorization and (request.httprequest.authorization.get(
                'password') or request.httprequest.authorization.get("username")) or None
            inst.base_url = request.httprequest.headers.get("base_url")
            inst._lcred = {}
            inst._sLogin = False
            inst.auth = True
            inst._mLang = request.httprequest.headers.get("lang") or 'ar_001'
            inst._mPricelist = request.httprequest.headers.get("pricelist") or None
            if request.httprequest.headers.get("Login"):
                try:
                    inst._lcred = literal_eval((request.httprequest.headers["Login"]))
                    # inst._lcred = literal_eval(
                    #     b64decode(request.httprequest.headers["Login"]).decode('utf-8'))
                except:
                    inst._lcred = {"email": None, "password": None}
            elif request.httprequest.headers.get("SocialLogin"):
                inst._sLogin = True
                try:
                    inst._lcred = literal_eval(
                        b64decode(request.httprequest.headers["SocialLogin"]).decode('utf-8'))
                except:
                    inst._lcred = {"authProvider": 1, "authUserId": 1234567890}
            else:
                inst.auth = False
            return func(inst, *args, **kwargs)
        return wrapped

    def _available_api(self):
        API = {
            'login': {
                'description': '',
                'uri': '/smart_api/user/login',
                'request': ['POST'],
            },

            'signOut': {
                'description': '',
                'uri': '/smart_api/user/signOut',
                'request': ['POST'],
            },

            'resetPassword': {
                'description': '',
                'uri': '/smart_api/user/resetPassword',
                'request': ['POST'],
                'body': {
                    "login": "rashad.ali.ye@gmail.com",
                }
            },
        }
        return API

    def _wrap2xml(self, apiName, data):
        resp_xml = "<?xml version='1.0' encoding='UTF-8'?>"
        resp_xml += '<odoo xmlns:xlink="http://www.w3.org/1999/xlink">'
        resp_xml += "<%s>" % apiName
        resp_xml += xml.dumps(apiName, data)
        resp_xml += "</%s>" % apiName
        resp_xml += '</odoo>'
        return resp_xml

    def _response(self, apiName, response, ctype='json'):
        if response.get("context"):
            response.pop("context")
        if 'local' in response:
            response.pop("local")
        if ctype == 'json':
            mime = 'application/json; charset=utf-8'
            body = json.dumps(response)
        else:
            mime = 'text/xml'
            body = self._wrap2xml(apiName, response)
        headers = [
            ('Content-Type', mime),
            ('Content-Length', len(body))
        ]
        return werkzeug.wrappers.Response(body, headers=headers)

    @__decorateMe
    def _authenticate(self, auth, **kwargs):
        if 'api_key' in kwargs:
            api_key = kwargs.get('api_key')
        elif request.httprequest.authorization:
            api_key = request.httprequest.authorization.get(
                'password') or request.httprequest.authorization.get("username")
        else:
            api_key = False
        smartAPI = request.env['smart_api'].sudo().search([], limit=1)
        payload = {"lang": self._mLang, "base_url": self.base_url,
                   "pricelist": self._mPricelist, "smart_api_obj": smartAPI}
        response = smartAPI._validate(api_key, payload)
        if not response.get('success'):
            return response
        context = response.get("context")
        request.context = dict(context)
        smartAPI = context['smart_api_obj']
        if auth:
            result = smartAPI.authenticate(self._lcred, kwargs.get(
                'detailed', False), self._sLogin, context=context)
            response.update(result)
        return response

    def _tokenUpdate(self, user_id=False):

        FcmRegister = request.env['fcm.registered.devices'].sudo()
        already_registered = FcmRegister.search(
            [('device_id', '=', self._mData.get("fcmDeviceId"))])
        if already_registered:
            already_registered.write(
                {'token': self._mData.get("fcmToken"), 'user_id': user_id})
        else:
            FcmRegister.create({
                'token': self._mData.get("fcmToken", ""),
                'device_id': self._mData.get("fcmDeviceId", ""),
                'description': "%r" % self._mData,
                'user_id': user_id,
            })
        return True

    @route('/smart_api/', csrf=False, type='http', auth="none")
    def index(self, **kwargs):

        response = self._authenticate(False, **kwargs)
        if response.get('success'):
            data = self._available_api()
            return self._response('smart_api', data, 'xml')
        else:
            headers = [
                ('WWW-Authenticate', 'Basic realm="Welcome to Odoo Webservice, please enter the authentication key as the login. No password required."')]
            return werkzeug.wrappers.Response('401 Unauthorized %r' % request.httprequest.authorization, status=401, headers=headers)

    def _languageData(self, smart_api):
        temp = {
            'defaultLanguage': (smart_api.default_lang.code, smart_api.default_lang.name),
            'allLanguages': [(id.code, id.name) for id in smart_api.language_ids],
        }
        return temp



